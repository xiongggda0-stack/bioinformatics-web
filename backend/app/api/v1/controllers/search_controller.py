from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.search import SearchResourceType, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get(
    "",
    response_model=SearchResponse,
    summary="统一搜索平台资源",
    description="按相关度搜索分析流程、软件算法、数据库、教程和文献。",
)
def search_resources(
    q: str = Query(..., description="搜索关键词，至少 2 个字符"),
    resource_type: SearchResourceType = Query(default="all", alias="type"),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> SearchResponse:
    service = SearchService(db)
    return service.search(query=q, resource_type=resource_type, limit=limit)
