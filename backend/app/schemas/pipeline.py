from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PipelineBase(BaseModel):
    title: str = Field(..., max_length=180)
    description: str = Field(..., max_length=500)
    omics_type: str = Field(..., max_length=80)
    category_key: str = Field(..., max_length=80)
    category_name: str = Field(..., max_length=120)
    dag_json: dict[str, Any]
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    content: str


class PipelineCreate(PipelineBase):
    pass


class PipelineResponse(PipelineBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
