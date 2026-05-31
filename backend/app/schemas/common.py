from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None


class ErrorResponse(BaseModel):
    code: int
    message: str
    data: None = None
