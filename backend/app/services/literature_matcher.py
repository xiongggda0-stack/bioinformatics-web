"""Auto-matching engine for literature - Pipeline / Algorithm associations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm
from app.models.pipeline import Pipeline

# Level-2 keyword mapping: canonical term -> (pipeline_title_or_None, algorithm_name_or_None)
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

    Matching is best-effort -- unmatched associations remain ``NULL``.
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

        Manual assignments take precedence over auto-matching.
        """
        self._load_indexes()

        # Manual assignments win
        if manual_pipeline_id is not None or manual_algorithm_id is not None:
            label_parts: list[str] = []
            if manual_pipeline_id is not None:
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
                    label = f"{pipe_target or ''} {algo_target or ''}".strip()
                    return (pid, aid, label)

        return (None, None, None)
