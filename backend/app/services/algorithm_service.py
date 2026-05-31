from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm
from app.repositories.algorithm_repository import AlgorithmRepository


class AlgorithmService:
    def __init__(self, db: Session) -> None:
        self.repository = AlgorithmRepository(db)

    def list_algorithms(
        self,
        keyword: str | None = None,
        category_key: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Algorithm]:
        return self.repository.list_algorithms(
            keyword=keyword,
            category_key=category_key,
            category=category,
            skip=skip,
            limit=limit,
        )

    def get_algorithm(self, algorithm_id: int) -> Algorithm:
        algorithm = self.repository.get_algorithm_by_id(algorithm_id)
        if algorithm is None:
            raise HTTPException(status_code=404, detail="算法或工具不存在")
        return algorithm
