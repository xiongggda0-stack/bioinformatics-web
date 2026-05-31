from collections import Counter
from collections.abc import Iterable
from urllib.parse import quote

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm
from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial
from app.models.literature import Literature
from app.models.pipeline import Pipeline
from app.repositories.search_repository import SearchRepository
from app.schemas.search import (
    SearchItemType,
    SearchResourceType,
    SearchResponse,
    SearchResultCounts,
    SearchResultItem,
)


TYPE_PRIORITY: dict[SearchItemType, int] = {
    "pipeline": 0,
    "algorithm": 1,
    "database": 2,
    "tutorial": 3,
    "literature": 4,
}


class SearchService:
    def __init__(self, db: Session) -> None:
        self.repository = SearchRepository(db)

    def search(
        self,
        query: str,
        resource_type: SearchResourceType = "all",
        limit: int = 20,
    ) -> SearchResponse:
        normalized_query = query.strip()
        if len(normalized_query) < 2:
            raise HTTPException(
                status_code=400,
                detail="搜索关键词至少需要 2 个字符",
            )

        items = [
            *self._search_pipelines(normalized_query),
            *self._search_algorithms(normalized_query),
            *self._search_databases(normalized_query),
            *self._search_tutorials(normalized_query),
            *self._search_literatures(normalized_query),
        ]
        counts = Counter(item.type for item in items)

        if resource_type != "all":
            items = [item for item in items if item.type == resource_type]

        items.sort(
            key=lambda item: (
                -item.score,
                TYPE_PRIORITY[item.type],
                self._get_numeric_id(item.id),
            )
        )

        return SearchResponse(
            query=normalized_query,
            total=len(items),
            counts=SearchResultCounts(
                pipeline=counts["pipeline"],
                algorithm=counts["algorithm"],
                database=counts["database"],
                tutorial=counts["tutorial"],
                literature=counts["literature"],
            ),
            items=items[:limit],
        )

    def _search_pipelines(self, query: str) -> list[SearchResultItem]:
        items: list[SearchResultItem] = []
        for pipeline in self.repository.list_pipelines():
            score = self._score(
                query,
                primary=pipeline.title,
                categories=[
                    pipeline.omics_type,
                    pipeline.category_key,
                    pipeline.category_name,
                    *(pipeline.metadata_json or {}).get("tools", []),
                ],
                summaries=[pipeline.description],
                bodies=[pipeline.content],
            )
            if score:
                items.append(
                    SearchResultItem(
                        id=f"pipeline-{pipeline.id}",
                        type="pipeline",
                        title=pipeline.title,
                        description=pipeline.description,
                        href=f"/pipelines/{pipeline.id}",
                        tags=[pipeline.omics_type, pipeline.category_name],
                        score=score,
                    )
                )
        return items

    def _search_algorithms(self, query: str) -> list[SearchResultItem]:
        items: list[SearchResultItem] = []
        for algorithm in self.repository.list_algorithms():
            score = self._score(
                query,
                primary=algorithm.name,
                categories=[
                    algorithm.category,
                    algorithm.category_key,
                    algorithm.category_name,
                    algorithm.tool_type,
                ],
                summaries=[algorithm.summary],
                bodies=[algorithm.markdown_docs],
            )
            if score:
                items.append(
                    SearchResultItem(
                        id=f"algorithm-{algorithm.id}",
                        type="algorithm",
                        title=algorithm.name,
                        description=algorithm.summary,
                        href=f"/algorithms/{algorithm.id}",
                        tags=[algorithm.category_name, algorithm.tool_type],
                        score=score,
                    )
                )
        return items

    def _search_databases(self, query: str) -> list[SearchResultItem]:
        items: list[SearchResultItem] = []
        for resource in self.repository.list_databases():
            score = self._score(
                query,
                primary=resource.name,
                categories=[
                    resource.slug,
                    resource.full_name,
                    resource.category_key,
                    resource.category_name,
                    *resource.tags_json,
                    *resource.data_types_json,
                    *resource.species_json,
                ],
                summaries=[resource.description, *resource.use_cases_json],
            )
            if score:
                items.append(
                    SearchResultItem(
                        id=f"database-{resource.id}",
                        type="database",
                        title=resource.name,
                        description=resource.description,
                        href=f"/databases?keyword={quote(resource.name)}",
                        tags=[resource.category_name, *resource.tags_json[:2]],
                        score=score,
                    )
                )
        return items

    def _search_tutorials(self, query: str) -> list[SearchResultItem]:
        items: list[SearchResultItem] = []
        for tutorial in self.repository.list_tutorials():
            score = self._score(
                query,
                primary=tutorial.title,
                categories=[
                    tutorial.resource.name,
                    tutorial.resource.category_name,
                    *tutorial.steps_json,
                ],
                summaries=[tutorial.scenario, tutorial.example_query or ""],
                bodies=[tutorial.content],
            )
            if score:
                items.append(
                    SearchResultItem(
                        id=f"tutorial-{tutorial.id}",
                        type="tutorial",
                        title=tutorial.title,
                        description=tutorial.scenario,
                        href=f"/databases/tutorials/{tutorial.slug}",
                        tags=[tutorial.resource.name, "教程"],
                        score=score,
                    )
                )
        return items

    def _search_literatures(self, query: str) -> list[SearchResultItem]:
        items: list[SearchResultItem] = []
        for literature in self.repository.list_literatures():
            score = self._score(
                query,
                primary=literature.title,
                categories=[
                    literature.journal,
                    str(literature.publication_year),
                    *literature.authors,
                ],
                summaries=[literature.abstract_text],
            )
            if score:
                items.append(
                    SearchResultItem(
                        id=f"literature-{literature.id}",
                        type="literature",
                        title=literature.title,
                        description=f"{literature.journal} · {literature.publication_year}",
                        href=f"/literatures/{literature.id}",
                        tags=[literature.journal, str(literature.publication_year)],
                        score=score,
                    )
                )
        return items

    def _score(
        self,
        query: str,
        primary: str,
        categories: Iterable[str] = (),
        summaries: Iterable[str] = (),
        bodies: Iterable[str] = (),
    ) -> int:
        normalized_query = query.lower()
        normalized_primary = primary.lower()

        if normalized_primary == normalized_query:
            return 100
        if normalized_query in normalized_primary:
            return 70
        if self._contains(categories, normalized_query):
            return 40
        if self._contains(summaries, normalized_query):
            return 20
        if self._contains(bodies, normalized_query):
            return 10
        return 0

    def _contains(self, values: Iterable[str], query: str) -> bool:
        return any(query in str(value).lower() for value in values)

    def _get_numeric_id(self, item_id: str) -> int:
        return int(item_id.rsplit("-", maxsplit=1)[-1])
