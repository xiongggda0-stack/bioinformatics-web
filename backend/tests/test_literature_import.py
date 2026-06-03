"""Tests for literature import endpoints and matcher."""

from unittest.mock import MagicMock, patch

from app.models.algorithm import Algorithm
from app.models.literature import Literature
from app.models.pipeline import Pipeline
from app.services.literature_importer import LiteratureImporter
from app.services.literature_matcher import LiteratureMatcher


# -- LiteratureMatcher tests ---------------------------------------------------

class TestLiteratureMatcher:
    def test_exact_title_match_in_title(self, db_session):
        """pipeline title appears in literature title."""
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
        """keyword 'bwa' maps to BWA-MEM."""
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
        """no match returns None."""
        matcher = LiteratureMatcher(db_session)
        pid, aid, label = matcher.match(
            title="Completely unrelated paper title",
            abstract="nothing here",
        )
        assert pid is None
        assert aid is None
        assert label is None

    def test_manual_override_takes_precedence(self, db_session):
        """manual ID overrides auto-match."""
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
        assert pid == p2.id


# -- LiteratureImporter persistence tests --------------------------------------

class TestLiteratureImporterPersistence:
    """de-dup and manual assignment (no network)."""

    def test_skip_duplicate_doi(self, db_session):
        """duplicate DOI returns skipped."""
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
            _ParsedRecord(
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


# -- API endpoint tests --------------------------------------------------------

class TestImportEndpoints:
    def test_pubmed_import_empty_list_rejected(self, client):
        """empty PMID list returns 422."""
        resp = client.post(
            "/api/literatures/import/pubmed", json={"pmids": []}
        )
        assert resp.status_code == 422

    def test_doi_import_empty_doi_rejected(self, client):
        """empty DOI returns 422."""
        resp = client.post(
            "/api/literatures/import/doi", json={"doi": ""}
        )
        assert resp.status_code == 422

    @patch("app.services.literature_importer.requests.get")
    def test_pubmed_import_mocked_api(self, mock_get, client):
        """mock PubMed API response, verify import chain."""
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
        """mock CrossRef API response, verify import chain."""
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
        """auto_match=True triggers matcher."""
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
