from pydantic import BaseModel, ConfigDict, Field


class LiteratureBase(BaseModel):
    title: str = Field(..., max_length=500)
    authors: list[str]
    journal: str = Field(..., max_length=180)
    publication_year: int
    doi: str = Field(..., max_length=160)
    abstract_text: str
    pipeline_id: int | None = None
    algorithm_id: int | None = None


class LiteratureCreate(LiteratureBase):
    pass


class LiteratureResponse(LiteratureBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
