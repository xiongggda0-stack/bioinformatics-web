from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm
from app.models.pipeline import Pipeline
from app.schemas.algorithm import AlgorithmBase
from app.seed_data.algorithms import seed_algorithms
from app.seed_data.pipelines import seed_pipelines


def test_pipeline_seed_exposes_public_trust_metadata(db_session: Session) -> None:
    seed_pipelines(db_session)
    pipeline = db_session.scalar(select(Pipeline).limit(1))

    assert pipeline is not None
    assert pipeline.metadata_json["validation_status"] == "文档校验"
    assert pipeline.metadata_json["last_reviewed_at"] == "2026-06-01"
    assert pipeline.metadata_json["applicability"]["species"]
    assert pipeline.metadata_json["applicability"]["data_types"]
    assert pipeline.metadata_json["applicability"]["experiment_types"]
    assert pipeline.metadata_json["disclaimer"]


def test_star_seed_exposes_official_docs_version_and_installation(
    db_session: Session,
) -> None:
    seed_algorithms(db_session)
    star = db_session.scalar(select(Algorithm).where(Algorithm.name == "STAR"))

    assert star is not None
    assert star.metadata_json["validation_status"] == "文档校验"
    assert star.metadata_json["official_docs_url"].startswith("https://")
    assert star.metadata_json["version"]
    assert star.metadata_json["installation"]


def test_all_algorithm_seeds_expose_public_trust_metadata(
    db_session: Session,
) -> None:
    seed_algorithms(db_session)
    algorithms = list(db_session.scalars(select(Algorithm)).all())

    assert algorithms
    for algorithm in algorithms:
        assert algorithm.metadata_json["disclaimer"]
        assert algorithm.metadata_json["last_reviewed_at"] == "2026-06-01"
        assert algorithm.metadata_json["applicability"]["species"]
        assert algorithm.metadata_json["applicability"]["data_types"]
        assert algorithm.metadata_json["applicability"]["experiment_types"]


def test_core_algorithm_versions_expose_reviewed_versions_and_durable_reminder(
    db_session: Session,
) -> None:
    seed_algorithms(db_session)
    algorithms = {
        algorithm.name: algorithm
        for algorithm in db_session.scalars(select(Algorithm)).all()
    }
    expected_versions = {
        "STAR": "2.7.11b",
        "Salmon": "1.11.4",
        "featureCounts": "Subread 2.1.1",
        "DESeq2": "1.52.0",
        "Cell Ranger": "10.0.0",
        "Seurat v5": "5.5.0",
    }

    for name, expected_version in expected_versions.items():
        version = algorithms[name].metadata_json["version"]
        assert version
        assert expected_version in version
        assert "执行前请以官方稳定版为准" in version


def test_algorithm_metadata_json_has_database_server_default() -> None:
    server_default = Algorithm.__table__.c.metadata_json.server_default

    assert server_default is not None
    assert str(server_default.arg) == "'{}'"


def test_algorithm_schema_serializes_metadata_json() -> None:
    payload = {
        "name": "STAR",
        "category": "Alignment",
        "category_key": "alignment",
        "category_name": "序列比对",
        "tool_type": "命令行软件",
        "summary": "RNA-seq splice-aware aligner",
        "performance_json": {},
        "metadata_json": {"validation_status": "文档校验"},
        "markdown_docs": "# STAR",
    }

    assert AlgorithmBase(**payload).model_dump()["metadata_json"] == {
        "validation_status": "文档校验"
    }


def test_algorithm_seed_upsert_restores_metadata_json(db_session: Session) -> None:
    seed_algorithms(db_session)
    star = db_session.scalar(select(Algorithm).where(Algorithm.name == "STAR"))
    assert star is not None

    star.metadata_json = {}
    db_session.commit()

    seed_algorithms(db_session)

    assert star.metadata_json["official_docs_url"].startswith("https://")
    assert star.metadata_json["last_reviewed_at"] == "2026-06-01"


def test_algorithm_seed_is_idempotent(db_session: Session) -> None:
    seed_algorithms(db_session)
    algorithm_count = len(list(db_session.scalars(select(Algorithm)).all()))

    seed_algorithms(db_session)

    assert len(list(db_session.scalars(select(Algorithm)).all())) == algorithm_count
