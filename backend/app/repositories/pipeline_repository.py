from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.pipeline import Pipeline


class PipelineRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_pipelines(
        self,
        keyword: str | None = None,
        omics_type: str | None = None,
        category_key: str | None = None,
        difficulty: str | None = None,
        tool: str | None = None,
        input_type: str | None = None,
        output_type: str | None = None,
        scenario: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Pipeline]:
        statement = select(Pipeline).order_by(Pipeline.created_at.desc(), Pipeline.id.desc())

        if keyword:
            keyword_like = f"%{keyword.strip()}%"
            statement = statement.where(
                or_(
                    Pipeline.title.ilike(keyword_like),
                    Pipeline.description.ilike(keyword_like),
                    Pipeline.omics_type.ilike(keyword_like),
                    Pipeline.content.ilike(keyword_like),
                )
            )

        if omics_type:
            statement = statement.where(Pipeline.omics_type == omics_type)

        if category_key:
            statement = statement.where(Pipeline.category_key == category_key)

        pipelines = list(self.db.scalars(statement).all())
        pipelines = [
            pipeline
            for pipeline in pipelines
            if self._matches_metadata_filters(
                pipeline.metadata_json,
                difficulty=difficulty,
                tool=tool,
                input_type=input_type,
                output_type=output_type,
                scenario=scenario,
            )
        ]

        return pipelines[skip : skip + limit]

    def get_pipeline_by_id(self, pipeline_id: int) -> Pipeline | None:
        return self.db.get(Pipeline, pipeline_id)

    def _matches_metadata_filters(
        self,
        metadata: dict[str, Any] | None,
        difficulty: str | None = None,
        tool: str | None = None,
        input_type: str | None = None,
        output_type: str | None = None,
        scenario: str | None = None,
    ) -> bool:
        metadata = metadata or {}

        if difficulty and metadata.get("difficulty") != difficulty:
            return False

        if scenario and scenario.lower() not in str(metadata.get("scenario", "")).lower():
            return False

        if tool and not self._list_contains(metadata.get("tools"), tool):
            return False

        if input_type and not self._list_contains(metadata.get("inputs"), input_type):
            return False

        if output_type and not self._list_contains(metadata.get("outputs"), output_type):
            return False

        return True

    def _list_contains(self, values: Any, expected: str) -> bool:
        if not isinstance(values, list):
            return False

        expected_terms = [term.strip().lower() for term in expected.split(",") if term.strip()]
        if not expected_terms:
            return True

        normalized_values = [str(value).lower() for value in values]
        return all(
            any(term in value for value in normalized_values)
            for term in expected_terms
        )
