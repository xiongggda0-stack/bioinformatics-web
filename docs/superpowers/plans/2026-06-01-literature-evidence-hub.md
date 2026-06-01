# 文献与动态集轻量证据中心 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 Literature 演示模块升级为可公开展示的轻量证据中心：支持人工精选文献、结构化中文导读、URL 同步搜索筛选、多对多资源关联和反向证据链。

**Architecture:** 保持现有 FastAPI Controller-Service-Repository 与 Next.js App Router 架构。Literature 主表保存论文元数据与人工导读，三个关联表分别连接 Pipeline、Algorithm 和 DatabaseTutorial；列表接口返回轻量关联计数，详情关系接口返回完整关联对象。人工精选内容拆入 JSON seed 文件，由现有 `literatures.py` 负责读取、校验、upsert 和稳定业务键解析。

**Tech Stack:** Python 3.12、FastAPI、Pydantic、SQLAlchemy、PostgreSQL 15、pytest、Next.js 14 App Router、React、TypeScript、TailwindCSS、Docker Compose。

---

## 文件结构

### 新建文件

```text
backend/
  app/models/literature_link.py                 三张 Literature 多对多关联表
  app/seed_data/literature_records/
    core_methods.json                           经典方法论文
    reviews_guides.json                         综述与实践指南
    frontier_research.json                      人工精选前沿动态
  tests/test_literature_model.py                Literature 新字段默认值
  tests/test_literature_seed.py                 JSON seed、幂等性与关系解析
  tests/test_literature_api.py                  搜索筛选与排序接口
  tests/test_literature_relations.py            正向、反向多对多证据链

frontend/
  components/LiteratureBrowser.tsx              文献列表搜索筛选和卡片
  lib/literatureTypes.ts                        Literature 前端 DTO 与筛选类型
```

### 修改文件

```text
backend/
  app/models/literature.py                      增加结构化导读字段和关联关系
  app/models/__init__.py                        暴露关联模型
  app/schemas/literature.py                     区分列表项与详情响应
  app/schemas/relation.py                       增加 DatabaseTutorial 关联结构
  app/repositories/literature_repository.py     增加搜索、筛选和 selectinload
  app/repositories/relation_repository.py       改用多对多表查询
  app/services/literature_service.py            生成列表关联计数
  app/services/relation_service.py              返回多资源数组和教程反向关系
  app/services/search_service.py                全站搜索纳入中文导读和关键词
  app/api/v1/controllers/literature_controller.py
                                                  暴露列表筛选参数
  app/api/v1/controllers/database_controller.py 增加教程关系接口
  app/seed_data/literatures.py                   JSON loader、upsert 和关系解析
  init_db.py                                    PostgreSQL 兼容列迁移和 seed 顺序

frontend/
  app/literatures/page.tsx                      服务端首屏筛选和 LiteratureBrowser
  app/literatures/[id]/page.tsx                 中文导读、核心结论和证据链
  app/databases/tutorials/[id]/page.tsx          展示反向关联论文
  components/RelatedResources.tsx               支持数据库教程卡片
  lib/databaseApi.ts                            获取教程关联论文
  lib/databaseTypes.ts                          教程关系 DTO

docs/
  DATABASE_AND_SEED.md                          Literature seed 与关系表说明
  FRONTEND_GUIDE.md                             文献列表和详情页使用说明
  ROADMAP.md                                    标记轻量证据中心能力
```

## Task 1: 扩展 Literature 模型、Schema 和 PostgreSQL 兼容迁移

**Files:**
- Create: `backend/app/models/literature_link.py`
- Create: `backend/tests/test_literature_model.py`
- Modify: `backend/app/models/literature.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/schemas/literature.py`
- Modify: `backend/app/main.py`
- Modify: `backend/init_db.py`

- [ ] **Step 1: 编写失败测试**

创建 `backend/tests/test_literature_model.py`：

```python
from datetime import date

from sqlalchemy.orm import Session

from app.models.literature import Literature


def test_literature_defaults_support_public_evidence_metadata(
    db_session: Session,
) -> None:
    literature = Literature(
        title="Example paper",
        authors=["A. Author"],
        journal="Bioinformatics",
        publication_year=2026,
        doi="10.0000/example",
        abstract_text="Example abstract.",
        chinese_summary="示例中文导读。",
        recommendation_reason="用于验证默认字段。",
        topic_key="bulk-rnaseq",
        topic_name="Bulk RNA-seq",
        last_reviewed_at=date(2026, 6, 1),
    )
    db_session.add(literature)
    db_session.commit()
    db_session.refresh(literature)

    assert literature.literature_type == "classic_method"
    assert literature.keywords_json == []
    assert literature.key_findings_json == []
    assert literature.applicable_scenarios_json == []
    assert literature.is_featured is False
    assert literature.created_at is not None
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_model.py -q
```

Expected: FAIL，提示 `Literature` 不接受 `chinese_summary`、`topic_key` 或其他新增字段。

- [ ] **Step 3: 新增关联表模型**

创建 `backend/app/models/literature_link.py`：

```python
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LiteraturePipelineLink(Base):
    __tablename__ = "literature_pipeline_links"

    literature_id: Mapped[int] = mapped_column(
        ForeignKey("literatures.id", ondelete="CASCADE"), primary_key=True
    )
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), primary_key=True
    )


class LiteratureAlgorithmLink(Base):
    __tablename__ = "literature_algorithm_links"

    literature_id: Mapped[int] = mapped_column(
        ForeignKey("literatures.id", ondelete="CASCADE"), primary_key=True
    )
    algorithm_id: Mapped[int] = mapped_column(
        ForeignKey("algorithms.id", ondelete="CASCADE"), primary_key=True
    )


class LiteratureDatabaseTutorialLink(Base):
    __tablename__ = "literature_database_tutorial_links"

    literature_id: Mapped[int] = mapped_column(
        ForeignKey("literatures.id", ondelete="CASCADE"), primary_key=True
    )
    database_tutorial_id: Mapped[int] = mapped_column(
        ForeignKey("database_tutorials.id", ondelete="CASCADE"), primary_key=True
    )
```

- [ ] **Step 4: 扩展 Literature ORM**

在 `backend/app/models/literature.py` 中保留旧 `pipeline_id` 和 `algorithm_id` 列用于平滑迁移，并新增字段与 link relationships：

```python
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.literature_link import (
        LiteratureAlgorithmLink,
        LiteratureDatabaseTutorialLink,
        LiteraturePipelineLink,
    )


class Literature(Base):
    __tablename__ = "literatures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    authors: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    journal: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    doi: Mapped[str | None] = mapped_column(String(160), unique=True, index=True)
    pmid: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    abstract_text: Mapped[str] = mapped_column(Text, nullable=False)
    literature_type: Mapped[str] = mapped_column(
        String(40), nullable=False, index=True, default="classic_method"
    )
    topic_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    topic_name: Mapped[str] = mapped_column(String(120), nullable=False)
    keywords_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    chinese_summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation_reason: Mapped[str] = mapped_column(Text, nullable=False)
    key_findings_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    applicable_scenarios_json: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    published_at: Mapped[date | None] = mapped_column(Date)
    last_reviewed_at: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500))
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    pipeline_id: Mapped[int | None] = mapped_column(
        ForeignKey("pipelines.id"), nullable=True, index=True
    )
    algorithm_id: Mapped[int | None] = mapped_column(
        ForeignKey("algorithms.id"), nullable=True, index=True
    )

    pipeline_links: Mapped[list["LiteraturePipelineLink"]] = relationship(
        cascade="all, delete-orphan"
    )
    algorithm_links: Mapped[list["LiteratureAlgorithmLink"]] = relationship(
        cascade="all, delete-orphan"
    )
    database_tutorial_links: Mapped[list["LiteratureDatabaseTutorialLink"]] = relationship(
        cascade="all, delete-orphan"
    )
```

- [ ] **Step 5: 暴露模型并让应用启动时注册表**

在 `backend/app/models/__init__.py` 中导入并加入 `__all__`：

```python
from app.models.literature_link import (
    LiteratureAlgorithmLink,
    LiteratureDatabaseTutorialLink,
    LiteraturePipelineLink,
)
```

在 `backend/app/main.py` 的模型模块导入中加入：

```python
    literature_link,
```

- [ ] **Step 6: 扩展 Pydantic Schema**

将 `backend/app/schemas/literature.py` 更新为：

```python
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LiteratureBase(BaseModel):
    title: str = Field(..., max_length=500)
    authors: list[str]
    journal: str = Field(..., max_length=180)
    publication_year: int
    doi: str | None = Field(default=None, max_length=160)
    pmid: str | None = Field(default=None, max_length=32)
    abstract_text: str
    literature_type: str = Field(..., max_length=40)
    topic_key: str = Field(..., max_length=80)
    topic_name: str = Field(..., max_length=120)
    keywords_json: list[str] = Field(default_factory=list)
    chinese_summary: str
    recommendation_reason: str
    key_findings_json: list[str] = Field(default_factory=list)
    applicable_scenarios_json: list[str] = Field(default_factory=list)
    published_at: date | None = None
    last_reviewed_at: date
    source_url: str | None = Field(default=None, max_length=500)
    is_featured: bool = False


class LiteratureCreate(LiteratureBase):
    pass


class LiteratureResponse(LiteratureBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LiteratureListItemResponse(LiteratureResponse):
    pipeline_count: int = 0
    algorithm_count: int = 0
    database_tutorial_count: int = 0
```

- [ ] **Step 7: 增加 PostgreSQL 临时兼容迁移**

在 `backend/init_db.py` 的 seed 之前增加 Literature 列迁移，并在顶部显式导入 link 模型：

```python
from app.models import literature_link  # noqa: F401
```

```python
        literature_migrations = [
            "ADD COLUMN IF NOT EXISTS pmid VARCHAR(32)",
            "ADD COLUMN IF NOT EXISTS literature_type VARCHAR(40) NOT NULL DEFAULT 'classic_method'",
            "ADD COLUMN IF NOT EXISTS topic_key VARCHAR(80) NOT NULL DEFAULT 'other'",
            "ADD COLUMN IF NOT EXISTS topic_name VARCHAR(120) NOT NULL DEFAULT '其他主题'",
            "ADD COLUMN IF NOT EXISTS keywords_json JSON NOT NULL DEFAULT '[]'",
            "ADD COLUMN IF NOT EXISTS chinese_summary TEXT NOT NULL DEFAULT ''",
            "ADD COLUMN IF NOT EXISTS recommendation_reason TEXT NOT NULL DEFAULT ''",
            "ADD COLUMN IF NOT EXISTS key_findings_json JSON NOT NULL DEFAULT '[]'",
            "ADD COLUMN IF NOT EXISTS applicable_scenarios_json JSON NOT NULL DEFAULT '[]'",
            "ADD COLUMN IF NOT EXISTS published_at DATE",
            "ADD COLUMN IF NOT EXISTS last_reviewed_at DATE NOT NULL DEFAULT CURRENT_DATE",
            "ADD COLUMN IF NOT EXISTS source_url VARCHAR(500)",
            "ADD COLUMN IF NOT EXISTS is_featured BOOLEAN NOT NULL DEFAULT FALSE",
            "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        ]
        for migration in literature_migrations:
            db.execute(text(f"ALTER TABLE literatures {migration}"))
        db.execute(text("ALTER TABLE literatures ALTER COLUMN doi DROP NOT NULL"))
```

- [ ] **Step 8: 运行专项测试**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_model.py -q
```

Expected: PASS。

- [ ] **Step 9: 提交**

```powershell
git add backend/app/models/literature.py backend/app/models/literature_link.py backend/app/models/__init__.py backend/app/schemas/literature.py backend/app/main.py backend/init_db.py backend/tests/test_literature_model.py
git commit -m "feat: add literature evidence metadata models"
```

## Task 2: 建立 Literature 多对多关系查询

**Files:**
- Create: `backend/tests/test_literature_relations.py`
- Modify: `backend/app/schemas/relation.py`
- Modify: `backend/app/repositories/relation_repository.py`
- Modify: `backend/app/services/relation_service.py`
- Modify: `backend/app/api/v1/controllers/database_controller.py`

- [ ] **Step 1: 编写失败测试**

创建 `backend/tests/test_literature_relations.py`。使用辅助函数创建一个流程、一个软件、一个数据库教程、一篇论文和三条 link：

```python
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Algorithm,
    DatabaseResource,
    DatabaseTutorial,
    Literature,
    LiteratureAlgorithmLink,
    LiteratureDatabaseTutorialLink,
    LiteraturePipelineLink,
    Pipeline,
)


def seed_linked_literature(db_session: Session) -> tuple[Pipeline, Algorithm, DatabaseTutorial, Literature]:
    pipeline = Pipeline(
        title="Bulk RNA-seq 分析",
        description="从 FASTQ 到 DEG。",
        omics_type="RNA-Seq",
        category_key="basic",
        category_name="基础分析",
        dag_json={"nodes": []},
        metadata_json={"tools": ["DESeq2"]},
        content="# RNA-seq",
    )
    algorithm = Algorithm(
        name="DESeq2",
        category="Differential expression",
        category_key="differential-expression",
        category_name="差异表达",
        tool_type="R 包",
        summary="RNA-seq 差异表达。",
        performance_json={},
        metadata_json={},
        markdown_docs="# DESeq2",
    )
    resource = DatabaseResource(
        slug="geo",
        name="GEO",
        full_name="Gene Expression Omnibus",
        category_key="expression",
        category_name="表达数据",
        description="公共表达数据。",
        use_cases_json=[],
        data_types_json=["RNA-seq"],
        species_json=["Human"],
        tags_json=[],
        url="https://www.ncbi.nlm.nih.gov/geo/",
        region="USA",
        rating=5,
    )
    tutorial = DatabaseTutorial(
        slug="geo-expression-search",
        title="GEO 表达矩阵检索",
        scenario="查找公开 RNA-seq 数据。",
        steps_json=["输入关键词"],
        entry_url="https://www.ncbi.nlm.nih.gov/geo/",
        content="# GEO",
    )
    resource.tutorials.append(tutorial)
    literature = Literature(
        title="Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2",
        authors=["Michael I. Love"],
        journal="Genome Biology",
        publication_year=2014,
        doi="10.1186/s13059-014-0550-8",
        abstract_text="DESeq2 paper.",
        chinese_summary="DESeq2 经典方法论文。",
        recommendation_reason="理解差异分析统计模型。",
        literature_type="classic_method",
        topic_key="bulk-rnaseq",
        topic_name="Bulk RNA-seq",
        keywords_json=["DESeq2"],
        last_reviewed_at=date(2026, 6, 1),
    )
    db_session.add_all([pipeline, algorithm, resource, literature])
    db_session.flush()
    db_session.add_all(
        [
            LiteraturePipelineLink(literature_id=literature.id, pipeline_id=pipeline.id),
            LiteratureAlgorithmLink(literature_id=literature.id, algorithm_id=algorithm.id),
            LiteratureDatabaseTutorialLink(
                literature_id=literature.id,
                database_tutorial_id=tutorial.id,
            ),
        ]
    )
    db_session.commit()
    return pipeline, algorithm, tutorial, literature


def test_literature_relations_return_all_resource_types(
    client: TestClient, db_session: Session
) -> None:
    _, _, _, literature = seed_linked_literature(db_session)

    response = client.get(f"/api/literatures/{literature.id}/relations")

    assert response.status_code == 200
    assert response.json()["pipelines"][0]["title"] == "Bulk RNA-seq 分析"
    assert response.json()["algorithms"][0]["name"] == "DESeq2"
    assert response.json()["database_tutorials"][0]["slug"] == "geo-expression-search"


def test_database_tutorial_relations_return_literatures(
    client: TestClient, db_session: Session
) -> None:
    _, _, tutorial, _ = seed_linked_literature(db_session)

    response = client.get(f"/api/databases/tutorials/{tutorial.slug}/relations")

    assert response.status_code == 200
    assert response.json()["literatures"][0]["doi"] == "10.1186/s13059-014-0550-8"


def test_pipeline_and_algorithm_relations_use_link_tables(
    client: TestClient, db_session: Session
) -> None:
    pipeline, algorithm, _, _ = seed_linked_literature(db_session)

    pipeline_response = client.get(f"/api/pipelines/{pipeline.id}/relations")
    algorithm_response = client.get(f"/api/algorithms/{algorithm.id}/relations")

    assert pipeline_response.status_code == 200
    assert pipeline_response.json()["literatures"][0]["doi"] == "10.1186/s13059-014-0550-8"
    assert algorithm_response.status_code == 200
    assert algorithm_response.json()["literatures"][0]["doi"] == "10.1186/s13059-014-0550-8"
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_relations.py -q
```

Expected: FAIL，旧 `LiteratureRelationsResponse` 没有数组字段，且数据库教程 relations 路由不存在。

- [ ] **Step 3: 扩展关系 Schema**

在 `backend/app/schemas/relation.py` 中增加：

```python
class RelatedDatabaseTutorial(BaseModel):
    slug: str
    title: str
    scenario: str

    model_config = ConfigDict(from_attributes=True)


class LiteratureRelationsResponse(BaseModel):
    literature_id: int
    pipelines: list[RelatedPipeline]
    algorithms: list[RelatedAlgorithm]
    database_tutorials: list[RelatedDatabaseTutorial]


class DatabaseTutorialRelationsResponse(BaseModel):
    tutorial_slug: str
    literatures: list[RelatedLiterature]
```

删除旧版 `LiteratureRelationsResponse.pipeline` 与 `LiteratureRelationsResponse.algorithm`。
同时将 `RelatedLiterature.doi` 改为 `str | None`，确保只有 PMID 的记录也能进入反向关系响应。

- [ ] **Step 4: 改造 RelationRepository**

在 `backend/app/repositories/relation_repository.py` 导入 link 模型和 `DatabaseTutorial`，将文献关系查询改为关联表查询：

```python
    def get_database_tutorial_by_slug(self, slug: str) -> DatabaseTutorial | None:
        return self.db.scalar(select(DatabaseTutorial).where(DatabaseTutorial.slug == slug))

    def list_literatures_for_pipeline(self, pipeline_id: int) -> list[Literature]:
        statement = (
            select(Literature)
            .join(
                LiteraturePipelineLink,
                LiteraturePipelineLink.literature_id == Literature.id,
            )
            .where(LiteraturePipelineLink.pipeline_id == pipeline_id)
            .order_by(Literature.publication_year.desc(), Literature.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_literatures_for_algorithm(self, algorithm_id: int) -> list[Literature]:
        statement = (
            select(Literature)
            .join(
                LiteratureAlgorithmLink,
                LiteratureAlgorithmLink.literature_id == Literature.id,
            )
            .where(LiteratureAlgorithmLink.algorithm_id == algorithm_id)
            .order_by(Literature.publication_year.desc(), Literature.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_pipelines_for_literature(self, literature_id: int) -> list[Pipeline]:
        statement = (
            select(Pipeline)
            .join(LiteraturePipelineLink, LiteraturePipelineLink.pipeline_id == Pipeline.id)
            .where(LiteraturePipelineLink.literature_id == literature_id)
            .order_by(Pipeline.id)
        )
        return list(self.db.scalars(statement).all())

    def list_algorithms_for_literature(self, literature_id: int) -> list[Algorithm]:
        statement = (
            select(Algorithm)
            .join(
                LiteratureAlgorithmLink,
                LiteratureAlgorithmLink.algorithm_id == Algorithm.id,
            )
            .where(LiteratureAlgorithmLink.literature_id == literature_id)
            .order_by(Algorithm.id)
        )
        return list(self.db.scalars(statement).all())

    def list_database_tutorials_for_literature(
        self, literature_id: int
    ) -> list[DatabaseTutorial]:
        statement = (
            select(DatabaseTutorial)
            .join(
                LiteratureDatabaseTutorialLink,
                LiteratureDatabaseTutorialLink.database_tutorial_id == DatabaseTutorial.id,
            )
            .where(LiteratureDatabaseTutorialLink.literature_id == literature_id)
            .order_by(DatabaseTutorial.id)
        )
        return list(self.db.scalars(statement).all())

    def list_literatures_for_database_tutorial(
        self, database_tutorial_id: int
    ) -> list[Literature]:
        statement = (
            select(Literature)
            .join(
                LiteratureDatabaseTutorialLink,
                LiteratureDatabaseTutorialLink.literature_id == Literature.id,
            )
            .where(
                LiteratureDatabaseTutorialLink.database_tutorial_id
                == database_tutorial_id
            )
            .order_by(Literature.publication_year.desc(), Literature.id.desc())
        )
        return list(self.db.scalars(statement).all())
```

在现有 `list_algorithms_for_pipeline()` 和 `list_pipelines_for_algorithm()` 中，将显式关系 join 改为通过 Literature link 表连接，保留已有 metadata tools 匹配逻辑：

```python
        explicit_statement = (
            select(Algorithm)
            .join(
                LiteratureAlgorithmLink,
                LiteratureAlgorithmLink.algorithm_id == Algorithm.id,
            )
            .join(
                LiteraturePipelineLink,
                LiteraturePipelineLink.literature_id
                == LiteratureAlgorithmLink.literature_id,
            )
            .where(LiteraturePipelineLink.pipeline_id == pipeline.id)
        )
```

```python
        explicit_statement = (
            select(Pipeline)
            .join(
                LiteraturePipelineLink,
                LiteraturePipelineLink.pipeline_id == Pipeline.id,
            )
            .join(
                LiteratureAlgorithmLink,
                LiteratureAlgorithmLink.literature_id
                == LiteraturePipelineLink.literature_id,
            )
            .where(LiteratureAlgorithmLink.algorithm_id == algorithm.id)
        )
```

- [ ] **Step 5: 改造 RelationService**

在 `backend/app/services/relation_service.py` 中替换 Literature 详情关系，并增加数据库教程反向关系：

```python
    def get_literature_relations(self, literature_id: int) -> dict[str, object]:
        literature = self.repository.get_literature(literature_id)
        if literature is None:
            raise HTTPException(status_code=404, detail="Literature 不存在")

        return {
            "literature_id": literature.id,
            "pipelines": self.repository.list_pipelines_for_literature(literature.id),
            "algorithms": self.repository.list_algorithms_for_literature(literature.id),
            "database_tutorials": (
                self.repository.list_database_tutorials_for_literature(literature.id)
            ),
        }

    def get_database_tutorial_relations(self, tutorial_slug: str) -> dict[str, object]:
        tutorial = self.repository.get_database_tutorial_by_slug(tutorial_slug)
        if tutorial is None:
            raise HTTPException(status_code=404, detail="数据库教程不存在")

        return {
            "tutorial_slug": tutorial.slug,
            "literatures": self.repository.list_literatures_for_database_tutorial(
                tutorial.id
            ),
        }
```

- [ ] **Step 6: 增加数据库教程关系接口**

在 `backend/app/api/v1/controllers/database_controller.py` 中增加：

```python
from app.schemas.relation import DatabaseTutorialRelationsResponse
from app.services.relation_service import RelationService


@router.get(
    "/tutorials/{tutorial_slug}/relations",
    response_model=DatabaseTutorialRelationsResponse,
    summary="获取数据库教程关联文献",
)
def get_database_tutorial_relations(
    tutorial_slug: str, db: Session = Depends(get_db)
) -> dict[str, object]:
    service = RelationService(db)
    return service.get_database_tutorial_relations(tutorial_slug)
```

将该路由放在 `"/tutorials/{tutorial_slug}"` 详情路由之前，避免可读性混乱。

- [ ] **Step 7: 运行专项测试**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_relations.py -q
```

Expected: PASS。

- [ ] **Step 8: 提交**

```powershell
git add backend/app/schemas/relation.py backend/app/repositories/relation_repository.py backend/app/services/relation_service.py backend/app/api/v1/controllers/database_controller.py backend/tests/test_literature_relations.py
git commit -m "feat: add literature evidence relations"
```

## Task 3: 拆分并扩充人工精选 Literature seed

**Files:**
- Create: `backend/app/seed_data/literature_records/core_methods.json`
- Create: `backend/app/seed_data/literature_records/reviews_guides.json`
- Create: `backend/app/seed_data/literature_records/frontier_research.json`
- Create: `backend/tests/test_literature_seed.py`
- Modify: `backend/app/seed_data/literatures.py`
- Modify: `backend/init_db.py`

- [ ] **Step 1: 编写失败测试**

创建 `backend/tests/test_literature_seed.py`：

```python
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Algorithm,
    Literature,
    LiteratureAlgorithmLink,
    LiteratureDatabaseTutorialLink,
    LiteraturePipelineLink,
    Pipeline,
)
from app.seed_data.algorithms import seed_algorithms
from app.seed_data.database_tutorials import seed_database_tutorials
from app.seed_data.databases import seed_databases
from app.seed_data.literatures import seed_literatures
from app.seed_data.pipelines import seed_pipelines


def seed_dependencies(db_session: Session) -> None:
    seed_pipelines(db_session)
    seed_algorithms(db_session)
    seed_databases(db_session)
    seed_database_tutorials(db_session)


def test_literature_seed_is_idempotent_and_curated(db_session: Session) -> None:
    seed_dependencies(db_session)
    seed_literatures(db_session)
    first_count = db_session.scalar(select(func.count(Literature.id)))

    seed_literatures(db_session)
    second_count = db_session.scalar(select(func.count(Literature.id)))

    assert first_count is not None
    assert first_count >= 20
    assert second_count == first_count


def test_literature_seed_exposes_all_public_types(db_session: Session) -> None:
    seed_dependencies(db_session)
    seed_literatures(db_session)

    literature_types = set(db_session.scalars(select(Literature.literature_type)).all())

    assert literature_types == {"classic_method", "review_guide", "frontier_research"}


def test_literature_seed_resolves_cross_module_links(db_session: Session) -> None:
    seed_dependencies(db_session)
    seed_literatures(db_session)

    assert db_session.scalar(select(func.count(LiteraturePipelineLink.literature_id))) > 0
    assert db_session.scalar(select(func.count(LiteratureAlgorithmLink.literature_id))) > 0
    assert (
        db_session.scalar(
            select(func.count(LiteratureDatabaseTutorialLink.literature_id))
        )
        > 0
    )


def test_literature_seed_migrates_legacy_foreign_keys(db_session: Session) -> None:
    seed_dependencies(db_session)
    pipeline = db_session.scalar(select(Pipeline).limit(1))
    algorithm = db_session.scalar(select(Algorithm).limit(1))
    assert pipeline is not None
    assert algorithm is not None
    legacy = Literature(
        title="Legacy curated record",
        authors=["A. Author"],
        journal="Bioinformatics",
        publication_year=2020,
        doi="10.0000/legacy-record",
        abstract_text="Legacy record.",
        chinese_summary="旧版精选文献。",
        recommendation_reason="验证平滑迁移。",
        topic_key="other",
        topic_name="其他主题",
        last_reviewed_at=date(2026, 6, 1),
        pipeline_id=pipeline.id,
        algorithm_id=algorithm.id,
    )
    db_session.add(legacy)
    db_session.commit()

    seed_literatures(db_session)

    assert db_session.get(LiteraturePipelineLink, (legacy.id, pipeline.id)) is not None
    assert db_session.get(LiteratureAlgorithmLink, (legacy.id, algorithm.id)) is not None
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_seed.py -q
```

Expected: FAIL，现有 seed 只有 3 篇，且没有三个公开类型与 link 表解析。

- [ ] **Step 3: 建立 JSON seed 格式**

在三个 JSON 文件中使用相同结构。每个文件的顶层为数组，每条记录使用：

```json
{
  "title": "Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2",
  "authors": ["Michael I. Love", "Wolfgang Huber", "Simon Anders"],
  "journal": "Genome Biology",
  "publication_year": 2014,
  "doi": "10.1186/s13059-014-0550-8",
  "pmid": "25516281",
  "abstract_text": "DESeq2 provides methods to test for differential expression by use of negative binomial generalized linear models.",
  "literature_type": "classic_method",
  "topic_key": "bulk-rnaseq",
  "topic_name": "Bulk RNA-seq",
  "keywords_json": ["DESeq2", "differential expression", "RNA-seq"],
  "chinese_summary": "这篇论文介绍 DESeq2 的差异表达统计框架，重点解决 RNA-seq 计数数据的离散度估计、效应量判断和多重检验问题。",
  "recommendation_reason": "用于理解为什么差异表达分析必须使用原始 count 建模，以及如何解释 log2FoldChange、pvalue 和 padj。",
  "key_findings_json": [
    "使用负二项广义线性模型分析 RNA-seq count。",
    "通过 shrinkage 提升离散度和 fold change 估计稳定性。"
  ],
  "applicable_scenarios_json": ["Bulk RNA-seq 差异表达", "多因素实验设计"],
  "published_at": "2014-12-05",
  "last_reviewed_at": "2026-06-01",
  "source_url": "https://doi.org/10.1186/s13059-014-0550-8",
  "is_featured": true,
  "pipeline_titles": ["Bulk RNA-seq 标准差异表达分析增强版"],
  "algorithm_names": ["DESeq2"],
  "database_tutorial_slugs": []
}
```

- [ ] **Step 4: 人工核验并录入首批内容**

使用 DOI 官方落地页或 PubMed 页面核验 `title`、`authors`、`journal`、`publication_year`、`doi`、`pmid` 和 `source_url`。三个文件合计录入至少 `20` 篇：

| 文件 | 最低数量 | 必须覆盖 |
| --- | --- | --- |
| `core_methods.json` | 12 | BWA、STAR、Salmon、featureCounts、DESeq2、Seurat、Cell Ranger、WGCNA、rMATS、STAR-Fusion、Trinity、CUT&Tag |
| `reviews_guides.json` | 4 | Bulk RNA-seq、单细胞、空间转录组、变异检测 |
| `frontier_research.json` | 4 | Seurat v5、多模态单细胞、空间转录组、长读长转录组 |

录入约束：

- 每条必须有 DOI 或 PMID。
- 每条必须有中文导读、推荐理由、至少一条核心结论和至少一个适用场景。
- 每条至少关联一个当前平台中已存在的流程、软件或教程。
- 所有 `pipeline_titles`、`algorithm_names` 和 `database_tutorial_slugs` 必须与 seed 中的稳定业务键完全一致。
- 不复制论文全文，不在 seed 中粘贴长篇受版权保护内容。

- [ ] **Step 5: 将 literatures.py 改为 JSON loader 和关系解析器**

保留公开入口 `seed_literatures(db: Session) -> None`，增加：

```python
import json
import warnings
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.models import (
    Algorithm,
    DatabaseTutorial,
    Literature,
    LiteratureAlgorithmLink,
    LiteratureDatabaseTutorialLink,
    LiteraturePipelineLink,
    Pipeline,
)

SEED_DIR = Path(__file__).with_name("literature_records")
SEED_FILES = (
    "core_methods.json",
    "reviews_guides.json",
    "frontier_research.json",
)


def load_literature_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for filename in SEED_FILES:
        with (SEED_DIR / filename).open(encoding="utf-8") as seed_file:
            records.extend(json.load(seed_file))
    return records


def _find_literature(db: Session, item: dict[str, Any]) -> Literature | None:
    doi = item.get("doi")
    pmid = item.get("pmid")
    if not doi and not pmid:
        raise ValueError("Literature seed requires DOI or PMID.")
    clauses = []
    if doi:
        clauses.append(Literature.doi == doi)
    if pmid:
        clauses.append(Literature.pmid == pmid)
    return db.scalar(select(Literature).where(or_(*clauses)))


LITERATURE_FIELDS = (
    "title",
    "authors",
    "journal",
    "publication_year",
    "doi",
    "pmid",
    "abstract_text",
    "literature_type",
    "topic_key",
    "topic_name",
    "keywords_json",
    "chinese_summary",
    "recommendation_reason",
    "key_findings_json",
    "applicable_scenarios_json",
    "source_url",
    "is_featured",
)


def _values_for_literature(item: dict[str, Any]) -> dict[str, Any]:
    values = {field: item.get(field) for field in LITERATURE_FIELDS}
    values["published_at"] = (
        date.fromisoformat(item["published_at"]) if item.get("published_at") else None
    )
    values["last_reviewed_at"] = date.fromisoformat(item["last_reviewed_at"])
    return values


def _warn_missing(kind: str, key: str) -> None:
    warnings.warn(f"Skipping missing literature relation: {kind}={key}", stacklevel=2)


def _replace_links(db: Session, literature: Literature, item: dict[str, Any]) -> None:
    db.execute(
        delete(LiteraturePipelineLink).where(
            LiteraturePipelineLink.literature_id == literature.id
        )
    )
    db.execute(
        delete(LiteratureAlgorithmLink).where(
            LiteratureAlgorithmLink.literature_id == literature.id
        )
    )
    db.execute(
        delete(LiteratureDatabaseTutorialLink).where(
            LiteratureDatabaseTutorialLink.literature_id == literature.id
        )
    )

    for title in item.get("pipeline_titles", []):
        pipeline = db.scalar(select(Pipeline).where(Pipeline.title == title))
        if pipeline is None:
            _warn_missing("pipeline", title)
            continue
        db.add(LiteraturePipelineLink(literature_id=literature.id, pipeline_id=pipeline.id))

    for name in item.get("algorithm_names", []):
        algorithm = db.scalar(select(Algorithm).where(Algorithm.name == name))
        if algorithm is None:
            _warn_missing("algorithm", name)
            continue
        db.add(
            LiteratureAlgorithmLink(
                literature_id=literature.id,
                algorithm_id=algorithm.id,
            )
        )

    for slug in item.get("database_tutorial_slugs", []):
        tutorial = db.scalar(
            select(DatabaseTutorial).where(DatabaseTutorial.slug == slug)
        )
        if tutorial is None:
            _warn_missing("database_tutorial", slug)
            continue
        db.add(
            LiteratureDatabaseTutorialLink(
                literature_id=literature.id,
                database_tutorial_id=tutorial.id,
            )
        )


def _migrate_legacy_links(db: Session) -> None:
    for literature in db.scalars(select(Literature)).all():
        if (
            literature.pipeline_id is not None
            and db.get(
                LiteraturePipelineLink,
                (literature.id, literature.pipeline_id),
            )
            is None
        ):
            db.add(
                LiteraturePipelineLink(
                    literature_id=literature.id,
                    pipeline_id=literature.pipeline_id,
                )
            )
        if (
            literature.algorithm_id is not None
            and db.get(
                LiteratureAlgorithmLink,
                (literature.id, literature.algorithm_id),
            )
            is None
        ):
            db.add(
                LiteratureAlgorithmLink(
                    literature_id=literature.id,
                    algorithm_id=literature.algorithm_id,
                )
            )


def seed_literatures(db: Session) -> None:
    for item in load_literature_records():
        literature = _find_literature(db, item)
        values = _values_for_literature(item)
        if literature is None:
            literature = Literature(**values)
            db.add(literature)
            db.flush()
        else:
            for key, value in values.items():
                setattr(literature, key, value)
        _replace_links(db, literature, item)

    _migrate_legacy_links(db)
    db.commit()
```

旧版 `build_mock_literatures()` 删除。上面的 loader 只将 Literature ORM 字段写入主表；关系配置只用于解析 link。目标键不存在时输出具体键名并跳过该 link。`_migrate_legacy_links()` 负责保留不在 JSON seed 中的旧记录关联。

- [ ] **Step 6: 调整 init_db seed 顺序**

将 `backend/init_db.py` 的调用顺序改为：

```python
        seed_pipelines(db)
        seed_algorithms(db)
        seed_databases(db)
        seed_database_tutorials(db)
        seed_literatures(db)
```

- [ ] **Step 7: 运行专项测试和内容安全扫描**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_seed.py -q
docker compose run --rm --no-deps backend python scripts/scan_public_content.py
```

Expected: seed 测试 PASS，扫描输出 `Public content safety scan passed.`。

- [ ] **Step 8: 提交**

```powershell
git add backend/app/seed_data/literatures.py backend/app/seed_data/literature_records backend/init_db.py backend/tests/test_literature_seed.py
git commit -m "feat: seed curated literature evidence records"
```

## Task 4: 为 Literature 列表接口增加搜索、筛选、排序和关联计数

**Files:**
- Create: `backend/tests/test_literature_api.py`
- Modify: `backend/app/repositories/literature_repository.py`
- Modify: `backend/app/services/literature_service.py`
- Modify: `backend/app/api/v1/controllers/literature_controller.py`

- [ ] **Step 1: 编写失败测试**

创建 `backend/tests/test_literature_api.py`。文件内复用 Task 2 的真实关系 helper，并定义：

```python
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Literature
from test_literature_relations import seed_linked_literature


def seed_literature_api_records(db_session: Session) -> None:
    _, algorithm, _, frontier = seed_linked_literature(db_session)
    algorithm.name = "Seurat v5"
    frontier.title = "Dictionary learning for integrative, multimodal and scalable single-cell analysis"
    frontier.doi = "10.1038/s41587-023-01767-y"
    frontier.pmid = "37088945"
    frontier.journal = "Nature Biotechnology"
    frontier.publication_year = 2024
    frontier.literature_type = "frontier_research"
    frontier.topic_key = "single-cell"
    frontier.topic_name = "单细胞分析"
    frontier.keywords_json = ["Seurat", "single-cell", "multimodal"]
    frontier.chinese_summary = "Seurat v5 多模态单细胞整合研究。"
    frontier.is_featured = True

    db_session.add_all(
        [
            Literature(
                title="Classic RNA-seq method",
                authors=["A. Author"],
                journal="Bioinformatics",
                publication_year=2014,
                doi="10.0000/classic-rnaseq",
                abstract_text="Classic method.",
                literature_type="classic_method",
                topic_key="bulk-rnaseq",
                topic_name="Bulk RNA-seq",
                keywords_json=["RNA-seq"],
                chinese_summary="经典 RNA-seq 方法。",
                recommendation_reason="用于测试排序。",
                last_reviewed_at=date(2026, 6, 1),
            ),
            Literature(
                title="Variant calling review",
                authors=["B. Author"],
                journal="Genome Biology",
                publication_year=2020,
                doi="10.0000/variant-review",
                abstract_text="Variant review.",
                literature_type="review_guide",
                topic_key="variant",
                topic_name="变异检测",
                keywords_json=["variant"],
                chinese_summary="变异检测综述。",
                recommendation_reason="用于测试筛选。",
                last_reviewed_at=date(2026, 6, 1),
            ),
        ]
    )
    db_session.commit()
```

随后增加：

```python
def test_list_literatures_filters_keyword_topic_type_year_and_links(
    client: TestClient, db_session: Session
) -> None:
    seed_literature_api_records(db_session)

    response = client.get(
        "/api/literatures"
        "?keyword=Seurat"
        "&topic_key=single-cell"
        "&literature_type=frontier_research"
        "&publication_year=2024"
        "&linked_only=true"
    )

    assert response.status_code == 200
    assert [item["doi"] for item in response.json()] == [
        "10.1038/s41587-023-01767-y"
    ]
    assert response.json()[0]["pipeline_count"] == 1
    assert response.json()[0]["algorithm_count"] == 1


def test_list_literatures_orders_featured_items_first(
    client: TestClient, db_session: Session
) -> None:
    seed_literature_api_records(db_session)

    response = client.get("/api/literatures")

    assert response.status_code == 200
    assert response.json()[0]["is_featured"] is True


def test_list_literatures_rejects_invalid_limit(client: TestClient) -> None:
    response = client.get("/api/literatures?limit=201")

    assert response.status_code == 422
    assert response.json()["message"] == "请求参数校验失败"
```

helper 中的 Seurat 文献必须通过 `LiteraturePipelineLink` 和 `LiteratureAlgorithmLink` 建立真实关系，不使用 mock。

- [ ] **Step 2: 运行测试并确认失败**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_api.py -q
```

Expected: FAIL，旧接口不接受筛选参数，也不返回关联计数。

- [ ] **Step 3: 扩展 Repository**

在 `backend/app/repositories/literature_repository.py` 中使用 `selectinload()` 一次性加载三类 link：

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.literature import Literature


class LiteratureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_literatures(
        self,
        keyword: str | None = None,
        literature_type: str | None = None,
        topic_key: str | None = None,
        publication_year: int | None = None,
        linked_only: bool = False,
        limit: int = 100,
    ) -> list[Literature]:
        statement = (
            select(Literature)
            .options(
                selectinload(Literature.pipeline_links),
                selectinload(Literature.algorithm_links),
                selectinload(Literature.database_tutorial_links),
            )
            .order_by(
                Literature.is_featured.desc(),
                Literature.publication_year.desc(),
                Literature.id.desc(),
            )
        )
        if literature_type:
            statement = statement.where(Literature.literature_type == literature_type)
        if topic_key:
            statement = statement.where(Literature.topic_key == topic_key)
        if publication_year is not None:
            statement = statement.where(Literature.publication_year == publication_year)

        items = list(self.db.scalars(statement).all())
        items = [
            item
            for item in items
            if self._matches_keyword(item, keyword)
            and (not linked_only or self._has_links(item))
        ]
        return items[:limit]

    def get_literature_by_id(self, literature_id: int) -> Literature | None:
        return self.db.get(Literature, literature_id)

    def _matches_keyword(self, literature: Literature, keyword: str | None) -> bool:
        if not keyword:
            return True
        normalized = keyword.strip().lower()
        values = [
            literature.title,
            *literature.authors,
            literature.journal,
            literature.doi or "",
            literature.pmid or "",
            literature.topic_name,
            literature.chinese_summary,
            literature.recommendation_reason,
            *literature.keywords_json,
        ]
        return normalized in " ".join(values).lower()

    def _has_links(self, literature: Literature) -> bool:
        return bool(
            literature.pipeline_links
            or literature.algorithm_links
            or literature.database_tutorial_links
        )
```

- [ ] **Step 4: 扩展 Service**

在 `backend/app/services/literature_service.py` 中让列表返回轻量关联计数：

```python
from app.schemas.literature import LiteratureListItemResponse


    def list_literatures(
        self,
        keyword: str | None = None,
        literature_type: str | None = None,
        topic_key: str | None = None,
        publication_year: int | None = None,
        linked_only: bool = False,
        limit: int = 100,
    ) -> list[LiteratureListItemResponse]:
        items = self.repository.list_literatures(
            keyword=keyword,
            literature_type=literature_type,
            topic_key=topic_key,
            publication_year=publication_year,
            linked_only=linked_only,
            limit=limit,
        )
        return [
            LiteratureListItemResponse.model_validate(item).model_copy(
                update={
                    "pipeline_count": len(item.pipeline_links),
                    "algorithm_count": len(item.algorithm_links),
                    "database_tutorial_count": len(item.database_tutorial_links),
                }
            )
            for item in items
        ]
```

- [ ] **Step 5: 扩展 Controller**

在 `backend/app/api/v1/controllers/literature_controller.py` 中增加 Query 参数，并将列表响应模型改为 `list[LiteratureListItemResponse]`：

```python
def list_literatures(
    keyword: str | None = Query(default=None, description="搜索标题、作者、DOI、PMID、导读或关键词"),
    literature_type: str | None = Query(default=None, description="按文献类型筛选"),
    topic_key: str | None = Query(default=None, description="按主题筛选"),
    publication_year: int | None = Query(default=None, ge=1900, le=2100, description="按发表年份筛选"),
    linked_only: bool = Query(default=False, description="仅显示已关联平台资源的文献"),
    limit: int = Query(default=100, ge=1, le=200, description="返回数量上限"),
    db: Session = Depends(get_db),
) -> list[LiteratureListItemResponse]:
    service = LiteratureService(db)
    return service.list_literatures(
        keyword=keyword,
        literature_type=literature_type,
        topic_key=topic_key,
        publication_year=publication_year,
        linked_only=linked_only,
        limit=limit,
    )
```

- [ ] **Step 6: 运行专项测试**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_literature_api.py -q
```

Expected: PASS。

- [ ] **Step 7: 提交**

```powershell
git add backend/app/repositories/literature_repository.py backend/app/services/literature_service.py backend/app/api/v1/controllers/literature_controller.py backend/tests/test_literature_api.py
git commit -m "feat: add literature search and filters"
```

## Task 5: 升级 Literature 列表页

**Files:**
- Create: `frontend/lib/literatureTypes.ts`
- Create: `frontend/components/LiteratureBrowser.tsx`
- Modify: `frontend/app/literatures/page.tsx`

- [ ] **Step 1: 建立前端类型**

创建 `frontend/lib/literatureTypes.ts`：

```typescript
export type LiteratureType =
  | "classic_method"
  | "review_guide"
  | "frontier_research";

export interface LiteratureListItem {
  id: number;
  title: string;
  authors: string[];
  journal: string;
  publication_year: number;
  doi: string | null;
  pmid: string | null;
  literature_type: LiteratureType;
  topic_key: string;
  topic_name: string;
  keywords_json: string[];
  chinese_summary: string;
  recommendation_reason: string;
  key_findings_json: string[];
  applicable_scenarios_json: string[];
  published_at: string | null;
  last_reviewed_at: string;
  source_url: string | null;
  is_featured: boolean;
  created_at: string;
  pipeline_count: number;
  algorithm_count: number;
  database_tutorial_count: number;
}

export interface LiteratureFilters {
  keyword: string;
  literature_type: string;
  topic_key: string;
  publication_year: string;
  linked_only: boolean;
}
```

- [ ] **Step 2: 创建 LiteratureBrowser**

创建 `frontend/components/LiteratureBrowser.tsx`，沿用 `PipelineBrowser` 的 URL 同步模式，并明确修复此前列表请求失败时清空首屏数据的问题：

```typescript
"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState, useTransition } from "react";

import type {
  LiteratureFilters,
  LiteratureListItem,
  LiteratureType
} from "@/lib/literatureTypes";

const CLIENT_API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL ?? "http://localhost:8000";

const defaultFilters: LiteratureFilters = {
  keyword: "",
  literature_type: "",
  topic_key: "",
  publication_year: "",
  linked_only: false
};

const typeLabels: Record<LiteratureType, string> = {
  classic_method: "经典方法",
  review_guide: "综述指南",
  frontier_research: "前沿研究"
};
```

组件必须实现：

- `filtersFromSearchParams()`：读取 `keyword`、`literature_type`、`topic_key`、`publication_year` 和 `linked_only=1`。
- `buildBackendQuery()`：将 `linked_only` 转换为布尔查询参数并设置 `limit=200`。
- `fetchFilteredLiteratures()`：非 `2xx` 时抛出 `Error`。
- `useEffect()`：请求失败时只设置 `errorMessage`，保留 `serverLiteratures` 的上一次有效结果。
- `pushFilters()`：使用 `router.replace()` 更新 URL，不滚动页面。
- 类型、主题、年份下拉框和“仅看已关联”复选框。
- 卡片展示类型标签、主题、期刊、年份、中文导读、关键词、三类关联数量和 DOI 外链。
- 每张卡片使用 `<article>` 容器，标题使用内部 `<Link>`；存在 DOI 时展示独立 DOI `<a>`，没有 DOI 时展示独立 PubMed `<a>`，避免嵌套链接。
- 加载中、失败提示、无数据和无匹配四种状态。

- [ ] **Step 3: 改造服务端 Literature 页面**

将 `frontend/app/literatures/page.tsx` 改为服务端首屏查询：

```typescript
import LiteratureBrowser from "@/components/LiteratureBrowser";
import PageHeader from "@/components/PageHeader";
import type {
  LiteratureFilters,
  LiteratureListItem
} from "@/lib/literatureTypes";

interface LiteraturesPageProps {
  searchParams?: Record<string, string | string[] | undefined>;
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";
```

实现 `getInitialFilters()`、`buildLiteratureQuery()` 和 `fetchLiteratures()`，并行获取 filtered 与 all：

```typescript
  const [literatures, allLiteratures] = await Promise.all([
    fetchLiteratures(filters),
    fetchLiteratures()
  ]);
```

页面头部 stats 使用：

```typescript
stats={[
  { label: "papers", value: allLiteratures.length },
  { label: "matched", value: literatures.length }
]}
```

- [ ] **Step 4: 运行 TypeScript 检查**

Run:

```powershell
docker compose run --rm --no-deps frontend npx tsc --noEmit
git restore --source=HEAD -- frontend/tsconfig.tsbuildinfo
```

Expected: PASS。

- [ ] **Step 5: 提交**

```powershell
git add frontend/lib/literatureTypes.ts frontend/components/LiteratureBrowser.tsx frontend/app/literatures/page.tsx
git commit -m "feat: add literature browsing experience"
```

## Task 6: 升级 Literature 详情页证据链

**Files:**
- Modify: `frontend/app/literatures/[id]/page.tsx`
- Modify: `frontend/components/RelatedResources.tsx`

- [ ] **Step 1: 扩展 RelatedResources**

在 `frontend/components/RelatedResources.tsx` 中增加：

```typescript
export interface RelatedDatabaseTutorial {
  slug: string;
  title: string;
  scenario: string;
}
```

同时将已有 `RelatedLiterature` 调整为：

```typescript
export interface RelatedLiterature {
  id: number;
  title: string;
  journal: string;
  publication_year: number;
  doi: string | null;
}
```

在 props 中增加：

```typescript
  databaseTutorials?: RelatedDatabaseTutorial[];
```

将 `hasResources` 纳入 `databaseTutorials.length > 0`，并渲染教程卡片：

```tsx
{databaseTutorials.map((tutorial) => (
  <Link
    key={`database-tutorial-${tutorial.slug}`}
    href={`/databases/tutorials/${tutorial.slug}`}
    className="block rounded border border-sky-200 bg-sky-50/50 p-4 transition hover:-translate-y-0.5 hover:border-sky-500 hover:bg-white hover:shadow-sm"
  >
    <span className="text-xs font-semibold text-sky-700">数据库教程</span>
    <h3 className="mt-2 text-sm font-semibold leading-6 text-ink">
      {tutorial.title}
    </h3>
    <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-600">
      {tutorial.scenario}
    </p>
  </Link>
))}
```

- [ ] **Step 2: 改造 Literature 详情页类型和关系**

在 `frontend/app/literatures/[id]/page.tsx` 中：

- 使用 `LiteratureListItem` 去除计数字段后的详情类型，或声明同字段 `LiteratureDetail`。
- 将 `LiteratureRelations` 改为：

```typescript
interface LiteratureRelations {
  literature_id: number;
  pipelines: RelatedPipeline[];
  algorithms: RelatedAlgorithm[];
  database_tutorials: RelatedDatabaseTutorial[];
}
```

- 将 fetch 失败降级值改为：

```typescript
return {
  literature_id: Number(id),
  pipelines: [],
  algorithms: [],
  database_tutorials: []
};
```

- [ ] **Step 3: 改造详情页面阅读区**

标题区 badges 展示类型中文标签、`topic_name`、期刊和年份。meta 展示 DOI、PMID、最近复核日期和关联状态。

左侧按顺序渲染：

```tsx
<DetailSectionCard eyebrow="Chinese Guide" title="中文导读">
  <p className="text-base leading-8 text-slate-700">
    {literature.chinese_summary}
  </p>
</DetailSectionCard>

<DetailSectionCard eyebrow="Key Findings" title="核心结论">
  <ul className="space-y-3">
    {literature.key_findings_json.map((finding) => (
      <li key={finding} className="rounded border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-700">
        {finding}
      </li>
    ))}
  </ul>
</DetailSectionCard>
```

继续增加“适用场景”“英文摘要”“推荐阅读理由”三个 section。

右侧使用：

```tsx
<RelatedResources
  pipelines={relations.pipelines}
  algorithms={relations.algorithms}
  databaseTutorials={relations.database_tutorials}
  compact
  title="平台证据链"
  emptyText="这篇文献暂未关联具体平台资源"
/>
```

存在 DOI 时保留 DOI 外链，并在存在 `pmid` 时增加：

```tsx
<a
  href={`https://pubmed.ncbi.nlm.nih.gov/${literature.pmid}/`}
  target="_blank"
  rel="noreferrer"
>
  打开 PubMed
</a>
```

- [ ] **Step 4: 运行 TypeScript 检查**

Run:

```powershell
docker compose run --rm --no-deps frontend npx tsc --noEmit
git restore --source=HEAD -- frontend/tsconfig.tsbuildinfo
```

Expected: PASS。

- [ ] **Step 5: 提交**

```powershell
git add frontend/app/literatures/[id]/page.tsx frontend/components/RelatedResources.tsx
git commit -m "feat: add literature evidence detail view"
```

## Task 7: 在数据库教程中展示反向关联文献

**Files:**
- Modify: `frontend/lib/databaseTypes.ts`
- Modify: `frontend/lib/databaseApi.ts`
- Modify: `frontend/app/databases/tutorials/[id]/page.tsx`

- [ ] **Step 1: 增加教程关系类型**

在 `frontend/lib/databaseTypes.ts` 中增加：

```typescript
export interface RelatedLiteratureDto {
  id: number;
  title: string;
  journal: string;
  publication_year: number;
  doi: string | null;
}

export interface DatabaseTutorialRelationsDto {
  tutorial_slug: string;
  literatures: RelatedLiteratureDto[];
}
```

- [ ] **Step 2: 增加 API helper**

在 `frontend/lib/databaseApi.ts` 中增加：

```typescript
import type { DatabaseTutorialRelationsDto } from "@/lib/databaseTypes";

export async function fetchDatabaseTutorialRelations(
  slug: string
): Promise<DatabaseTutorialRelationsDto> {
  const response = await fetch(
    `${SERVER_API_BASE_URL}/api/databases/tutorials/${slug}/relations`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    return { tutorial_slug: slug, literatures: [] };
  }

  return (await response.json()) as DatabaseTutorialRelationsDto;
}
```

- [ ] **Step 3: 在教程详情页展示关联论文**

在 `frontend/app/databases/tutorials/[id]/page.tsx` 中并行获取教程和关系：

```typescript
  const [detail, relations] = await Promise.all([
    fetchDatabaseTutorial(params.id),
    fetchDatabaseTutorialRelations(params.id)
  ]);
```

在 sidebar 中加入：

```tsx
<RelatedResources
  literatures={relations.literatures}
  compact
  kicker="Evidence"
  title="关联文献"
  emptyText="这篇教程暂未关联精选文献"
/>
```

现有 Literature 关系卡片仅在 `literature.doi` 非空时展示 `DOI: ...`，缺少 DOI 时不渲染空标签。

- [ ] **Step 4: 运行 TypeScript 检查**

Run:

```powershell
docker compose run --rm --no-deps frontend npx tsc --noEmit
git restore --source=HEAD -- frontend/tsconfig.tsbuildinfo
```

Expected: PASS。

- [ ] **Step 5: 提交**

```powershell
git add frontend/lib/databaseTypes.ts frontend/lib/databaseApi.ts frontend/app/databases/tutorials/[id]/page.tsx
git commit -m "feat: link database tutorials to literature evidence"
```

## Task 8: 让全站搜索使用 Literature 中文导读和关键词

**Files:**
- Modify: `backend/app/services/search_service.py`
- Modify: `backend/tests/test_search_service.py`

- [ ] **Step 1: 编写失败测试**

在 `backend/tests/test_search_service.py` 中增加：

```python
from datetime import date

from sqlalchemy.orm import Session

from app.models.literature import Literature
from app.services.search_service import SearchService


def test_search_literature_matches_chinese_summary_and_keywords(
    db_session: Session,
) -> None:
    db_session.add(
        Literature(
            title="Example spatial transcriptomics paper",
            authors=["A. Author"],
            journal="Nature Methods",
            publication_year=2026,
            doi="10.0000/spatial-example",
            abstract_text="Example abstract.",
            literature_type="frontier_research",
            topic_key="spatial-transcriptomics",
            topic_name="空间转录组",
            keywords_json=["Visium", "空间定位"],
            chinese_summary="用于理解空间表达矩阵与组织坐标的联合分析。",
            recommendation_reason="空间转录组入门。",
            last_reviewed_at=date(2026, 6, 1),
        )
    )
    db_session.commit()

    response = SearchService(db_session).search(query="空间定位")

    assert response.total == 1
    assert response.items[0].type == "literature"
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_search_service.py::test_search_literature_matches_chinese_summary_and_keywords -q
```

Expected: FAIL，全站搜索当前只搜索标题、期刊、年份、作者和英文摘要。

- [ ] **Step 3: 扩展 Literature 搜索字段**

在 `backend/app/services/search_service.py` 的 `_search_literatures()` 中将中文导读、推荐理由和关键词纳入：

```python
                secondary=[
                    literature.journal,
                    str(literature.publication_year),
                    literature.topic_name,
                    literature.pmid or "",
                    *literature.authors,
                    *literature.keywords_json,
                ],
                summaries=[
                    literature.chinese_summary,
                    literature.recommendation_reason,
                    literature.abstract_text,
                ],
```

结果 tags 改为：

```python
tags=[
    literature.topic_name,
    literature.journal,
    str(literature.publication_year),
]
```

- [ ] **Step 4: 运行专项测试**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest tests/test_search_service.py -q
```

Expected: PASS。

- [ ] **Step 5: 提交**

```powershell
git add backend/app/services/search_service.py backend/tests/test_search_service.py
git commit -m "feat: enrich global literature search"
```

## Task 9: 补充文档并完成全量验证

**Files:**
- Modify: `docs/DATABASE_AND_SEED.md`
- Modify: `docs/FRONTEND_GUIDE.md`
- Modify: `docs/ROADMAP.md`

- [ ] **Step 1: 更新开发文档**

在 `docs/DATABASE_AND_SEED.md` 中记录：

- Literature 三类公开内容。
- `literature_records/*.json` 的维护方式。
- DOI / PMID 稳定 upsert key。
- 三张多对多关系表。
- seed 调用顺序必须为 Pipeline、Algorithm、Database、DatabaseTutorial、Literature。

在 `docs/FRONTEND_GUIDE.md` 中记录：

- `/literatures` URL 筛选参数。
- `/literatures/{id}` 中文导读和证据链。
- `/databases/tutorials/{slug}` 反向关联论文。

在 `docs/ROADMAP.md` 中将“文献与动态集轻量证据中心”标记为已完成，并将 DOI/PMID 批量导入、PubMed 候选抓取和人工审核队列放入后续阶段。

- [ ] **Step 2: 运行后端全量测试**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest -q
```

Expected: 全部 PASS。

- [ ] **Step 3: 运行公共内容扫描**

Run:

```powershell
docker compose run --rm --no-deps backend python scripts/scan_public_content.py
docker compose run --rm --no-deps -v "${PWD}\docs:/docs:ro" backend python scripts/scan_public_content.py /docs
```

Expected: 两次均输出 `Public content safety scan passed.`。

- [ ] **Step 4: 运行前端类型检查**

Run:

```powershell
docker compose run --rm --no-deps frontend npx tsc --noEmit
git restore --source=HEAD -- frontend/tsconfig.tsbuildinfo
```

Expected: PASS。

- [ ] **Step 5: 运行 Next.js 生产构建**

为避免 `next dev` 和 `next build` 共享 `.next`，先停止 `3001` 独立预览前端，再清理工作树内缓存：

```powershell
$frontendContainer = docker ps --filter "publish=3001" --format "{{.Names}}" | Select-Object -First 1
if ($frontendContainer) {
  docker stop $frontendContainer
}
$root = (Resolve-Path '.').Path
$nextPath = Join-Path $root 'frontend\.next'
if (Test-Path -LiteralPath $nextPath) {
  $resolved = (Resolve-Path -LiteralPath $nextPath).Path
  if (-not $resolved.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to delete outside workspace: $resolved"
  }
  Remove-Item -LiteralPath $resolved -Recurse -Force
}
docker compose run --rm --no-deps frontend npm run build
```

Expected: `Compiled successfully`。

- [ ] **Step 6: 重新初始化数据库并启动独立预览**

先删除构建缓存，再启动 `3001` 前端。保持 `8001` 后端运行；若后端已停止，则按相同数据库连接参数重新启动：

```powershell
docker compose run --rm --no-deps backend python init_db.py
docker compose run --rm --no-deps backend python init_db.py
$root = (Resolve-Path '.').Path
$nextPath = Join-Path $root 'frontend\.next'
if (Test-Path -LiteralPath $nextPath) {
  $resolved = (Resolve-Path -LiteralPath $nextPath).Path
  if (-not $resolved.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to delete outside workspace: $resolved"
  }
  Remove-Item -LiteralPath $resolved -Recurse -Force
}
docker compose run --rm -d --no-deps -p 3001:3000 -e BACKEND_API_URL=http://host.docker.internal:8001 -e NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8001 frontend npm run dev
```

Expected: 两次初始化均成功，第二次不会新增重复文献或重复 link。

- [ ] **Step 7: 浏览器验收**

在 `http://localhost:3001` 验收：

```text
/literatures
/literatures?literature_type=frontier_research
/literatures?keyword=Seurat
/databases/tutorials/geo-expression-search
/search?q=空间定位&type=literature
```

使用 API 动态获取 Seurat 文献详情地址：

```powershell
$seuratLiterature = Invoke-RestMethod 'http://localhost:8001/api/literatures?keyword=Seurat&limit=1'
$seuratLiteratureId = $seuratLiterature[0].id
"http://localhost:3001/literatures/$seuratLiteratureId"
```

验收要求：

- 默认列表展示至少 `20` 篇文献。
- URL 筛选刷新后仍保留状态。
- 列表卡片显示中文导读、类型标签和关联计数。
- 文献详情页显示中文导读、核心结论、适用场景、英文摘要和证据链。
- 数据库教程页显示反向关联论文。
- 移动端宽度下筛选控件、标签和卡片文字不重叠。
- 页面没有 hydration 错误浮层。

- [ ] **Step 8: 检查差异并提交文档**

Run:

```powershell
git diff --check
git status --short
```

Expected: 无空白错误，仅包含本轮预期文档差异。

```powershell
git add docs/DATABASE_AND_SEED.md docs/FRONTEND_GUIDE.md docs/ROADMAP.md
git commit -m "docs: describe literature evidence hub"
```

## Task 10: 最终代码审查

**Files:**
- Review all files changed by Tasks 1-9.

- [ ] **Step 1: 使用 requesting-code-review**

调用 `superpowers:requesting-code-review`，重点检查：

- 临时迁移能否在已有 PostgreSQL 数据库上重复执行。
- link 表 upsert 是否幂等，是否可能积累重复关系。
- Literature 列表请求失败时是否保留上一次有效数据。
- Pipeline、Algorithm 和 DatabaseTutorial 的反向关联是否保持可用。
- seed 中 DOI、PMID、标题和链接是否经过官方来源核验。
- 公共内容扫描是否覆盖新增 JSON seed。

- [ ] **Step 2: 修复审查问题**

对审查发现的问题逐项使用 TDD 修复，每个行为变更先增加失败测试，再做最小实现。

- [ ] **Step 3: 重新运行验证**

Run:

```powershell
docker compose run --rm --no-deps backend python -m pytest -q
docker compose run --rm --no-deps backend python scripts/scan_public_content.py
docker compose run --rm --no-deps frontend npx tsc --noEmit
git restore --source=HEAD -- frontend/tsconfig.tsbuildinfo
git diff --check
git status --short
```

Expected: 测试、扫描、类型检查和差异检查全部通过，工作树只包含经过审查后尚未提交的预期修复；如有修复，提交为独立 commit。
