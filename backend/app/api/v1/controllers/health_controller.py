from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.services.health_service import HealthService

router = APIRouter(prefix="/api", tags=["Health"])


@router.get(
    "/health",
    response_model=ApiResponse[dict[str, str]],
    summary="服务健康检查",
    description="检查 API 服务与 PostgreSQL 数据库连接是否正常。",
)
def health_check(db: Session = Depends(get_db)) -> ApiResponse[dict[str, str]]:
    service = HealthService(db)
    return ApiResponse(code=0, message="ok", data=service.check())

