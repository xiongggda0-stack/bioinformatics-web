from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm


class AlgorithmRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_algorithms(
        self,
        keyword: str | None = None,
        category_key: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Algorithm]:
        statement = select(Algorithm).order_by(Algorithm.created_at.desc(), Algorithm.id.desc())

        if keyword:
            keyword_like = f"%{keyword.strip()}%"
            statement = statement.where(
                or_(
                    Algorithm.name.ilike(keyword_like),
                    Algorithm.category.ilike(keyword_like),
                    Algorithm.category_name.ilike(keyword_like),
                    Algorithm.tool_type.ilike(keyword_like),
                    Algorithm.summary.ilike(keyword_like),
                    Algorithm.markdown_docs.ilike(keyword_like),
                )
            )

        if category_key:
            statement = statement.where(Algorithm.category_key == category_key)

        if category:
            statement = statement.where(Algorithm.category == category)

        statement = statement.offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())

    def get_algorithm_by_id(self, algorithm_id: int) -> Algorithm | None:
        return self.db.get(Algorithm, algorithm_id)
