from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial


def build_resource() -> DatabaseResource:
    return DatabaseResource(
        slug="ncbi",
        name="NCBI",
        full_name="National Center for Biotechnology Information",
        category_key="portal",
        category_name="综合门户",
        description="常用生物信息学综合入口。",
        use_cases_json=["查基因", "下载公共数据"],
        data_types_json=["Genome", "Literature"],
        species_json=["All"],
        tags_json=["Public Data", "API"],
        url="https://www.ncbi.nlm.nih.gov/",
        api_url="https://www.ncbi.nlm.nih.gov/books/NBK25501/",
        region="USA",
        rating=5,
    )


def test_database_resource_persists_json_fields(db_session: Session) -> None:
    resource = build_resource()
    db_session.add(resource)
    db_session.commit()

    saved = db_session.scalar(
        select(DatabaseResource).where(DatabaseResource.slug == "ncbi")
    )

    assert saved is not None
    assert saved.use_cases_json == ["查基因", "下载公共数据"]
    assert saved.tags_json == ["Public Data", "API"]


def test_database_tutorial_belongs_to_resource(db_session: Session) -> None:
    resource = build_resource()
    resource.tutorials.append(
        DatabaseTutorial(
            slug="sra-fastq-download",
            title="SRA FASTQ 下载教程",
            scenario="从 SRA 下载 FASTQ。",
            steps_json=["检索项目", "下载数据"],
            example_query="SRR123456",
            entry_url="https://www.ncbi.nlm.nih.gov/sra",
            content="# SRA 下载",
        )
    )
    db_session.add(resource)
    db_session.commit()

    saved = db_session.scalar(
        select(DatabaseResource).where(DatabaseResource.slug == "ncbi")
    )

    assert saved is not None
    assert len(saved.tutorials) == 1
    assert saved.tutorials[0].slug == "sra-fastq-download"


def test_deleting_database_resource_cascades_to_tutorials(
    db_session: Session,
) -> None:
    resource = build_resource()
    resource.tutorials.append(
        DatabaseTutorial(
            slug="sra-fastq-download",
            title="SRA FASTQ 下载教程",
            scenario="从 SRA 下载 FASTQ。",
            steps_json=["检索项目", "下载数据"],
            entry_url="https://www.ncbi.nlm.nih.gov/sra",
            content="# SRA 下载",
        )
    )
    db_session.add(resource)
    db_session.commit()

    db_session.delete(resource)
    db_session.commit()

    tutorial = db_session.scalar(select(DatabaseTutorial))
    assert tutorial is None
