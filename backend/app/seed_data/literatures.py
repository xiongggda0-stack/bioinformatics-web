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
    cutandtag_pipeline_id: int | None = None,
    wgcna_algorithm_id: int | None = None,
    star_algorithm_id: int | None = None,
    featurecounts_algorithm_id: int | None = None,
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
                "Patrik L. Stahl",
                "Fredrik Salmen",
                "Sanja Vickovic",
                "Anna Lundmark",
                "Jose Fernandez Navarro",
                "Jens Magnusson",
                "Stefania Giacomello",
                "Michaela Asp",
                "Jakub O. Westholm",
                "Mikael Huss",
                "Annellie Mollbrink",
                "Sten Linnarsson",
                "Simone Codeluppi",
                "Ake Borg",
                "Fredrik Ponten",
                "Paul Igor Costea",
                "Peter Sahlen",
                "Jan Mulder",
                "Olaf Bergmann",
                "Joakim Lundeberg",
                "Jonas Frisen",
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

    # DOI 是文献记录的稳定唯一键；重复执行脚本时更新关联关系，保证跨模块跳转可用。
    # Use DOI as the stable upsert key so repeated seed runs can refresh links.
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
