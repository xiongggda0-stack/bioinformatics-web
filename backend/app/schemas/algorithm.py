from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AlgorithmBase(BaseModel):
    name: str = Field(..., max_length=160)
    category: str = Field(..., max_length=100)
    category_key: str = Field(..., max_length=80)
    category_name: str = Field(..., max_length=120)
    tool_type: str = Field(..., max_length=80)
    summary: str = Field(..., max_length=500)
    performance_json: dict[str, Any]
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    markdown_docs: str


class AlgorithmCreate(AlgorithmBase):
    pass


class AlgorithmResponse(AlgorithmBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
