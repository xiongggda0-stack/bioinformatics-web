from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.pipeline import Pipeline


def seed_pipeline(db_session: Session) -> None:
    db_session.add(
        Pipeline(
            title="Bulk RNA-seq 分析",
            description="从 FASTQ 到差异表达结果。",
            omics_type="RNA-Seq",
            category_key="basic",
            category_name="基础分析",
            dag_json={"nodes": []},
            metadata_json={},
            content="# RNA-seq",
        )
    )
    db_session.commit()


def test_search_api_returns_ranked_items(
    client: TestClient, db_session: Session
) -> None:
    seed_pipeline(db_session)

    response = client.get("/api/search?q=RNA-seq")

    assert response.status_code == 200
    assert response.json()["query"] == "RNA-seq"
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["type"] == "pipeline"


def test_search_api_rejects_short_keyword(client: TestClient) -> None:
    response = client.get("/api/search?q=a")

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "message": "搜索关键词至少需要 2 个字符",
        "data": None,
    }


def test_search_api_returns_empty_result_for_missing_keyword(client: TestClient) -> None:
    response = client.get("/api/search?q=missing-keyword")

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []
