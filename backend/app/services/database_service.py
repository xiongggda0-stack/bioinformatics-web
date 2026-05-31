from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial
from app.repositories.database_repository import DatabaseRepository


class DatabaseService:
    def __init__(self, db: Session) -> None:
        self.repository = DatabaseRepository(db)

    def list_resources(
        self,
        keyword: str | None = None,
        category_key: str | None = None,
        data_type: str | None = None,
        species: str | None = None,
        limit: int = 100,
    ) -> list[DatabaseResource]:
        return self.repository.list_resources(
            keyword=keyword,
            category_key=category_key,
            data_type=data_type,
            species=species,
            limit=limit,
        )

    def get_resource(self, slug: str) -> DatabaseResource:
        resource = self.repository.get_resource_by_slug(slug)
        if resource is None:
            raise HTTPException(status_code=404, detail="数据库资源不存在")
        return resource

    def get_tutorial(self, slug: str) -> DatabaseTutorial:
        tutorial = self.repository.get_tutorial_by_slug(slug)
        if tutorial is None:
            raise HTTPException(status_code=404, detail="数据库教程不存在")
        return tutorial
