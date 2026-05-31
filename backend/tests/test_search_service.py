from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm
from app.models.pipeline import Pipeline
from app.services.search_service import SearchService


def build_pipeline(
    title: str,
    description: str = "普通简介",
    content: str = "普通正文",
    category_name: str = "基础分析",
) -> Pipeline:
    return Pipeline(
        title=title,
        description=description,
        omics_type="Other",
        category_key="basic",
        category_name=category_name,
        dag_json={"nodes": []},
        metadata_json={},
        content=content,
    )


def build_algorithm(name: str) -> Algorithm:
    return Algorithm(
        name=name,
        category="Alignment",
        category_key="alignment",
        category_name="序列比对",
        tool_type="software",
        summary="普通简介",
        performance_json={},
        markdown_docs="普通正文",
    )


def test_search_scores_title_matches_before_summary_and_markdown(
    db_session: Session,
) -> None:
    db_session.add_all(
        [
            build_pipeline("RNA-seq"),
            build_pipeline("Bulk RNA-seq 分析"),
            build_pipeline("表达分析", description="适用于 RNA-seq 项目"),
            build_pipeline("转录组流程", content="正文提到 RNA-seq"),
        ]
    )
    db_session.commit()

    response = SearchService(db_session).search(query="RNA-seq")

    assert [item.score for item in response.items] == [100, 70, 20, 10]


def test_search_filters_resource_type(db_session: Session) -> None:
    db_session.add(build_pipeline("STAR"))
    db_session.add(build_algorithm("STAR"))
    db_session.commit()

    response = SearchService(db_session).search(query="STAR", resource_type="algorithm")

    assert response.total == 1
    assert response.counts.algorithm == 1
    assert [item.type for item in response.items] == ["algorithm"]


def test_search_uses_stable_type_priority_for_equal_scores(db_session: Session) -> None:
    db_session.add(build_pipeline("STAR"))
    db_session.add(build_algorithm("STAR"))
    db_session.commit()

    response = SearchService(db_session).search(query="STAR")

    assert [item.type for item in response.items] == ["pipeline", "algorithm"]
