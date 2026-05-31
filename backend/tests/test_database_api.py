from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial


def seed_resource(db_session: Session) -> None:
    resource = DatabaseResource(
        slug="geo",
        name="GEO",
        full_name="Gene Expression Omnibus",
        category_key="expression",
        category_name="转录组表达",
        description="公共表达矩阵和测序项目入口。",
        use_cases_json=["查找表达矩阵"],
        data_types_json=["Expression", "RNA-seq"],
        species_json=["Human", "Mouse"],
        tags_json=["Public Data"],
        url="https://www.ncbi.nlm.nih.gov/geo/",
        region="USA",
        rating=5,
    )
    resource.tutorials.append(
        DatabaseTutorial(
            slug="geo-expression-search",
            title="GEO 表达数据检索",
            scenario="查找公开表达矩阵。",
            steps_json=["搜索关键词", "筛选项目"],
            example_query="RNA-seq",
            entry_url="https://www.ncbi.nlm.nih.gov/geo/",
            content="# GEO 教程",
        )
    )
    db_session.add(resource)
    db_session.commit()


def test_list_databases_returns_resources(
    client: TestClient, db_session: Session
) -> None:
    seed_resource(db_session)

    response = client.get("/api/databases")

    assert response.status_code == 200
    assert response.json()[0]["slug"] == "geo"
    assert response.json()[0]["tutorials"][0]["slug"] == "geo-expression-search"


def test_list_databases_filters_keyword_and_category(
    client: TestClient, db_session: Session
) -> None:
    seed_resource(db_session)

    response = client.get("/api/databases?keyword=GEO&category_key=expression")

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["geo"]


def test_get_database_tutorial_returns_resource_context(
    client: TestClient, db_session: Session
) -> None:
    seed_resource(db_session)

    response = client.get("/api/databases/tutorials/geo-expression-search")

    assert response.status_code == 200
    assert response.json()["resource"]["slug"] == "geo"
    assert response.json()["slug"] == "geo-expression-search"


def test_missing_database_tutorial_returns_standard_error(client: TestClient) -> None:
    response = client.get("/api/databases/tutorials/missing-slug")

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "数据库教程不存在",
        "data": None,
    }
