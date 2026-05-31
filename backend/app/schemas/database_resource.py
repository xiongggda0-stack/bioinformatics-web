from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DatabaseTutorialBase(BaseModel):
    slug: str = Field(..., max_length=160)
    title: str = Field(..., max_length=240)
    scenario: str
    steps_json: list[str] = Field(default_factory=list)
    example_query: str | None = None
    entry_url: str = Field(..., max_length=500)
    content: str


class DatabaseTutorialResponse(DatabaseTutorialBase):
    id: int
    database_resource_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatabaseResourceBase(BaseModel):
    slug: str = Field(..., max_length=120)
    name: str = Field(..., max_length=120)
    full_name: str = Field(..., max_length=240)
    category_key: str = Field(..., max_length=80)
    category_name: str = Field(..., max_length=120)
    description: str
    use_cases_json: list[str] = Field(default_factory=list)
    data_types_json: list[str] = Field(default_factory=list)
    species_json: list[str] = Field(default_factory=list)
    tags_json: list[str] = Field(default_factory=list)
    url: str = Field(..., max_length=500)
    download_url: str | None = Field(default=None, max_length=500)
    api_url: str | None = Field(default=None, max_length=500)
    region: str = Field(..., max_length=120)
    rating: int = Field(..., ge=1, le=5)


class DatabaseResourceResponse(DatabaseResourceBase):
    id: int
    created_at: datetime
    tutorials: list[DatabaseTutorialResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DatabaseTutorialDetailResponse(DatabaseTutorialResponse):
    resource: DatabaseResourceBase

    model_config = ConfigDict(from_attributes=True)
