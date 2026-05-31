from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.algorithm import Algorithm
from app.schemas.algorithm import AlgorithmResponse
from app.schemas.relation import AlgorithmRelationsResponse
from app.services.algorithm_service import AlgorithmService
from app.services.relation_service import RelationService

router = APIRouter(prefix="/api/algorithms", tags=["Algorithms"])


@router.get(
    "",
    response_model=list[AlgorithmResponse],
    summary="获取算法与工具列表",
    description="返回 Algorithm Gallery 中已登记的生信算法和工具条目。",
)
def list_algorithms(
    keyword: str | None = Query(default=None, description="按算法名、分类、简介或文档全文搜索"),
    category_key: str | None = Query(default=None, description="按算法分类 key 筛选"),
    category: str | None = Query(default=None, description="按算法原始分类名称筛选"),
    skip: int = Query(default=0, ge=0, description="分页起始偏移量"),
    limit: int = Query(default=100, ge=1, le=200, description="单次返回数量上限"),
    db: Session = Depends(get_db),
) -> list[Algorithm]:
    service = AlgorithmService(db)
    return service.list_algorithms(
        keyword=keyword,
        category_key=category_key,
        category=category,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{algorithm_id}/relations",
    response_model=AlgorithmRelationsResponse,
    summary="获取算法关联资源",
    description="返回与指定 Algorithm 关联的分析流程和文献，用于详情页交叉跳转。",
)
def get_algorithm_relations(
    algorithm_id: int, db: Session = Depends(get_db)
) -> dict[str, object]:
    service = RelationService(db)
    return service.get_algorithm_relations(algorithm_id)


@router.get(
    "/{algorithm_id}",
    response_model=AlgorithmResponse,
    summary="获取算法与工具详情",
    description="根据算法 ID 返回分类、简介、性能基准预留数据与 Markdown 原理文档。",
)
def get_algorithm(algorithm_id: int, db: Session = Depends(get_db)) -> Algorithm:
    service = AlgorithmService(db)
    return service.get_algorithm(algorithm_id)
