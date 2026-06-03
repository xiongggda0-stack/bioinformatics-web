"""Schemas for literature import endpoints."""

from pydantic import BaseModel, Field


class PubmedImportRequest(BaseModel):
    pmids: list[str] = Field(..., min_length=1, max_length=50)
    auto_match: bool = True


class DoiImportRequest(BaseModel):
    doi: str = Field(..., min_length=5, max_length=200)
    pipeline_id: int | None = None
    algorithm_id: int | None = None
    auto_match: bool = True


class ImportDetail(BaseModel):
    identifier: str  # PMID or DOI
    title: str | None = None
    status: str  # "imported" | "skipped" | "failed"
    matched_to: str | None = None
    error: str | None = None


class ImportReport(BaseModel):
    imported: int = 0
    skipped: int = 0
    failed: int = 0
    matched: int = 0
    details: list[ImportDetail]
