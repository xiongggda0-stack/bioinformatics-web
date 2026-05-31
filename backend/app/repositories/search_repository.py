from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.algorithm import Algorithm
from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial
from app.models.literature import Literature
from app.models.pipeline import Pipeline


class SearchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_pipelines(self) -> list[Pipeline]:
        return list(self.db.scalars(select(Pipeline)).all())

    def list_algorithms(self) -> list[Algorithm]:
        return list(self.db.scalars(select(Algorithm)).all())

    def list_databases(self) -> list[DatabaseResource]:
        statement = select(DatabaseResource).options(
            selectinload(DatabaseResource.tutorials)
        )
        return list(self.db.scalars(statement).all())

    def list_tutorials(self) -> list[DatabaseTutorial]:
        statement = select(DatabaseTutorial).options(
            joinedload(DatabaseTutorial.resource)
        )
        return list(self.db.scalars(statement).all())

    def list_literatures(self) -> list[Literature]:
        return list(self.db.scalars(select(Literature)).all())
