# 公开展示型生信知识平台第一轮升级 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有生信知识平台升级为适合公开展示的版本：清理敏感信息，增加可信度信息，改造首页，新增学习路径，并增强全站搜索体验。

**Architecture:** 保持现有 FastAPI Controller-Service-Repository 与 Next.js App Router 架构。Pipeline 继续使用已有 `metadata_json`，Algorithm 新增 `metadata_json` JSON 字段；前端通过共享 `TrustPanel` 渲染可信度信息。学习路径使用前端结构化配置，不新增数据库表；搜索增强建立在现有 `/api/search` 接口之上。

**Tech Stack:** Python 3.12、FastAPI、Pydantic、SQLAlchemy、PostgreSQL 15、pytest、Next.js 14 App Router、React、TypeScript、TailwindCSS、Docker Compose。

---

## 文件结构

### 新建文件

```text
backend/
  app/services/content_safety_service.py   公共内容敏感信息扫描规则
  scripts/scan_public_content.py           可在容器内执行的扫描入口
  tests/test_content_safety_service.py     扫描规则回归测试
  tests/test_public_metadata_seed.py       Pipeline/Algorithm 可信度 seed 测试

frontend/
  app/learning-paths/page.tsx              学习路径首页
  components/TrustPanel.tsx                详情页可信度面板
  components/SearchHighlight.tsx           搜索关键词高亮
  lib/learningPaths.ts                     四条精选学习路线配置
  lib/trustMetadata.ts                     前端可信度类型和降级逻辑
```

### 修改文件

```text
backend/
  app/models/algorithm.py                  新增 Algorithm.metadata_json
  app/schemas/algorithm.py                 API 暴露 metadata_json
  app/seed_data/algorithms.py              为软件条目生成可信度元数据
  app/seed_data/pipelines.py               为流程生成可信度元数据并脱敏凭据
  init_db.py                               兼容已有 PostgreSQL 表

frontend/
  app/page.tsx                             研究问题入口、三类入口、闭环升级
  app/pipelines/[id]/page.tsx              接入 TrustPanel
  app/algorithms/[id]/page.tsx             接入 TrustPanel
  app/search/page.tsx                      热门词和排序说明
  components/Navbar.tsx                    增加学习路径导航
  components/SearchResultCard.tsx          接入关键词高亮
  components/SearchResults.tsx             透传关键词

docs/
  DEVELOPMENT_SETUP.md                     公共内容扫描命令
  FRONTEND_GUIDE.md                        学习路径和 TrustPanel
  DATABASE_AND_SEED.md                     Algorithm.metadata_json
  ROADMAP.md                               标记公开版第一轮能力
```

## Task 1: 建立公共内容敏感信息扫描基线

**Files:**
- Create: `backend/app/services/content_safety_service.py`
- Create: `backend/scripts/scan_public_content.py`
- Create: `backend/tests/test_content_safety_service.py`
- Modify: `backend/app/seed_data/pipelines.py:6335`
- Modify: `docs/DEVELOPMENT_SETUP.md`

- [ ] **Step 1: 编写失败测试**

创建 `backend/tests/test_content_safety_service.py`：

```python
from pathlib import Path

from app.services.content_safety_service import scan_paths


def test_scan_paths_flags_plaintext_login_password(tmp_path: Path) -> None:
    content = tmp_path / "pipeline.py"
    content.write_text("./lnd login -u real-user -p real-password", encoding="utf-8")

    findings = scan_paths([tmp_path])

    assert len(findings) == 1
    assert findings[0].rule == "login-password"


def test_scan_paths_accepts_documented_placeholders(tmp_path: Path) -> None:
    content = tmp_path / "pipeline.py"
    content.write_text(
        "./lnd login -u <YOUR_USERNAME> -p <YOUR_PASSWORD>",
        encoding="utf-8",
    )

    assert scan_paths([tmp_path]) == []
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```powershell
docker-compose exec -T backend python -m pytest tests/test_content_safety_service.py -q
```

Expected: FAIL，提示 `app.services.content_safety_service` 不存在。

- [ ] **Step 3: 实现扫描服务**

创建 `backend/app/services/content_safety_service.py`：

```python
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class SafetyFinding:
    path: Path
    line_number: int
    rule: str
    excerpt: str


LOGIN_PASSWORD_PATTERN = re.compile(
    r"login\b[^\n]*\s-u\s+(?!<YOUR_USERNAME>)(\S+)"
    r"[^\n]*\s-p\s+(?!<YOUR_PASSWORD>)(\S+)",
    re.IGNORECASE,
)
TOKEN_PATTERN = re.compile(
    r"(?i)\b(token|api[_-]?key|secret)\b\s*[:=]\s*"
    r"(?!<YOUR_TOKEN>)([A-Za-z0-9._-]{8,})"
)
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
WINDOWS_PATH_PATTERN = re.compile(r"\b[A-Za-z]:\\(?:[^\\\s]+\\?)+")

RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("login-password", LOGIN_PASSWORD_PATTERN),
    ("token", TOKEN_PATTERN),
    ("email", EMAIL_PATTERN),
    ("windows-absolute-path", WINDOWS_PATH_PATTERN),
)


def scan_paths(paths: list[Path]) -> list[SafetyFinding]:
    findings: list[SafetyFinding] = []
    for root in paths:
        files = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".py", ".json", ".md", ".ts", ".tsx"}:
                continue
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(),
                start=1,
            ):
                for rule, pattern in RULES:
                    if pattern.search(line):
                        findings.append(
                            SafetyFinding(
                                path=path,
                                line_number=line_number,
                                rule=rule,
                                excerpt=line.strip()[:160],
                            )
                        )
    return findings
```

创建 `backend/scripts/scan_public_content.py`：

```python
from pathlib import Path
import sys

from app.services.content_safety_service import scan_paths


def main() -> int:
    roots = [Path("app/seed_data")]
    findings = scan_paths(roots)
    for finding in findings:
        print(
            f"{finding.path}:{finding.line_number}: "
            f"[{finding.rule}] {finding.excerpt}"
        )
    if findings:
        print(f"Found {len(findings)} public content safety issue(s).")
        return 1
    print("Public content safety scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 脱敏已发现凭据**

在 `backend/app/seed_data/pipelines.py` 中替换：

```bash
./lnd login -u X101SC250910114-Z01-J003 -p ggeah41n
```

为：

```bash
./lnd login -u <YOUR_USERNAME> -p <YOUR_PASSWORD>
```

- [ ] **Step 5: 在开发文档中增加扫描命令**

在 `docs/DEVELOPMENT_SETUP.md` 增加：

```markdown
## 公开内容安全扫描

新增或导入 Pipeline、软件文档、数据库教程后，运行：

```powershell
docker-compose exec -T backend python scripts/scan_public_content.py
```

示例命令禁止提交真实用户名、密码、Token、邮箱和本机绝对路径。请使用
`<YOUR_USERNAME>`、`<YOUR_PASSWORD>`、`<YOUR_TOKEN>` 和 `<YOUR_PROJECT_DIR>`。
```

- [ ] **Step 6: 运行测试和真实扫描**

Run:

```powershell
docker-compose exec -T backend python -m pytest tests/test_content_safety_service.py -q
docker-compose exec -T backend python scripts/scan_public_content.py
```

Expected: `2 passed`，并输出 `Public content safety scan passed.`

- [ ] **Step 7: 提交**

```powershell
git add backend/app/services/content_safety_service.py backend/scripts/scan_public_content.py backend/tests/test_content_safety_service.py backend/app/seed_data/pipelines.py docs/DEVELOPMENT_SETUP.md
git commit -m "feat: add public content safety scan"
```

## Task 2: 为 Pipeline 和软件条目补充可信度元数据

**Files:**
- Modify: `backend/app/models/algorithm.py`
- Modify: `backend/app/schemas/algorithm.py`
- Modify: `backend/app/seed_data/pipelines.py`
- Modify: `backend/app/seed_data/algorithms.py`
- Modify: `backend/init_db.py`
- Create: `backend/tests/test_public_metadata_seed.py`

- [ ] **Step 1: 编写失败测试**

创建 `backend/tests/test_public_metadata_seed.py`：

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.algorithm import Algorithm
from app.models.pipeline import Pipeline
from app.seed_data.algorithms import seed_algorithms
from app.seed_data.pipelines import seed_pipelines


def test_pipeline_seed_exposes_public_trust_metadata(db_session: Session) -> None:
    seed_pipelines(db_session)
    pipeline = db_session.scalar(select(Pipeline).limit(1))

    assert pipeline is not None
    assert pipeline.metadata_json["validation_status"] in {
        "示例验证",
        "文档校验",
        "待验证",
    }
    assert pipeline.metadata_json["last_reviewed_at"]
    assert pipeline.metadata_json["applicability"]["data_types"]
    assert pipeline.metadata_json["disclaimer"]


def test_algorithm_seed_exposes_public_trust_metadata(db_session: Session) -> None:
    seed_algorithms(db_session)
    algorithm = db_session.scalar(select(Algorithm).where(Algorithm.name == "STAR"))

    assert algorithm is not None
    assert algorithm.metadata_json["validation_status"] == "文档校验"
    assert algorithm.metadata_json["official_docs_url"].startswith("https://")
    assert algorithm.metadata_json["version"]
    assert algorithm.metadata_json["installation"]
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```powershell
docker-compose exec -T backend python -m pytest tests/test_public_metadata_seed.py -q
```

Expected: FAIL，Algorithm 尚无 `metadata_json`，Pipeline 尚无公开可信度键。

- [ ] **Step 3: 扩展 Algorithm ORM 和 Schema**

在 `backend/app/models/algorithm.py` 中，紧跟 `performance_json` 增加：

```python
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
```

在 `backend/app/schemas/algorithm.py` 中，紧跟 `performance_json` 增加：

```python
    metadata_json: dict[str, Any] = Field(default_factory=dict)
```

在 `backend/init_db.py` 中增加兼容已有 PostgreSQL 数据库的字段补丁：

```python
        db.execute(
            text(
                "ALTER TABLE algorithms "
                "ADD COLUMN IF NOT EXISTS metadata_json JSON NOT NULL DEFAULT '{}'"
            )
        )
```

- [ ] **Step 4: 扩展 Pipeline 元数据推断**

在 `backend/app/seed_data/pipelines.py` 的 `infer_pipeline_metadata()` 返回值中增加：

```python
        "validation_status": "文档校验",
        "last_reviewed_at": "2026-06-01",
        "applicability": {
            "species": ["Human", "Mouse", "Plant"],
            "data_types": inputs[:6] or [omics_type],
            "experiment_types": [scenario_by_type.get(omics_type, omics_type)],
        },
        "disclaimer": (
            "本文档用于教学与流程设计参考。运行前请根据物种、参考基因组版本、"
            "测序平台和计算环境复核命令与参数。"
        ),
```

- [ ] **Step 5: 为 Algorithm 生成可信度元数据**

在 `backend/app/seed_data/algorithms.py` 增加：

```python
ALGORITHM_OFFICIAL_DOCS: dict[str, str] = {
    "STAR": "https://github.com/alexdobin/STAR",
    "Salmon": "https://salmon.readthedocs.io/",
    "featureCounts": "https://subread.sourceforge.net/",
    "DESeq2": "https://bioconductor.org/packages/DESeq2/",
    "Cell Ranger": "https://www.10xgenomics.com/support/software/cell-ranger",
    "Seurat v5": "https://satijalab.org/seurat/",
}


def infer_algorithm_metadata(item: dict[str, Any]) -> dict[str, Any]:
    name = str(item["name"])
    return {
        "validation_status": "文档校验",
        "last_reviewed_at": "2026-06-01",
        "difficulty": "进阶",
        "version": "请以官方文档最新稳定版为准",
        "installation": "优先使用官方安装说明或 Bioconda/Conda 环境隔离安装",
        "official_docs_url": ALGORITHM_OFFICIAL_DOCS.get(name),
        "applicability": {
            "species": ["Human", "Mouse", "Plant"],
            "data_types": [str(item["category"])],
            "experiment_types": [str(item["category_name"])],
        },
        "disclaimer": (
            "软件版本和默认参数可能变化。正式分析前请结合官方文档、"
            "数据规模和实验设计复核配置。"
        ),
    }
```

在 `seed_algorithms()` 的循环开头增加：

```python
        item["metadata_json"] = item.get("metadata_json") or infer_algorithm_metadata(item)
```

在更新已有 Algorithm 时增加：

```python
        algorithm.metadata_json = item["metadata_json"]
```

- [ ] **Step 6: 运行测试**

Run:

```powershell
docker-compose exec -T backend python -m pytest tests/test_public_metadata_seed.py -q
docker-compose exec -T backend python init_db.py
```

Expected: `2 passed`，初始化脚本正常完成。

- [ ] **Step 7: 提交**

```powershell
git add backend/app/models/algorithm.py backend/app/schemas/algorithm.py backend/app/seed_data/pipelines.py backend/app/seed_data/algorithms.py backend/init_db.py backend/tests/test_public_metadata_seed.py
git commit -m "feat: seed public trust metadata"
```

## Task 3: 新增可复用 TrustPanel

**Files:**
- Create: `frontend/lib/trustMetadata.ts`
- Create: `frontend/components/TrustPanel.tsx`

- [ ] **Step 1: 定义前端可信度类型和降级逻辑**

创建 `frontend/lib/trustMetadata.ts`：

```typescript
export interface TrustApplicability {
  species?: string[];
  data_types?: string[];
  experiment_types?: string[];
}

export interface TrustMetadata {
  validation_status?: string;
  last_reviewed_at?: string;
  difficulty?: string;
  official_docs_url?: string | null;
  version?: string;
  installation?: string;
  applicability?: TrustApplicability;
  disclaimer?: string;
}

export function getTrustValue(value?: string | null): string {
  return value?.trim() ? value : "待补充";
}
```

- [ ] **Step 2: 创建可信度面板**

创建 `frontend/components/TrustPanel.tsx`：

```tsx
import type { TrustMetadata } from "@/lib/trustMetadata";
import { getTrustValue } from "@/lib/trustMetadata";

interface TrustPanelProps {
  metadata: TrustMetadata;
  officialLinkLabel?: string;
}

function Tags({ items }: { items?: string[] }): JSX.Element {
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {(items?.length ? items : ["待补充"]).map((item) => (
        <span
          key={item}
          className="rounded bg-white px-2 py-1 text-xs text-slate-600 ring-1 ring-slate-200"
        >
          {item}
        </span>
      ))}
    </div>
  );
}

export default function TrustPanel({
  metadata,
  officialLinkLabel = "查看官方文档"
}: TrustPanelProps): JSX.Element {
  return (
    <section className="rounded border border-emerald-200 bg-emerald-50/50 p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
        Public Trust
      </p>
      <h2 className="mt-2 text-lg font-semibold text-ink">公开使用说明</h2>
      <dl className="mt-4 grid gap-3 sm:grid-cols-3">
        <div><dt className="text-xs text-slate-500">验证状态</dt><dd className="mt-1 text-sm font-semibold text-ink">{getTrustValue(metadata.validation_status)}</dd></div>
        <div><dt className="text-xs text-slate-500">最后更新</dt><dd className="mt-1 text-sm font-semibold text-ink">{getTrustValue(metadata.last_reviewed_at)}</dd></div>
        <div><dt className="text-xs text-slate-500">难度等级</dt><dd className="mt-1 text-sm font-semibold text-ink">{getTrustValue(metadata.difficulty)}</dd></div>
      </dl>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        <div><p className="text-xs text-slate-500">适用物种</p><Tags items={metadata.applicability?.species} /></div>
        <div><p className="text-xs text-slate-500">数据类型</p><Tags items={metadata.applicability?.data_types} /></div>
        <div><p className="text-xs text-slate-500">实验类型</p><Tags items={metadata.applicability?.experiment_types} /></div>
      </div>
      {metadata.official_docs_url ? (
        <a
          href={metadata.official_docs_url}
          target="_blank"
          rel="noreferrer noopener"
          className="mt-4 inline-flex text-sm font-semibold text-teal"
        >
          {officialLinkLabel}
        </a>
      ) : null}
      <p className="mt-4 border-t border-emerald-200 pt-4 text-xs leading-5 text-slate-600">
        {getTrustValue(metadata.disclaimer)}
      </p>
    </section>
  );
}
```

- [ ] **Step 3: 运行前端类型检查**

Run:

```powershell
docker-compose exec -T frontend npx tsc --noEmit --pretty false
```

Expected: PASS，无 TypeScript 错误。

- [ ] **Step 4: 提交**

```powershell
git add frontend/lib/trustMetadata.ts frontend/components/TrustPanel.tsx
git commit -m "feat: add reusable public trust panel"
```

## Task 4: 在 Pipeline 和软件详情页接入 TrustPanel

**Files:**
- Modify: `frontend/app/pipelines/[id]/page.tsx`
- Modify: `frontend/app/algorithms/[id]/page.tsx`

- [ ] **Step 1: 扩展 Pipeline 前端类型并渲染面板**

在 `frontend/app/pipelines/[id]/page.tsx` 中：

```tsx
import TrustPanel from "@/components/TrustPanel";
import type { TrustMetadata } from "@/lib/trustMetadata";
```

让 `PipelineMetadata` 继承可信度类型：

```tsx
interface PipelineMetadata extends TrustMetadata {
  difficulty?: string;
  tools?: string[];
  inputs?: string[];
  outputs?: string[];
  estimated_time?: string;
  scenario?: string;
}
```

在 `<PipelineMetadataPanel />` 前增加：

```tsx
      <TrustPanel metadata={pipeline.metadata_json ?? {}} />
```

- [ ] **Step 2: 扩展 Algorithm 前端类型并渲染面板**

在 `frontend/app/algorithms/[id]/page.tsx` 中：

```tsx
import TrustPanel from "@/components/TrustPanel";
import type { TrustMetadata } from "@/lib/trustMetadata";
```

在 `Algorithm` 接口中增加：

```tsx
  metadata_json: TrustMetadata;
```

在性能图表前增加：

```tsx
      <TrustPanel
        metadata={algorithm.metadata_json ?? {}}
        officialLinkLabel="打开官方文档"
      />
```

- [ ] **Step 3: 初始化数据库并运行类型检查**

Run:

```powershell
docker-compose exec -T backend python init_db.py
docker-compose exec -T frontend npx tsc --noEmit --pretty false
```

Expected: 两条命令均成功。

- [ ] **Step 4: HTTP 冒烟测试**

Run:

```powershell
Invoke-WebRequest http://localhost:3000/pipelines/1 -UseBasicParsing
Invoke-WebRequest http://localhost:3000/algorithms/4 -UseBasicParsing
```

Expected: 两个页面均返回 `200`。

- [ ] **Step 5: 提交**

```powershell
git add frontend/app/pipelines/[id]/page.tsx frontend/app/algorithms/[id]/page.tsx
git commit -m "feat: show trust metadata on detail pages"
```

## Task 5: 改造首页并新增学习路径页

**Files:**
- Create: `frontend/lib/learningPaths.ts`
- Create: `frontend/app/learning-paths/page.tsx`
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/components/Navbar.tsx`
- Modify: `frontend/app/layout.tsx`

- [ ] **Step 1: 创建学习路径配置**

创建 `frontend/lib/learningPaths.ts`：

```typescript
export interface LearningPathStep {
  title: string;
  description: string;
  href: string;
  resourceType: string;
}

export interface LearningPath {
  slug: string;
  title: string;
  description: string;
  audience: string;
  steps: LearningPathStep[];
}

export const learningPaths: LearningPath[] = [
  {
    slug: "bulk-rnaseq",
    title: "Bulk RNA-seq 入门",
    description: "从 FASTQ 质控到差异表达、富集分析和结果解释。",
    audience: "第一次独立完成 bulk RNA-seq 项目的学习者",
    steps: [
      { title: "选择标准流程", description: "先理解完整分析路线。", href: "/pipelines?keyword=Bulk%20RNA-seq", resourceType: "流程" },
      { title: "学习 STAR", description: "理解比对、索引和 BAM 输出。", href: "/search?q=STAR&type=algorithm", resourceType: "软件" },
      { title: "学习 GEO", description: "复用公开表达数据。", href: "/databases?keyword=GEO", resourceType: "数据库" }
    ]
  },
  {
    slug: "single-cell-rnaseq",
    title: "单细胞 RNA-seq 入门",
    description: "理解 Cell Ranger、Seurat、聚类注释与常见质控。",
    audience: "准备分析 10x Genomics 单细胞数据的学习者",
    steps: [
      { title: "选择 10x 流程", description: "从原始数据进入基础聚类。", href: "/pipelines?keyword=10x", resourceType: "流程" },
      { title: "学习 Cell Ranger", description: "理解 count 矩阵生成。", href: "/search?q=Cell%20Ranger&type=algorithm", resourceType: "软件" },
      { title: "学习 Seurat", description: "理解质控、降维、聚类和注释。", href: "/search?q=Seurat&type=algorithm", resourceType: "软件" }
    ]
  },
  {
    slug: "public-database",
    title: "公共数据库数据下载与复用",
    description: "从 GEO、SRA、ENA 和 Ensembl 获取可复用数据。",
    audience: "需要下载公开数据并复现分析的学习者",
    steps: [
      { title: "浏览数据库导航", description: "按数据类型查找入口。", href: "/databases", resourceType: "数据库" },
      { title: "检索 GEO", description: "查找表达矩阵和项目元数据。", href: "/databases?keyword=GEO", resourceType: "数据库" },
      { title: "下载 FASTQ", description: "从 SRA 或 ENA 获取原始数据。", href: "/databases?keyword=SRA", resourceType: "教程" }
    ]
  },
  {
    slug: "evidence-chain",
    title: "从流程文档到文献证据链",
    description: "把流程、软件、数据库和方法论文连接起来。",
    audience: "需要为分析方案补充证据依据的学习者",
    steps: [
      { title: "选择流程", description: "从研究问题找到分析路线。", href: "/pipelines", resourceType: "流程" },
      { title: "查看软件参数", description: "理解关键工具适用范围。", href: "/algorithms", resourceType: "软件" },
      { title: "查看文献证据", description: "追溯方法论文和 DOI。", href: "/literatures", resourceType: "文献" }
    ]
  }
];
```

- [ ] **Step 2: 创建学习路径页面**

创建 `frontend/app/learning-paths/page.tsx`：

```tsx
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import { learningPaths } from "@/lib/learningPaths";

export default function LearningPathsPage(): JSX.Element {
  return (
    <main className="min-h-screen bg-slate-50">
      <PageHeader
        eyebrow="Learning Paths"
        title="从研究问题走到可复用分析"
        description="选择一条精选路线，按顺序阅读流程、软件参数、数据库教程和文献证据。"
        stats={[{ label: "paths", value: learningPaths.length }]}
      />
      <section className="mx-auto grid max-w-7xl gap-5 px-6 py-10 lg:grid-cols-2">
        {learningPaths.map((path) => (
          <article key={path.slug} className="rounded border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">{path.audience}</p>
            <h2 className="mt-3 text-xl font-semibold text-ink">{path.title}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">{path.description}</p>
            <ol className="mt-5 space-y-3">
              {path.steps.map((step, index) => (
                <li key={step.href}>
                  <Link href={step.href} className="block rounded border border-slate-200 bg-slate-50 p-4 transition hover:border-teal hover:bg-white">
                    <span className="text-xs font-semibold text-coral">STEP {index + 1} · {step.resourceType}</span>
                    <h3 className="mt-2 text-sm font-semibold text-ink">{step.title}</h3>
                    <p className="mt-1 text-xs leading-5 text-slate-600">{step.description}</p>
                  </Link>
                </li>
              ))}
            </ol>
          </article>
        ))}
      </section>
    </main>
  );
}
```

- [ ] **Step 3: 改造首页**

在 `frontend/app/page.tsx` 中增加研究场景配置：

```tsx
const researchScenarios = [
  { title: "Bulk RNA-seq 差异表达", href: "/pipelines?keyword=Bulk%20RNA-seq", tag: "RNA-seq" },
  { title: "单细胞转录组", href: "/pipelines?keyword=10x", tag: "Single-cell" },
  { title: "可变剪接", href: "/pipelines?keyword=rMATS", tag: "Splicing" },
  { title: "WGCNA 共表达网络", href: "/pipelines?keyword=WGCNA", tag: "Network" },
  { title: "CUT&Tag", href: "/pipelines?keyword=CUT%26Tag", tag: "Epigenomics" },
  { title: "BSA", href: "/pipelines?keyword=BSA", tag: "Variant" },
  { title: "空间转录组", href: "/pipelines?keyword=Visium", tag: "Spatial" },
  { title: "更多分析流程", href: "/pipelines", tag: "Explore" }
];
```

将首页第一屏标题替换为：

```tsx
<h1 className="max-w-3xl text-4xl font-bold leading-tight text-ink md:text-6xl">
  你正在处理哪类生物信息学数据？
</h1>
<p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
  从研究问题出发，找到可复用分析流程，再继续查看软件参数、数据库入口和文献依据。
</p>
```

在第一屏加入 `researchScenarios` 网格；增加三个入口卡片，分别指向 `/pipelines`、`/search` 和 `/learning-paths`。保留已有分析闭环，但移动到后续区块。

- [ ] **Step 4: 更新导航和站点元信息**

在 `frontend/components/Navbar.tsx` 的 `navItems` 中加入：

```tsx
  { label: "学习路径", href: "/learning-paths" },
```

在 `frontend/app/layout.tsx` 更新：

```tsx
export const metadata: Metadata = {
  title: "生信知识平台",
  description: "连接分析流程、软件参数、数据库教程与文献证据的一站式生信知识平台"
};
```

- [ ] **Step 5: 类型检查和页面验证**

Run:

```powershell
docker-compose exec -T frontend npx tsc --noEmit --pretty false
Invoke-WebRequest http://localhost:3000/ -UseBasicParsing
Invoke-WebRequest http://localhost:3000/learning-paths -UseBasicParsing
```

Expected: 类型检查通过，两个页面均返回 `200`。

- [ ] **Step 6: 提交**

```powershell
git add frontend/lib/learningPaths.ts frontend/app/learning-paths/page.tsx frontend/app/page.tsx frontend/components/Navbar.tsx frontend/app/layout.tsx
git commit -m "feat: add public homepage and learning paths"
```

## Task 6: 增强全站搜索结果体验

**Files:**
- Create: `frontend/components/SearchHighlight.tsx`
- Modify: `frontend/components/SearchResultCard.tsx`
- Modify: `frontend/components/SearchResults.tsx`
- Modify: `frontend/components/GlobalSearch.tsx`
- Modify: `frontend/app/search/page.tsx`

- [ ] **Step 1: 创建关键词高亮组件**

创建 `frontend/components/SearchHighlight.tsx`：

```tsx
interface SearchHighlightProps {
  text: string;
  query?: string;
}

export default function SearchHighlight({
  text,
  query = ""
}: SearchHighlightProps): JSX.Element {
  const keyword = query.trim();
  if (!keyword) {
    return <>{text}</>;
  }

  const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const parts = text.split(new RegExp(`(${escaped})`, "ig"));

  return (
    <>
      {parts.map((part, index) =>
        part.toLowerCase() === keyword.toLowerCase() ? (
          <mark key={`${part}-${index}`} className="bg-amber-100 text-inherit">
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </>
  );
}
```

- [ ] **Step 2: 将查询词传递到结果卡片**

扩展 `frontend/components/SearchResultCard.tsx`：

```tsx
import SearchHighlight from "@/components/SearchHighlight";

interface SearchResultCardProps {
  item: SearchResultItem;
  query?: string;
  compact?: boolean;
  onNavigate?: () => void;
}
```

标题和描述使用：

```tsx
<SearchHighlight text={item.title} query={query} />
<SearchHighlight text={item.description} query={query} />
```

扩展 `frontend/components/SearchResults.tsx`：

```tsx
interface SearchResultsProps {
  items: SearchResultItem[];
  hasQuery: boolean;
  query?: string;
}
```

并传递：

```tsx
<SearchResultCard key={`${item.type}-${item.id}`} item={item} query={query} />
```

扩展 `frontend/components/GlobalSearch.tsx` 的预览卡片：

```tsx
<SearchResultCard
  key={`${result.type}-${result.id}`}
  item={result}
  query={trimmedKeyword}
  compact
  onNavigate={() => setIsOpen(false)}
/>
```

- [ ] **Step 3: 增加热门词与排序说明**

在 `frontend/app/search/page.tsx` 增加：

```tsx
const popularQueries = ["RNA-seq", "Seurat", "GEO", "WGCNA", "CUT&Tag"];
```

在搜索表单后增加热门词入口：

```tsx
<div className="mt-4 flex flex-wrap items-center gap-2">
  <span className="text-xs font-semibold text-slate-500">热门搜索</span>
  {popularQueries.map((item) => (
    <Link
      key={item}
      href={`/search?q=${encodeURIComponent(item)}`}
      className="rounded bg-white px-2.5 py-1 text-xs text-slate-600 ring-1 ring-slate-200 transition hover:text-teal hover:ring-teal"
    >
      {item}
    </Link>
  ))}
</div>
<p className="mt-4 text-xs leading-5 text-slate-500">
  结果按相关度排序：标题完全匹配优先，其次是标题包含、分类标签、摘要和正文命中。
</p>
```

修改结果渲染：

```tsx
<SearchResults items={response.items} hasQuery={hasQuery} query={query} />
```

- [ ] **Step 4: 运行类型检查和搜索页冒烟测试**

Run:

```powershell
docker-compose exec -T frontend npx tsc --noEmit --pretty false
Invoke-WebRequest "http://localhost:3000/search?q=GEO&type=all" -UseBasicParsing
```

Expected: 类型检查通过，搜索页返回 `200`。

- [ ] **Step 5: 提交**

```powershell
git add frontend/components/SearchHighlight.tsx frontend/components/SearchResultCard.tsx frontend/components/SearchResults.tsx frontend/components/GlobalSearch.tsx frontend/app/search/page.tsx
git commit -m "feat: improve public search experience"
```

## Task 7: 更新项目文档

**Files:**
- Modify: `docs/FRONTEND_GUIDE.md`
- Modify: `docs/DATABASE_AND_SEED.md`
- Modify: `docs/ROADMAP.md`

- [ ] **Step 1: 补充前端指南**

在 `docs/FRONTEND_GUIDE.md` 增加：

```markdown
## 公开知识平台体验

- `/learning-paths`：四条精选学习路线。
- `TrustPanel.tsx`：Pipeline 和软件详情页共用的可信度面板。
- `SearchHighlight.tsx`：全站搜索结果关键词高亮。
- 首页优先使用研究问题入口，引导用户进入流程。
```

- [ ] **Step 2: 补充数据库和 seed 指南**

在 `docs/DATABASE_AND_SEED.md` 增加：

```markdown
## 公开可信度元数据

- Pipeline 使用 `metadata_json` 保存验证状态、更新时间、适用范围和免责声明。
- Algorithm 使用 `metadata_json` 保存验证状态、更新时间、版本说明、安装方式、
  官方文档地址、适用范围和免责声明。
- 缺失字段由前端统一显示为“待补充”。
```

- [ ] **Step 3: 更新 Roadmap**

在 `docs/ROADMAP.md` 顶部增加：

```markdown
## 当前阶段：公开展示型知识平台

- 安全扫描与示例脱敏。
- Pipeline 和软件详情页可信度面板。
- 面向研究问题的首页入口。
- 学习路径页。
- 搜索关键词高亮与热门入口。
```

- [ ] **Step 4: 提交**

```powershell
git add docs/FRONTEND_GUIDE.md docs/DATABASE_AND_SEED.md docs/ROADMAP.md
git commit -m "docs: describe public knowledge platform features"
```

## Task 8: 完整回归与公开版视觉验收

**Files:**
- Verify only

- [ ] **Step 1: 运行公共内容扫描**

Run:

```powershell
docker-compose exec -T backend python scripts/scan_public_content.py
```

Expected: `Public content safety scan passed.`

- [ ] **Step 2: 运行后端完整测试**

Run:

```powershell
docker-compose exec -T backend python -m pytest -q
```

Expected: 全部测试通过。

- [ ] **Step 3: 运行前端 TypeScript 和生产构建**

Run:

```powershell
docker-compose exec -T frontend npx tsc --noEmit --pretty false
docker-compose run --rm --no-deps frontend npm run build
```

Expected: 两条命令均成功，构建路由包含 `/learning-paths`。

- [ ] **Step 4: 重建本地服务**

Run:

```powershell
docker-compose up -d --build
```

Expected: PostgreSQL healthy，backend 和 frontend 正常运行。

- [ ] **Step 5: HTTP 冒烟测试**

Run:

```powershell
$urls = @(
  "http://localhost:3000/",
  "http://localhost:3000/learning-paths",
  "http://localhost:3000/pipelines/1",
  "http://localhost:3000/algorithms/4",
  "http://localhost:3000/search?q=GEO&type=all",
  "http://localhost:8000/api/health"
)
$urls | ForEach-Object {
  $response = Invoke-WebRequest $_ -UseBasicParsing
  [PSCustomObject]@{ Url = $_; Status = $response.StatusCode }
}
```

Expected: 所有 URL 均返回 `200`。

- [ ] **Step 6: 桌面端视觉检查**

使用浏览器检查：

```text
http://localhost:3000/
http://localhost:3000/learning-paths
http://localhost:3000/pipelines/1
http://localhost:3000/algorithms/4
http://localhost:3000/search?q=GEO&type=all
```

检查：

- 首页第一屏可见研究问题入口，下一屏有内容提示。
- 学习路径步骤卡片层级清楚。
- TrustPanel 不遮挡详情正文和右侧 TOC。
- 搜索高亮可见，热门词可点击。
- 中文文本无乱码。

- [ ] **Step 7: 移动端视觉检查**

使用 `390x844` 视口检查：

```text
http://localhost:3000/
http://localhost:3000/learning-paths
http://localhost:3000/pipelines/1
http://localhost:3000/search?q=GEO&type=all
```

检查：

- 顶部导航可横向滚动，不覆盖搜索框。
- 研究场景卡片文本不溢出。
- TrustPanel 标签换行自然。
- 搜索标签和结果卡片不横向溢出。

- [ ] **Step 8: 抽查外链安全属性**

检查 `TrustPanel.tsx` 中外链：

```tsx
target="_blank"
rel="noreferrer noopener"
```

Expected: 两个属性均存在。

- [ ] **Step 9: 检查工作区并提交必要修复**

Run:

```powershell
git diff --check
git status --short
```

Expected: 无未解释的改动，无空白错误。

如果视觉验收产生必要修复，按实际改动文件逐个暂存后提交：

```powershell
git add frontend/app frontend/components frontend/lib
git commit -m "fix: polish public knowledge platform"
```
