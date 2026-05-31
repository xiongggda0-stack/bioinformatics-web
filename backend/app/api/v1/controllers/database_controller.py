from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial
from app.schemas.database_resource import (
    DatabaseResourceResponse,
    DatabaseTutorialDetailResponse,
)
from app.services.database_service import DatabaseService

router = APIRouter(prefix="/api/databases", tags=["Databases"])


@router.get(
    "",
    response_model=list[DatabaseResourceResponse],
    summary="获取数据库导航列表",
)
def list_databases(
    keyword: str | None = Query(default=None, description="按名称、分类或用途搜索"),
    category_key: str | None = Query(default=None, description="按数据库分类筛选"),
    data_type: str | None = Query(default=None, description="按数据类型筛选"),
    species: str | None = Query(default=None, description="按物种筛选"),
    limit: int = Query(default=100, ge=1, le=200, description="返回数量上限"),
    db: Session = Depends(get_db),
) -> list[DatabaseResource]:
    service = DatabaseService(db)
    return service.list_resources(
        keyword=keyword,
        category_key=category_key,
        data_type=data_type,
        species=species,
        limit=limit,
    )


@router.get(
    "/tutorials/{tutorial_slug}",
    response_model=DatabaseTutorialDetailResponse,
    summary="获取数据库教程详情",
)
def get_database_tutorial(
    tutorial_slug: str, db: Session = Depends(get_db)
) -> DatabaseTutorial:
    service = DatabaseService(db)
    return service.get_tutorial(tutorial_slug)


@router.get(
    "/{resource_slug}",
    response_model=DatabaseResourceResponse,
    summary="获取数据库资源详情",
)
def get_database_resource(
    resource_slug: str, db: Session = Depends(get_db)
) -> DatabaseResource:
    service = DatabaseService(db)
    return service.get_resource(resource_slug)
