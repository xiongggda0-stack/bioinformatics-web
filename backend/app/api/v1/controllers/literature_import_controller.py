"""Literature import endpoints -- PubMed batch + DOI single import."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.literature_import import (
    DoiImportRequest,
    ImportReport,
    PubmedImportRequest,
)
from app.services.literature_importer import LiteratureImporter

router = APIRouter(prefix="/api/literatures/import", tags=["Literature Import"])


def _build_report(details: list) -> ImportReport:
    return ImportReport(
        imported=sum(1 for d in details if d.status == "imported"),
        skipped=sum(1 for d in details if d.status == "skipped"),
        failed=sum(1 for d in details if d.status == "failed"),
        matched=sum(1 for d in details if d.matched_to is not None),
        details=details,
    )


@router.post(
    "/pubmed",
    response_model=ApiResponse[ImportReport],
    summary="PubMed 批量导入",
)
def import_from_pubmed(
    body: PubmedImportRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[ImportReport]:
    importer = LiteratureImporter(db)
    details = importer.import_from_pubmed(
        pmids=body.pmids,
        auto_match=body.auto_match,
    )
    report = _build_report(details)
    return ApiResponse(code=200, message="导入完成", data=report)


@router.post(
    "/doi",
    response_model=ApiResponse[ImportReport],
    summary="DOI 单篇导入",
)
def import_from_doi(
    body: DoiImportRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[ImportReport]:
    importer = LiteratureImporter(db)
    detail = importer.import_from_doi(
        doi=body.doi,
        pipeline_id=body.pipeline_id,
        algorithm_id=body.algorithm_id,
        auto_match=body.auto_match,
    )
    report = _build_report([detail])
    return ApiResponse(code=200, message="导入完成", data=report)
