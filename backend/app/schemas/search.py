from typing import Literal

from pydantic import BaseModel, Field


SearchResourceType = Literal[
    "all",
    "pipeline",
    "algorithm",
    "database",
    "tutorial",
    "literature",
]
SearchItemType = Literal[
    "pipeline",
    "algorithm",
    "database",
    "tutorial",
    "literature",
]


class SearchResultItem(BaseModel):
    id: str
    type: SearchItemType
    title: str
    description: str
    href: str
    tags: list[str] = Field(default_factory=list)
    score: int


class SearchResultCounts(BaseModel):
    pipeline: int = 0
    algorithm: int = 0
    database: int = 0
    tutorial: int = 0
    literature: int = 0


class SearchResponse(BaseModel):
    query: str
    total: int
    counts: SearchResultCounts
    items: list[SearchResultItem]
