from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Algorithm, Literature, Pipeline
from app.repositories.relation_repository import RelationRepository


class RelationService:
    def __init__(self, db: Session) -> None:
        self.repository = RelationRepository(db)

    def get_pipeline_relations(self, pipeline_id: int) -> dict[str, object]:
        pipeline = self.repository.get_pipeline(pipeline_id)
        if pipeline is None:
            raise HTTPException(status_code=404, detail="Pipeline 不存在")

        return {
            "pipeline_id": pipeline.id,
            "algorithms": self.repository.list_algorithms_for_pipeline(pipeline),
            "literatures": self.repository.list_literatures_for_pipeline(pipeline.id),
        }

    def get_algorithm_relations(self, algorithm_id: int) -> dict[str, object]:
        algorithm = self.repository.get_algorithm(algorithm_id)
        if algorithm is None:
            raise HTTPException(status_code=404, detail="Algorithm 不存在")

        return {
            "algorithm_id": algorithm.id,
            "pipelines": self.repository.list_pipelines_for_algorithm(algorithm),
            "literatures": self.repository.list_literatures_for_algorithm(algorithm.id),
        }

    def get_literature_relations(self, literature_id: int) -> dict[str, Pipeline | Algorithm | Literature | None | int]:
        literature = self.repository.get_literature(literature_id)
        if literature is None:
            raise HTTPException(status_code=404, detail="Literature 不存在")

        pipeline = (
            self.repository.get_pipeline(literature.pipeline_id)
            if literature.pipeline_id is not None
            else None
        )
        algorithm = (
            self.repository.get_algorithm(literature.algorithm_id)
            if literature.algorithm_id is not None
            else None
        )

        return {
            "literature_id": literature.id,
            "pipeline": pipeline,
            "algorithm": algorithm,
        }
