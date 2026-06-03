from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.controllers.algorithm_controller import router as algorithm_router
from app.api.v1.controllers.database_controller import router as database_router
from app.api.v1.controllers.health_controller import router as health_router
from app.api.v1.controllers.literature_controller import router as literature_router
from app.api.v1.controllers.pipeline_controller import router as pipeline_router
from app.api.v1.controllers.search_controller import router as search_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import register_exception_handlers
from app.models import (
    algorithm,
    database_resource,
    database_tutorial,
    literature,
    pipeline,
    user,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="一站式生信云平台 MVP 后端服务",
        version="0.1.0",
    )

    origins = settings.cors_origins.split(",") if settings.cors_origins else ["http://localhost:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(pipeline_router)
    app.include_router(algorithm_router)
    app.include_router(database_router)
    app.include_router(literature_router)
    app.include_router(search_router)

    return app


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    # MVP 阶段直接建表；进入正式迭代后建议替换为 Alembic 迁移。
    Base.metadata.create_all(bind=engine)
