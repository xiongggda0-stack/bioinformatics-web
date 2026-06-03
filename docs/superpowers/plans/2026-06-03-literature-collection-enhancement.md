# 文献集数据扩展 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为文献集模块新增 PubMed 批量导入和 DOI 单篇导入能力，导入时自动匹配已有 Pipeline/Algorithm，并将种子文献从 3 篇扩展到 10 篇。

**Architecture:** 新增 LiteratureImporter（拉取 PubMed/CrossRef 数据）和 LiteratureMatcher（自动关联 Pipeline/Algorithm），通过两个新 POST 端点和扩展现有 seed 脚本完成。导入为同步操作，PMID 上限 50 篇。

**Tech Stack:** FastAPI 0.115.6, SQLAlchemy 2.0.36, lxml 5.3.0, NCBI E-utilities API, CrossRef REST API

---

### Task 1: 添加 lxml 依赖

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: 在 requirements 末尾添加 lxml**

`backend/requirements.txt` 追加：

```
lxml==5.3.0
```

- [ ] **Step 2: 安装依赖并验证**

Run: `cd backend && pip install lxml==5.3.0`
Expected: Successfully installed lxml-5.3.0

- [ ] **Step 3: 验证导入**

Run: `python -c "from lxml import etree; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add lxml for PubMed XML parsing"
```

---

### Task 2: 创建导入相关的 Pydantic Schema

**Files:**
- Create: `backend/app/schemas/literature_import.py`
- Modify: `backend/app/schemas/__init__.py`

- [ ] **Step 1: 创建 literature_import.py schema 文件**

```python
"""Schemas for literature import endpoints."""

from pydantic import BaseModel, Field


class PubmedImportRequest(BaseModel):
    pmids: list[str] = Field(..., min_length=1, max_length=50)
    auto_match: bool = True


class DoiImportRequest(BaseModel):
    doi: str = Field(..., min_length=5, max_length=200)
    pipeline_id: int | None = None
    algorithm_id: int | None = None
    auto_match: bool = True


class ImportDetail(BaseModel):
    identifier: str  # PMID or DOI
    title: str | None = None
    status: str  # "imported" | "skipped" | "failed"
    matched_to: str | None = None
    error: str | None = None


class ImportReport(BaseModel):
    imported: int = 0
    skipped: int = 0
    failed: int = 0
    matched: int = 0
    details: list[ImportDetail]
```

- [ ] **Step 2: 更新 `__init__.py` 导出**

在 `backend/app/schemas/__init__.py` 末尾追加：

```python
from app.schemas.literature_import import (
    DoiImportRequest,
    ImportDetail,
    ImportReport,
    PubmedImportRequest,
)

__all__ += [
    "DoiImportRequest",
    "ImportDetail",
    "ImportReport",
    "PubmedImportRequest",
]
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas/literature_import.py backend/app/schemas/__init__.py
git commit -m "feat: add literature import request/response schemas"
```

---

### Task 3: 创建 LiteratureMatcher 自动匹配引擎

**Files:**
- Create: `backend/app/services/literature_matcher.py`

- [ ] **Step 1: 编写匹配引擎**

```python
"""Auto-matching engine for literature ↔ Pipeline / Algorithm associations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm
from app.models.pipeline import Pipeline


# Level-2 keyword mapping: canonical term → (pipeline_title_or_None, algorithm_name_or_None)
_KEYWORD_MAP: dict[str, tuple[str | None, str | None]] = {
    "bwa": (None, "BWA-MEM"),
    "burrows-wheeler": (None, "BWA-MEM"),
    "seurat": (None, "Seurat v5"),
    "cell ranger": (None, "Cell Ranger"),
    "cellranger": (None, "Cell Ranger"),
    "wgs": ("WGS 变异检测流程", None),
    "whole genome sequencing": ("WGS 变异检测流程", None),
    "scrna": ("10x 单细胞基础降维聚类", None),
    "single cell rna": ("10x 单细胞基础降维聚类", None),
    "single-cell rna": ("10x 单细胞基础降维聚类", None),
    "star align": (None, "STAR"),
    "featurecounts": (None, "featureCounts"),
    "wgcna": (None, "WGCNA"),
    "des": (None, "DESeq2"),
    "deseq2": (None, "DESeq2"),
    "cut&tag": ("CUT&Tag 分析流程", None),
    "cut and tag": ("CUT&Tag 分析流程", None),
}


class LiteratureMatcher:
    """Match imported literature against existing Pipeline / Algorithm records.

    Matching is best-effort — unmatched associations remain ``NULL``.
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._pipelines: dict[str, int] | None = None
        self._algorithms: dict[str, int] | None = None

    def _load_indexes(self) -> None:
        if self._pipelines is not None:
            return
        pipelines = self._db.scalars(select(Pipeline)).all()
        algorithms = self._db.scalars(select(Algorithm)).all()
        self._pipelines = {p.title.lower(): p.id for p in pipelines}
        self._algorithms = {a.name.lower(): a.id for a in algorithms}

    def match(
        self,
        title: str,
        abstract: str,
        manual_pipeline_id: int | None = None,
        manual_algorithm_id: int | None = None,
    ) -> tuple[int | None, int | None, str | None]:
        """Return ``(pipeline_id, algorithm_id, matched_label)``.

        *Manual assignments take precedence over auto-matching.*
        """
        self._load_indexes()

        # Manual assignments win
        if manual_pipeline_id is not None or manual_algorithm_id is not None:
            label_parts: list[str] = []
            if manual_pipeline_id is not None:
                # resolve name for report
                for name, pid in (self._pipelines or {}).items():
                    if pid == manual_pipeline_id:
                        label_parts.append(name)
                        break
            if manual_algorithm_id is not None:
                for name, aid in (self._algorithms or {}).items():
                    if aid == manual_algorithm_id:
                        label_parts.append(name)
                        break
            return (
                manual_pipeline_id,
                manual_algorithm_id,
                " + ".join(label_parts) if label_parts else None,
            )

        combined = f"{title.lower()} {abstract.lower()}"

        # Level 1: exact title/name in text
        assert self._pipelines is not None and self._algorithms is not None
        for pipe_title, pipe_id in self._pipelines.items():
            if pipe_title in combined:
                return (pipe_id, None, pipe_title)

        for algo_name, algo_id in self._algorithms.items():
            if algo_name in combined:
                return (None, algo_id, algo_name)

        # Level 2: keyword mapping
        for keyword, (pipe_target, algo_target) in _KEYWORD_MAP.items():
            if keyword in combined:
                pid = self._pipelines.get(pipe_target.lower()) if pipe_target else None
                aid = self._algorithms.get(algo_target.lower()) if algo_target else None
                if pid is not None or aid is not None:
                    return (pid, aid, f"{pipe_target or ''} {algo_target or ''}".strip())

        return (None, None, None)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/literature_matcher.py
git commit -m "feat: add LiteratureMatcher auto-association engine"
```

---

### Task 4: 创建 LiteratureImporter 数据导入器

**Files:**
- Create: `backend/app/services/literature_importer.py`

- [ ] **Step 1: 编写导入器**

```python
"""PubMed and CrossRef literature import service.

Calls NCBI E-utilities for PubMed records and CrossRef REST API for DOI
lookups.  Imported records are de-duplicated by DOI.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree
from urllib.parse import quote

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
            # The root may BE the Article element in some responses
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
                identifier=doi, status="failed", error="Unable to parse CrossRef response"
            )

        return self._persist(record, auto_match, pipeline_id, algorithm_id)

    @staticmethod
    def _parse_crossref_json(data: dict[str, Any], identifier: str) -> _ParsedRecord | None:
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/literature_importer.py
git commit -m "feat: add LiteratureImporter for PubMed/CrossRef data ingestion"
```

---

### Task 5: 创建导入 Controller 并注册路由

**Files:**
- Create: `backend/app/api/v1/controllers/literature_import_controller.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建导入 controller**

```python
"""Literature import endpoints — PubMed batch + DOI single import."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.literature_import import (
    DoiImportRequest,
    ImportReport,
    PubmedImportRequest,
)
from app.services.literature_importer import LiteratureImporter

router = APIRouter(prefix="/api/literatures/import", tags=["Literature Import"])


def _build_report(details: list) -> ImportReport:
    return ImportReport(
        imported=sum(1 for d in details if d.status == "imported"),
        skipped=sum(1 for d in details if d.status == "skipped"),
        failed=sum(1 for d in details if d.status == "failed"),
        matched=sum(1 for d in details if d.matched_to is not None),
        details=details,
    )


@router.post(
    "/pubmed",
    response_model=ApiResponse[ImportReport],
    summary="PubMed 批量导入",
)
def import_from_pubmed(
    body: PubmedImportRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[ImportReport]:
    importer = LiteratureImporter(db)
    details = importer.import_from_pubmed(
        pmids=body.pmids,
        auto_match=body.auto_match,
    )
    report = _build_report(details)
    return ApiResponse(code=200, message="导入完成", data=report)


@router.post(
    "/doi",
    response_model=ApiResponse[ImportReport],
    summary="DOI 单篇导入",
)
def import_from_doi(
    body: DoiImportRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[ImportReport]:
    importer = LiteratureImporter(db)
    detail = importer.import_from_doi(
        doi=body.doi,
        pipeline_id=body.pipeline_id,
        algorithm_id=body.algorithm_id,
        auto_match=body.auto_match,
    )
    report = _build_report([detail])
    return ApiResponse(code=200, message="导入完成", data=report)
```

- [ ] **Step 2: 在 main.py 中注册 router**

在 `backend/app/main.py` 的 import 区域追加：

```python
from app.api.v1.controllers.literature_import_controller import router as literature_import_router
```

在 `register_exception_handlers(app)` 之后、`app.include_router(health_router)` 之前追加：

```python
    app.include_router(literature_import_router)
```

确认最终 import 区和 router 注册区如下（示意，只展示新增行）：

```python
# ... existing imports ...
from app.api.v1.controllers.literature_import_controller import router as literature_import_router

# Inside create_app():
# ...
    register_exception_handlers(app)
    app.include_router(literature_import_router)
    app.include_router(health_router)
    # ... rest unchanged ...
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/controllers/literature_import_controller.py backend/app/main.py
git commit -m "feat: add POST /api/literatures/import/pubmed and /doi endpoints"
```

---

### Task 6: 编写导入功能的测试

**Files:**
- Create: `backend/tests/test_literature_import.py`

- [ ] **Step 1: 编写测试文件**

```python
"""Tests for literature import endpoints and matcher."""

from unittest.mock import MagicMock, patch

from app.models.algorithm import Algorithm
from app.models.literature import Literature
from app.models.pipeline import Pipeline
from app.schemas.literature_import import ImportDetail
from app.services.literature_importer import LiteratureImporter
from app.services.literature_matcher import LiteratureMatcher


# ── LiteratureMatcher tests ────────────────────────────────────────────

class TestLiteratureMatcher:
    def test_exact_title_match_in_title(self, db_session):
        """标题包含 pipeline 名称时应精确匹配."""
        p = Pipeline(
            title="WGS 变异检测流程",
            description="test",
            omics_type="WGS",
            category_key="wgs",
            category_name="WGS",
            dag_json={},
            content="test",
        )
        db_session.add(p)
        db_session.commit()

        matcher = LiteratureMatcher(db_session)
        pid, aid, label = matcher.match(
            title="WGS 变异检测流程 benchmarking study",
            abstract="",
        )
        assert pid == p.id
        assert aid is None
        assert label is not None

    def test_keyword_match_bwa(self, db_session):
        """关键词 'bwa' 应映射到 BWA-MEM."""
        a = Algorithm(
            name="BWA-MEM",
            category="alignment",
            category_key="alignment",
            category_name="比对工具",
            tool_type="命令行软件",
            summary="test",
            performance_json={},
            markdown_docs="test",
        )
        db_session.add(a)
        db_session.commit()

        matcher = LiteratureMatcher(db_session)
        pid, aid, label = matcher.match(
            title="Some BWA benchmarking",
            abstract="",
        )
        assert aid == a.id
        assert "BWA-MEM" in (label or "")

    def test_no_match_returns_none(self, db_session):
        """无匹配时返回 None."""
        matcher = LiteratureMatcher(db_session)
        pid, aid, label = matcher.match(
            title="Completely unrelated paper title",
            abstract="nothing here",
        )
        assert pid is None
        assert aid is None
        assert label is None

    def test_manual_override_takes_precedence(self, db_session):
        """手动指定的 ID 优先于自动匹配."""
        p1 = Pipeline(
            title="RNA-seq 流程",
            description="test",
            omics_type="RNA-Seq",
            category_key="rnaseq",
            category_name="RNA-Seq",
            dag_json={},
            content="test",
        )
        p2 = Pipeline(
            title="WGS 变异检测流程",
            description="test",
            omics_type="WGS",
            category_key="wgs",
            category_name="WGS",
            dag_json={},
            content="test",
        )
        db_session.add_all([p1, p2])
        db_session.commit()

        matcher = LiteratureMatcher(db_session)
        pid, aid, label = matcher.match(
            title="RNA-seq analysis methods",
            abstract="",
            manual_pipeline_id=p2.id,
        )
        # 手动指定 p2，即使标题更匹配 p1
        assert pid == p2.id


# ── LiteratureImporter persistence tests ───────────────────────────────

class TestLiteratureImporterPersistence:
    """Test de-dup and manual assignment logic (no network)."""

    def test_skip_duplicate_doi(self, db_session):
        """重复 DOI 应返回 skipped."""
        existing = Literature(
            title="Existing paper",
            authors=["A Author"],
            journal="Test",
            publication_year=2020,
            doi="10.1234/test.1",
            abstract_text="abstract",
        )
        db_session.add(existing)
        db_session.commit()

        importer = LiteratureImporter(db_session)
        detail = importer._persist(
            importer._ParsedRecord(
                title="Duplicate paper",
                authors=["B Author"],
                journal="J2",
                publication_year=2021,
                doi="10.1234/test.1",
                abstract_text="abs",
                identifier="10.1234/test.1",
            ),
            auto_match=False,
        )
        assert detail.status == "skipped"


# ── API endpoint tests ─────────────────────────────────────────────────

class TestImportEndpoints:
    def test_pubmed_import_empty_list_rejected(self, client):
        """空 PMID 列表应返回 422."""
        resp = client.post("/api/literatures/import/pubmed", json={"pmids": []})
        assert resp.status_code == 422

    def test_doi_import_empty_doi_rejected(self, client):
        """空 DOI 应返回 422."""
        resp = client.post("/api/literatures/import/doi", json={"doi": ""})
        assert resp.status_code == 422

    @patch("app.services.literature_importer.requests.get")
    def test_pubmed_import_mocked_api(self, mock_get, client):
        """模拟 PubMed API 返回，验证导入链路."""
        mock_xml = """<?xml version="1.0"?>
        <PubmedArticleSet>
          <PubmedArticle>
            <MedlineCitation>
              <Article>
                <ArticleTitle>Test Paper Title</ArticleTitle>
                <Abstract>
                  <AbstractText>Test abstract content.</AbstractText>
                </Abstract>
                <AuthorList>
                  <Author>
                    <LastName>Smith</LastName>
                    <ForeName>John</ForeName>
                  </Author>
                </AuthorList>
                <Journal>
                  <Title>Test Journal</Title>
                  <JournalIssue>
                    <PubDate><Year>2023</Year></PubDate>
                  </JournalIssue>
                </Journal>
                <ArticleIdList>
                  <ArticleId IdType="doi">10.9999/test.9</ArticleId>
                </ArticleIdList>
              </Article>
            </MedlineCitation>
          </PubmedArticle>
        </PubmedArticleSet>"""

        mock_response = MagicMock()
        mock_response.text = mock_xml
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        resp = client.post(
            "/api/literatures/import/pubmed",
            json={"pmids": ["99999999"], "auto_match": False},
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["data"]["imported"] == 1
        assert payload["data"]["skipped"] == 0
        assert payload["data"]["failed"] == 0

    @patch("app.services.literature_importer.requests.get")
    def test_doi_import_mocked_api(self, mock_get, client):
        """模拟 CrossRef API 返回，验证导入链路."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {
                "title": ["Mock DOI Paper"],
                "abstract": "Mock abstract.",
                "container-title": ["Mock Journal"],
                "published-print": {"date-parts": [[2022]]},
                "author": [{"given": "Jane", "family": "Doe"}],
                "DOI": "10.9999/mock.1",
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        resp = client.post(
            "/api/literatures/import/doi",
            json={"doi": "10.9999/mock.1", "auto_match": False},
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["data"]["imported"] == 1

    @patch("app.services.literature_importer.requests.get")
    def test_pubmed_import_with_auto_match(self, mock_get, client):
        """自动匹配开启时，导入应触发 matcher."""
        # 先创建 Pipeline 供匹配
        import app.core.database as db_mod
        from app.main import create_app
        from sqlalchemy.orm import Session

        # Use the existing test DB to create a pipeline
        # We'll do this via the client's DB session override
        mock_xml = """<?xml version="1.0"?>
        <PubmedArticleSet>
          <PubmedArticle>
            <MedlineCitation>
              <Article>
                <ArticleTitle>BWA-MEM performance evaluation</ArticleTitle>
                <Abstract>
                  <AbstractText>Testing BWA short read alignment.</AbstractText>
                </Abstract>
                <AuthorList>
                  <Author>
                    <LastName>Li</LastName>
                    <ForeName>Heng</ForeName>
                  </Author>
                </AuthorList>
                <Journal>
                  <Title>Bioinformatics</Title>
                  <JournalIssue>
                    <PubDate><Year>2024</Year></PubDate>
                  </JournalIssue>
                </Journal>
                <ArticleIdList>
                  <ArticleId IdType="doi">10.9999/bwa.1</ArticleId>
                </ArticleIdList>
              </Article>
            </MedlineCitation>
          </PubmedArticle>
        </PubmedArticleSet>"""

        mock_response = MagicMock()
        mock_response.text = mock_xml
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        resp = client.post(
            "/api/literatures/import/pubmed",
            json={"pmids": ["88888888"], "auto_match": True},
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["data"]["imported"] == 1
```

- [ ] **Step 2: 运行测试**

Run: `cd backend && python -m pytest tests/test_literature_import.py -v`
Expected: 全部 PASS

- [ ] **Step 3: 确认现有测试不受影响**

Run: `cd backend && python -m pytest -v`
Expected: 全部 PASS（新增 + 原有）

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_literature_import.py
git commit -m "test: add unit tests for literature import and matching"
```

---

### Task 7: 扩展种子数据至 10 篇文献

**Files:**
- Modify: `backend/app/seed_data/literatures.py`

- [ ] **Step 1: 在 `build_mock_literatures` 中追加 7 篇新文献**

在现有的 return 列表（3 篇）末尾，`]` 之前追加以下 7 篇：

```python
        {
            "title": "CUT&Tag for efficient epigenomic profiling of small samples and single cells",
            "authors": [
                "Hatice S. Kaya-Okur",
                "Steven J. Wu",
                "Christine A. Codomo",
                "Erica S. Pledger",
                "Terri D. Bryson",
                "Jorja G. Henikoff",
                "Kami Ahmad",
                "Steven Henikoff",
            ],
            "journal": "Nature Communications",
            "publication_year": 2019,
            "doi": "10.1038/s41467-019-09982-5",
            "abstract_text": (
                "This paper describes CUT&Tag, an enzyme-tethering approach for "
                "highly efficient and sensitive epigenomic profiling from small samples "
                "and single cells. The method uses protein-A-Tn5 transposase fusion "
                "targeted by specific antibodies to perform tagmentation directly on "
                "chromatin in permeabilized cells or nuclei, eliminating the need for "
                "traditional ChIP-seq library preparation steps."
            ),
            "pipeline_id": cutandtag_pipeline_id,
            "algorithm_id": None,
        },
        {
            "title": "Visualization and analysis of gene expression in tissue sections by spatial transcriptomics",
            "authors": [
                "Patrik L. Ståhl",
                "Fredrik Salmén",
                "Sanja Vickovic",
                "Anna Lundmark",
                "José Fernández Navarro",
                "Jens Magnusson",
                "Stefania Giacomello",
                "Michaela Asp",
                "Jakub O. Westholm",
                "Mikael Huss",
                "Annellie Mollbrink",
                "Sten Linnarsson",
                "Simone Codeluppi",
                "Åke Borg",
                "Fredrik Pontén",
                "Paul Igor Costea",
                "Peter Sahlén",
                "Jan Mulder",
                "Olaf Bergmann",
                "Joakim Lundeberg",
                "Jonas Frisén",
            ],
            "journal": "Science",
            "publication_year": 2016,
            "doi": "10.1126/science.aaf2403",
            "abstract_text": (
                "This landmark study introduced spatial transcriptomics, a method that "
                "enables visualization and quantitative analysis of the transcriptome "
                "with spatial resolution in individual tissue sections. By placing tissue "
                "sections on arrayed reverse transcription primers with unique positional "
                "barcodes, the method captures both global gene expression patterns and "
                "the spatial organization of the tissue microenvironment."
            ),
            "pipeline_id": None,
            "algorithm_id": None,
        },
        {
            "title": "ChIP-seq guidelines and practices of the ENCODE and modENCODE consortia",
            "authors": [
                "Stephen G. Landt",
                "Georgi K. Marinov",
                "Anshul Kundaje",
                "Pouya Kheradpour",
                "Florencia Pauli",
                "Serafim Batzoglou",
                "Bradley E. Bernstein",
                "Peter Bickel",
                "James B. Brown",
                "Philip Cayting",
                "Yiwen Chen",
                "Gilberto DeSalvo",
                "Charles Epstein",
                "Katherine I. Fisher-Aylor",
                "Ghia Euskirchen",
                "Mark Gerstein",
                "Jason Gertz",
                "Alexander J. Hartemink",
                "Michael M. Hoffman",
                "Vishwanath R. Iyer",
            ],
            "journal": "Genome Research",
            "publication_year": 2012,
            "doi": "10.1101/gr.136184.111",
            "abstract_text": (
                "This comprehensive paper provides guidelines and best practices for "
                "ChIP-seq experiments as developed by the ENCODE and modENCODE "
                "consortia. It addresses antibody validation, library complexity, "
                "sequencing depth, replication, and data analysis standards that have "
                "become foundational references for the chromatin biology community."
            ),
            "pipeline_id": None,
            "algorithm_id": None,
        },
        {
            "title": "WGCNA: an R package for weighted correlation network analysis",
            "authors": ["Peter Langfelder", "Steve Horvath"],
            "journal": "BMC Bioinformatics",
            "publication_year": 2008,
            "doi": "10.1186/1471-2105-9-559",
            "abstract_text": (
                "This paper presents the WGCNA R package, a comprehensive collection of "
                "functions for performing weighted gene co-expression network analysis. "
                "WGCNA identifies gene modules based on pairwise correlations, relates "
                "modules to external sample traits, and calculates module membership "
                "measures. It has become an essential tool for systems biology and "
                "co-expression network studies."
            ),
            "pipeline_id": None,
            "algorithm_id": wgcna_algorithm_id,
        },
        {
            "title": "STAR: ultrafast universal RNA-seq aligner",
            "authors": [
                "Alexander Dobin",
                "Carrie A. Davis",
                "Felix Schlesinger",
                "Jorg Drenkow",
                "Chris Zaleski",
                "Sonali Jha",
                "Philippe Batut",
                "Mark Chaisson",
                "Thomas R. Gingeras",
            ],
            "journal": "Bioinformatics",
            "publication_year": 2013,
            "doi": "10.1093/bioinformatics/bts635",
            "abstract_text": (
                "This paper introduces STAR (Spliced Transcripts Alignment to a Reference), "
                "an ultrafast RNA-seq aligner that achieves high alignment accuracy by "
                "using uncompressed suffix arrays together with a novel sequential "
                "maximum mappable seed search strategy. STAR can align both short and "
                "long reads at speeds an order of magnitude faster than contemporary "
                "tools while maintaining splice junction discovery capabilities."
            ),
            "pipeline_id": None,
            "algorithm_id": star_algorithm_id,
        },
        {
            "title": "featureCounts: an efficient general purpose program for assigning sequence reads to genomic features",
            "authors": ["Yang Liao", "Gordon K. Smyth", "Wei Shi"],
            "journal": "Bioinformatics",
            "publication_year": 2014,
            "doi": "10.1093/bioinformatics/btt656",
            "abstract_text": (
                "This paper describes featureCounts, a highly efficient general-purpose "
                "read summarization program that counts mapped reads for genomic features "
                "such as genes, exons, promoters, and genomic bins. The method implements "
                "highly efficient chromosome hashing and feature blocking techniques to "
                "achieve read counting speeds substantially faster than existing methods "
                "while maintaining accuracy."
            ),
            "pipeline_id": None,
            "algorithm_id": featurecounts_algorithm_id,
        },
        {
            "title": "clusterProfiler: an R package for comparing biological themes among gene clusters",
            "authors": ["Guangchuang Yu", "Li-Gen Wang", "Yanyan Han", "Qing-Yu He"],
            "journal": "OMICS: A Journal of Integrative Biology",
            "publication_year": 2012,
            "doi": "10.1089/omi.2011.0118",
            "abstract_text": (
                "This paper presents clusterProfiler, an R package that implements methods "
                "for analyzing and visualizing functional profiles of gene clusters. The "
                "package supports over-representation analysis and gene set enrichment "
                "analysis of Gene Ontology and KEGG pathways, providing statistical "
                "analysis and rich visualization for interpreting functional enrichment "
                "results from high-throughput experiments."
            ),
            "pipeline_id": None,
            "algorithm_id": None,
        },
```

- [ ] **Step 2: 更新函数签名和 query 部分**

在 `build_mock_literatures` 的函数签名中追加 3 个参数：

将：
```python
def build_mock_literatures(
    wgs_pipeline_id: int | None,
    scrna_pipeline_id: int | None,
    bwa_algorithm_id: int | None,
    seurat_algorithm_id: int | None,
    cellranger_algorithm_id: int | None,
) -> list[dict[str, Any]]:
```

改为：
```python
def build_mock_literatures(
    wgs_pipeline_id: int | None,
    scrna_pipeline_id: int | None,
    bwa_algorithm_id: int | None,
    seurat_algorithm_id: int | None,
    cellranger_algorithm_id: int | None,
    cutandtag_pipeline_id: int | None = None,
    wgcna_algorithm_id: int | None = None,
    star_algorithm_id: int | None = None,
    featurecounts_algorithm_id: int | None = None,
) -> list[dict[str, Any]]:
```

- [ ] **Step 3: 在 `seed_literatures` 中查询新关联目标**

在 `seed_literatures` 函数内，原 `cellranger_algorithm_id = ...` 行之后追加：

```python
    cutandtag_pipeline_id = db.scalar(
        select(Pipeline.id).where(Pipeline.title == "CUT&Tag 分析流程")
    )
    wgcna_algorithm_id = db.scalar(
        select(Algorithm.id).where(Algorithm.name == "WGCNA")
    )
    star_algorithm_id = db.scalar(
        select(Algorithm.id).where(Algorithm.name == "STAR")
    )
    featurecounts_algorithm_id = db.scalar(
        select(Algorithm.id).where(Algorithm.name == "featureCounts")
    )
```

并在 `build_mock_literatures(...)` 调用中传入新参数：

```python
    for item in build_mock_literatures(
        wgs_pipeline_id,
        scrna_pipeline_id,
        bwa_algorithm_id,
        seurat_algorithm_id,
        cellranger_algorithm_id,
        cutandtag_pipeline_id,
        wgcna_algorithm_id,
        star_algorithm_id,
        featurecounts_algorithm_id,
    ):
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/seed_data/literatures.py
git commit -m "feat: expand seed literature from 3 to 10 papers"
```

---

### Task 8: 端到端验证

**Files:** 无新建

- [ ] **Step 1: 运行全部后端测试**

```bash
cd backend && python -m pytest -v
```
Expected: 全部 PASS

- [ ] **Step 2: 启动后端验证种子数据**

```bash
cd backend && python init_db.py
```
Expected: `Database initialized with pipeline, algorithm, literature, database and tutorial data.`

- [ ] **Step 3: 验证文献列表返回 10 篇**

```bash
curl -s http://localhost:8000/api/literatures | python -c "import sys,json; d=json.load(sys.stdin); print(f'Total literatures: {len(d)}')"
```
Expected: `Total literatures: 10`

- [ ] **Step 4: 验证导入端点可访问（无需网络）**

```bash
curl -s -X POST http://localhost:8000/api/literatures/import/pubmed -H "Content-Type: application/json" -d '{"pmids": []}'
```
Expected: HTTP 422（空列表拒绝）

- [ ] **Step 5: 验证 OpenAPI 文档中新增端点可见**

访问 `http://localhost:8000/docs`，确认 `/api/literatures/import/pubmed` 和 `/api/literatures/import/doi` 出现在 Swagger 文档中。

- [ ] **Step 6: Commit（如有任何 lint 修复）**

```bash
git add -A && git commit -m "chore: final verification fixes"
```

- [ ] **Step 7: 推送到 GitHub**

```bash
git push origin master
```

---
