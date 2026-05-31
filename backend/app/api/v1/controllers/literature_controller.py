from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.literature import Literature
from app.schemas.literature import LiteratureResponse
from app.schemas.relation import LiteratureRelationsResponse
from app.services.literature_service import LiteratureService
from app.services.relation_service import RelationService

router = APIRouter(prefix="/api/literatures", tags=["Literatures"])


@router.get(
    "",
    response_model=list[LiteratureResponse],
    summary="获取文献列表",
    description="返回 Literature Hub 中已登记的生信文献动态列表。",
)
def list_literatures(db: Session = Depends(get_db)) -> list[Literature]:
    service = LiteratureService(db)
    return service.list_literatures()


@router.get(
    "/{literature_id}/relations",
    response_model=LiteratureRelationsResponse,
    summary="获取文献关联资源",
    description="返回文献关联的分析流程和算法工具，用于详情页交叉跳转。",
)
def get_literature_relations(
    literature_id: int, db: Session = Depends(get_db)
) -> dict[str, object]:
    service = RelationService(db)
    return service.get_literature_relations(literature_id)


@router.get(
    "/{literature_id}",
    response_model=LiteratureResponse,
    summary="获取文献详情",
    description="根据文献 ID 返回标题、作者、期刊、DOI、摘要以及关联的流程或算法 ID。",
)
def get_literature(literature_id: int, db: Session = Depends(get_db)) -> Literature:
    service = LiteratureService(db)
    return service.get_literature(literature_id)
