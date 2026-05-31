from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Algorithm, Literature, Pipeline


class RelationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_pipeline(self, pipeline_id: int) -> Pipeline | None:
        return self.db.get(Pipeline, pipeline_id)

    def get_algorithm(self, algorithm_id: int) -> Algorithm | None:
        return self.db.get(Algorithm, algorithm_id)

    def get_literature(self, literature_id: int) -> Literature | None:
        return self.db.get(Literature, literature_id)

    def list_literatures_for_pipeline(self, pipeline_id: int) -> list[Literature]:
        statement = (
            select(Literature)
            .where(Literature.pipeline_id == pipeline_id)
            .order_by(Literature.publication_year.desc(), Literature.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_literatures_for_algorithm(self, algorithm_id: int) -> list[Literature]:
        statement = (
            select(Literature)
            .where(Literature.algorithm_id == algorithm_id)
            .order_by(Literature.publication_year.desc(), Literature.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_algorithms_for_pipeline(self, pipeline: Pipeline) -> list[Algorithm]:
        algorithms_by_id: dict[int, Algorithm] = {}

        explicit_statement = (
            select(Algorithm)
            .join(Literature, Literature.algorithm_id == Algorithm.id)
            .where(Literature.pipeline_id == pipeline.id)
        )
        for algorithm in self.db.scalars(explicit_statement).all():
            algorithms_by_id[algorithm.id] = algorithm

        tool_names = self._metadata_list(pipeline.metadata_json, "tools")
        if tool_names:
            for algorithm in self.db.scalars(select(Algorithm)).all():
                if self._algorithm_matches_tools(algorithm, tool_names):
                    algorithms_by_id[algorithm.id] = algorithm

        return sorted(algorithms_by_id.values(), key=lambda item: item.id)

    def list_pipelines_for_algorithm(self, algorithm: Algorithm) -> list[Pipeline]:
        pipelines_by_id: dict[int, Pipeline] = {}

        explicit_statement = (
            select(Pipeline)
            .join(Literature, Literature.pipeline_id == Pipeline.id)
            .where(Literature.algorithm_id == algorithm.id)
        )
        for pipeline in self.db.scalars(explicit_statement).all():
            pipelines_by_id[pipeline.id] = pipeline

        for pipeline in self.db.scalars(select(Pipeline)).all():
            tool_names = self._metadata_list(pipeline.metadata_json, "tools")
            if self._algorithm_matches_tools(algorithm, tool_names):
                pipelines_by_id[pipeline.id] = pipeline

        return sorted(pipelines_by_id.values(), key=lambda item: item.id)

    def _metadata_list(self, metadata: dict[str, Any] | None, key: str) -> list[str]:
        values = (metadata or {}).get(key, [])
        if not isinstance(values, list):
            return []
        return [str(value).strip() for value in values if str(value).strip()]

    def _algorithm_matches_tools(self, algorithm: Algorithm, tools: list[str]) -> bool:
        algorithm_name = algorithm.name.lower()
        for tool in tools:
            normalized_tool = tool.lower()
            if algorithm_name in normalized_tool or normalized_tool in algorithm_name:
                return True
        return False
