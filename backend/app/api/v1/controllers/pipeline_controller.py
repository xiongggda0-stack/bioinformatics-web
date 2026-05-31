from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.pipeline import Pipeline
from app.schemas.pipeline import PipelineResponse
from app.schemas.relation import PipelineRelationsResponse
from app.services.pipeline_service import PipelineService
from app.services.relation_service import RelationService

router = APIRouter(prefix="/api/pipelines", tags=["Pipelines"])


@router.get(
    "",
    response_model=list[PipelineResponse],
    summary="获取分析流程列表",
    description=(
        "返回 Pipeline Hub 中已登记的生信分析流程列表，支持关键词、分类、"
        "组学类型、难度、工具、输入、输出、场景和分页筛选。"
    ),
)
def list_pipelines(
    keyword: str | None = Query(
        default=None,
        description="关键词搜索，匹配标题、简介、组学类型和 Markdown 正文。",
    ),
    omics_type: str | None = Query(
        default=None,
        description="按组学或分析模块精确筛选，例如 RNA-Seq、scRNA-Seq、WGS。",
    ),
    category_key: str | None = Query(
        default=None,
        description="按流程分类筛选，例如 basic、structure、single-spatial、variant。",
    ),
    difficulty: str | None = Query(
        default=None,
        description="按难度筛选：入门、中级、高级。",
    ),
    tool: str | None = Query(
        default=None,
        description="按工具筛选，支持逗号组合，例如 DESeq2 或 STAR,featureCounts。",
    ),
    input_type: str | None = Query(
        default=None,
        description="按输入类型筛选，例如 FASTQ、BAM、TPM、count matrix。",
    ),
    output_type: str | None = Query(
        default=None,
        description="按输出类型筛选，例如 DEG table、heatmap、report。",
    ),
    scenario: str | None = Query(
        default=None,
        description="按应用场景筛选，例如 肿瘤转录组、非模式物种、单细胞分析。",
    ),
    skip: int = Query(default=0, ge=0, description="分页偏移量。"),
    limit: int = Query(default=100, ge=1, le=200, description="返回数量上限。"),
    db: Session = Depends(get_db),
) -> list[Pipeline]:
    service = PipelineService(db)
    return service.list_pipelines(
        keyword=keyword,
        omics_type=omics_type,
        category_key=category_key,
        difficulty=difficulty,
        tool=tool,
        input_type=input_type,
        output_type=output_type,
        scenario=scenario,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{pipeline_id}/relations",
    response_model=PipelineRelationsResponse,
    summary="获取分析流程关联资源",
    description="返回与指定 Pipeline 关联的算法工具和文献，用于详情页交叉跳转。",
)
def get_pipeline_relations(
    pipeline_id: int, db: Session = Depends(get_db)
) -> dict[str, object]:
    service = RelationService(db)
    return service.get_pipeline_relations(pipeline_id)


@router.get(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="获取单个分析流程详情",
    description="根据流程 ID 返回流程元数据、DAG 节点数据和 Markdown 文档内容。",
)
def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)) -> Pipeline:
    service = PipelineService(db)
    return service.get_pipeline(pipeline_id)
