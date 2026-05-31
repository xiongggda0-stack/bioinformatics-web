from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.pipeline import Pipeline
from app.repositories.pipeline_repository import PipelineRepository


class PipelineService:
    def __init__(self, db: Session) -> None:
        self.repository = PipelineRepository(db)

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
        return self.repository.list_pipelines(
            keyword=keyword,
            omics_type=omics_type,
            category_key=category_key,
            difficulty=difficulty,
            tool=tool,
            input_type=input_type,
            output_type=output_type,
            scenario=scenario,
            skip=skip,
            limit=limit,
        )

    def get_pipeline(self, pipeline_id: int) -> Pipeline:
        pipeline = self.repository.get_pipeline_by_id(pipeline_id)
        if pipeline is None:
            raise HTTPException(status_code=404, detail="分析流程不存在")
        return pipeline
