from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Algorithm, Literature, Pipeline


def build_mock_literatures(
    wgs_pipeline_id: int | None,
    scrna_pipeline_id: int | None,
    bwa_algorithm_id: int | None,
    seurat_algorithm_id: int | None,
    cellranger_algorithm_id: int | None,
) -> list[dict[str, Any]]:
    return [
        {
            "title": "Fast and accurate short read alignment with Burrows-Wheeler transform",
            "authors": ["Heng Li", "Richard Durbin"],
            "journal": "Bioinformatics",
            "publication_year": 2009,
            "doi": "10.1093/bioinformatics/btp324",
            "abstract_text": (
                "This landmark paper introduced BWA, a Burrows-Wheeler transform based "
                "short-read aligner designed for efficient mapping against large reference "
                "genomes. It established the algorithmic foundation for many WGS and WES "
                "variant calling pipelines, including workflows that later adopted BWA-MEM "
                "for longer reads and paired-end sequencing data."
            ),
            "pipeline_id": wgs_pipeline_id,
            "algorithm_id": bwa_algorithm_id,
        },
        {
            "title": "Dictionary learning for integrative, multimodal and scalable single-cell analysis",
            "authors": [
                "Yuhan Hao",
                "Tim Stuart",
                "Madeline H. Kowalski",
                "Saket Choudhary",
                "Paul Hoffman",
                "Austin Hartman",
                "Avi Srivastava",
                "Gesmira Molla",
                "Shaista Madad",
                "Carlos Fernandez-Granda",
                "Rahul Satija",
            ],
            "journal": "Nature Biotechnology",
            "publication_year": 2024,
            "doi": "10.1038/s41587-023-01767-y",
            "abstract_text": (
                "This work presents dictionary learning strategies used in Seurat v5 for "
                "integrative and scalable analysis of multimodal single-cell data. The study "
                "connects computational representation learning with practical single-cell "
                "tasks such as cross-dataset integration, modality alignment and annotation "
                "transfer across complex biological atlases."
            ),
            "pipeline_id": scrna_pipeline_id,
            "algorithm_id": seurat_algorithm_id,
        },
        {
            "title": "Massively parallel digital transcriptional profiling of single cells",
            "authors": [
                "Grace X. Y. Zheng",
                "Jessica M. Terry",
                "Phillip Belgrader",
                "Paul Ryvkin",
                "Zachary W. Bent",
                "Ryan Wilson",
                "Solongo B. Ziraldo",
                "Tobias D. Wheeler",
            ],
            "journal": "Nature Communications",
            "publication_year": 2017,
            "doi": "10.1038/ncomms14049",
            "abstract_text": (
                "This paper describes a high-throughput droplet-based single-cell RNA-seq "
                "system that enabled large-scale digital transcriptional profiling. It is a "
                "key experimental foundation for 10x Genomics workflows and motivates the "
                "preprocessing steps performed by tools such as Cell Ranger."
            ),
            "pipeline_id": scrna_pipeline_id,
            "algorithm_id": cellranger_algorithm_id,
        },
    ]


def seed_literatures(db: Session) -> None:
    wgs_pipeline_id = db.scalar(
        select(Pipeline.id).where(Pipeline.title == "WGS 变异检测流程")
    )
    scrna_pipeline_id = db.scalar(
        select(Pipeline.id).where(Pipeline.title == "10x 单细胞基础降维聚类")
    )
    bwa_algorithm_id = db.scalar(select(Algorithm.id).where(Algorithm.name == "BWA-MEM"))
    seurat_algorithm_id = db.scalar(select(Algorithm.id).where(Algorithm.name == "Seurat v5"))
    cellranger_algorithm_id = db.scalar(
        select(Algorithm.id).where(Algorithm.name == "Cell Ranger")
    )

    # DOI 是文献记录的稳定唯一键；重复执行脚本时更新关联关系，保证跨模块跳转可用。
    # Use DOI as the stable upsert key so repeated seed runs can refresh links.
    for item in build_mock_literatures(
        wgs_pipeline_id,
        scrna_pipeline_id,
        bwa_algorithm_id,
        seurat_algorithm_id,
        cellranger_algorithm_id,
    ):
        literature = db.scalar(select(Literature).where(Literature.doi == item["doi"]))
        if literature is None:
            db.add(Literature(**item))
            continue

        literature.title = item["title"]
        literature.authors = item["authors"]
        literature.journal = item["journal"]
        literature.publication_year = item["publication_year"]
        literature.abstract_text = item["abstract_text"]
        literature.pipeline_id = item["pipeline_id"]
        literature.algorithm_id = item["algorithm_id"]

    db.commit()
