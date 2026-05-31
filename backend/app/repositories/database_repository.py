from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial


class DatabaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_resources(
        self,
        keyword: str | None = None,
        category_key: str | None = None,
        data_type: str | None = None,
        species: str | None = None,
        limit: int = 100,
    ) -> list[DatabaseResource]:
        statement = (
            select(DatabaseResource)
            .options(selectinload(DatabaseResource.tutorials))
            .order_by(DatabaseResource.rating.desc(), DatabaseResource.name.asc())
        )

        if category_key:
            statement = statement.where(DatabaseResource.category_key == category_key)

        resources = list(self.db.scalars(statement).all())
        resources = [
            resource
            for resource in resources
            if self._matches_filters(
                resource,
                keyword=keyword,
                data_type=data_type,
                species=species,
            )
        ]
        return resources[:limit]

    def get_resource_by_slug(self, slug: str) -> DatabaseResource | None:
        statement = (
            select(DatabaseResource)
            .options(selectinload(DatabaseResource.tutorials))
            .where(DatabaseResource.slug == slug)
        )
        return self.db.scalar(statement)

    def get_tutorial_by_slug(self, slug: str) -> DatabaseTutorial | None:
        statement = (
            select(DatabaseTutorial)
            .options(joinedload(DatabaseTutorial.resource))
            .where(DatabaseTutorial.slug == slug)
        )
        return self.db.scalar(statement)

    def _matches_filters(
        self,
        resource: DatabaseResource,
        keyword: str | None = None,
        data_type: str | None = None,
        species: str | None = None,
    ) -> bool:
        if keyword:
            normalized_keyword = keyword.strip().lower()
            searchable_values = [
                resource.slug,
                resource.name,
                resource.full_name,
                resource.category_name,
                resource.description,
                *resource.use_cases_json,
                *resource.data_types_json,
                *resource.species_json,
                *resource.tags_json,
                *[
                    value
                    for tutorial in resource.tutorials
                    for value in [
                        tutorial.title,
                        tutorial.scenario,
                        tutorial.example_query or "",
                        *tutorial.steps_json,
                    ]
                ],
            ]
            if normalized_keyword not in " ".join(searchable_values).lower():
                return False

        if data_type and data_type not in resource.data_types_json:
            return False

        if species and species not in resource.species_json:
            return False

        return True
