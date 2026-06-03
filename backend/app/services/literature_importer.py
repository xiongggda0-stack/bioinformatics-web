"""PubMed and CrossRef literature import service.

Calls NCBI E-utilities for PubMed records and CrossRef REST API for DOI
lookups.  Imported records are de-duplicated by DOI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote
from xml.etree import ElementTree

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.literature import Literature
from app.schemas.literature_import import ImportDetail
from app.services.literature_matcher import LiteratureMatcher

NCBI_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
CROSSREF_WORKS_URL = "https://api.crossref.org/works"
REQUEST_TIMEOUT = 10


@dataclass
class _ParsedRecord:
    title: str
    authors: list[str]
    journal: str
    publication_year: int
    doi: str
    abstract_text: str
    identifier: str  # PMID or DOI


class LiteratureImporter:
    """Pull metadata from PubMed / CrossRef and persist Literature records."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._matcher = LiteratureMatcher(db)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def import_from_pubmed(
        self,
        pmids: list[str],
        auto_match: bool = True,
    ) -> list[ImportDetail]:
        """Import multiple PMIDs; one record per PMID."""
        details: list[ImportDetail] = []
        for pmid in pmids:
            detail = self._import_single_pubmed(pmid, auto_match)
            details.append(detail)
        return details

    def import_from_doi(
        self,
        doi: str,
        pipeline_id: int | None = None,
        algorithm_id: int | None = None,
        auto_match: bool = True,
    ) -> ImportDetail:
        """Import a single DOI."""
        return self._import_single_doi(doi, pipeline_id, algorithm_id, auto_match)

    # ------------------------------------------------------------------
    # PubMed helpers
    # ------------------------------------------------------------------

    def _import_single_pubmed(self, pmid: str, auto_match: bool) -> ImportDetail:
        """Fetch one PMID via NCBI E-utilities and persist."""
        try:
            params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml",
                "rettype": "abstract",
            }
            resp = requests.get(NCBI_EFETCH_URL, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            return ImportDetail(
                identifier=pmid, status="failed", error=str(exc)
            )

        record = self._parse_pubmed_xml(resp.text, pmid)
        if record is None:
            return ImportDetail(
                identifier=pmid, status="failed", error="Unable to parse PubMed XML"
            )

        return self._persist(record, auto_match)

    @staticmethod
    def _parse_pubmed_xml(xml_text: str, pmid: str) -> _ParsedRecord | None:
        """Extract metadata from NCBI E-utilities XML response."""
        root = ElementTree.fromstring(xml_text)
        article = root.find(".//PubmedArticle//Article")
        if article is None:
            article = root.find(".//Article")
        if article is None:
            return None

        title_el = article.find(".//ArticleTitle")
        title = "".join(title_el.itertext()) if title_el is not None else ""

        abstract_el = article.find(".//Abstract/AbstractText")
        abstract = "".join(abstract_el.itertext()) if abstract_el is not None else ""

        journal_el = article.find(".//Journal/Title")
        journal = journal_el.text.strip() if journal_el is not None and journal_el.text else ""

        year_el = article.find(".//Journal/JournalIssue/PubDate/Year")
        year = int(year_el.text) if year_el is not None and year_el.text else 0

        authors: list[str] = []
        for author_el in article.findall(".//AuthorList/Author"):
            last = author_el.findtext("LastName") or ""
            fore = author_el.findtext("ForeName") or ""
            initials = author_el.findtext("Initials") or ""
            name_parts = [p for p in (last, fore, initials) if p]
            if name_parts:
                authors.append(" ".join(name_parts))

        doi_el = article.find(".//ArticleIdList/ArticleId[@IdType='doi']")
        doi = (doi_el.text or "").strip() if doi_el is not None and doi_el.text else ""

        if not title:
            return None

        return _ParsedRecord(
            title=title,
            authors=authors,
            journal=journal,
            publication_year=year,
            doi=doi,
            abstract_text=abstract,
            identifier=pmid,
        )

    # ------------------------------------------------------------------
    # CrossRef (DOI) helpers
    # ------------------------------------------------------------------

    def _import_single_doi(
        self,
        doi: str,
        pipeline_id: int | None,
        algorithm_id: int | None,
        auto_match: bool,
    ) -> ImportDetail:
        """Fetch a single DOI via CrossRef API and persist."""
        try:
            resp = requests.get(
                f"{CROSSREF_WORKS_URL}/{quote(doi, safe='')}",
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
        except Exception as exc:
            return ImportDetail(
                identifier=doi, status="failed", error=str(exc)
            )

        record = self._parse_crossref_json(resp.json(), doi)
        if record is None:
            return ImportDetail(
                identifier=doi, status="failed",
                error="Unable to parse CrossRef response",
            )

        return self._persist(record, auto_match, pipeline_id, algorithm_id)

    @staticmethod
    def _parse_crossref_json(
        data: dict[str, Any], identifier: str
    ) -> _ParsedRecord | None:
        """Extract metadata from CrossRef /works/:doi JSON response."""
        msg = data.get("message")
        if not isinstance(msg, dict):
            return None

        title_list = msg.get("title")
        title = title_list[0] if isinstance(title_list, list) and title_list else ""

        abstract = msg.get("abstract", "")

        container = msg.get("container-title") or []
        journal = container[0] if container else ""

        published = msg.get("published-print") or msg.get("published-online") or {}
        date_parts = published.get("date-parts", [[0]])
        year = int(date_parts[0][0]) if date_parts and date_parts[0] else 0

        authors: list[str] = []
        for a in msg.get("author") or []:
            given = a.get("given", "")
            family = a.get("family", "")
            name = f"{family} {given}".strip()
            if name:
                authors.append(name)

        doi_val = msg.get("DOI", identifier)

        if not title:
            return None

        return _ParsedRecord(
            title=title,
            authors=authors,
            journal=journal,
            publication_year=year,
            doi=doi_val,
            abstract_text=abstract,
            identifier=identifier,
        )

    # ------------------------------------------------------------------
    # Persist & match
    # ------------------------------------------------------------------

    def _persist(
        self,
        record: _ParsedRecord,
        auto_match: bool,
        manual_pipeline_id: int | None = None,
        manual_algorithm_id: int | None = None,
    ) -> ImportDetail:
        """Write one record to DB, de-dup by DOI, optionally run matcher."""
        # De-dup by DOI
        if record.doi:
            existing = self._db.scalar(
                select(Literature).where(Literature.doi == record.doi)
            )
            if existing is not None:
                return ImportDetail(
                    identifier=record.identifier,
                    title=existing.title,
                    status="skipped",
                )

        # Auto-match
        pipeline_id = manual_pipeline_id
        algorithm_id = manual_algorithm_id
        matched_label: str | None = None
        if auto_match:
            pid, aid, label = self._matcher.match(
                title=record.title,
                abstract=record.abstract_text,
                manual_pipeline_id=manual_pipeline_id,
                manual_algorithm_id=manual_algorithm_id,
            )
            if pid is not None:
                pipeline_id = pid
            if aid is not None:
                algorithm_id = aid
            matched_label = label

        literature = Literature(
            title=record.title,
            authors=record.authors,
            journal=record.journal,
            publication_year=record.publication_year,
            doi=record.doi,
            abstract_text=record.abstract_text,
            pipeline_id=pipeline_id,
            algorithm_id=algorithm_id,
        )
        self._db.add(literature)
        self._db.commit()
        self._db.refresh(literature)

        return ImportDetail(
            identifier=record.identifier,
            title=literature.title,
            status="imported",
            matched_to=matched_label,
        )
