# 文献集数据扩展设计

## 1. 背景与动机

Bioinformatics Web 当前文献集模块仅含 3 篇种子文献（BWA、Seurat v5、10x 单细胞），覆盖领域过窄，无法支撑平台公开展示的学术深度。文献作为知识平台“分析闭环”的证据基础，需要以可控方式扩展到覆盖更多生信子领域。

### 当前状态

| 维度 | 现状 |
|------|------|
| 数据量 | 3 篇，全部手工编写 |
| 模型字段 | title / authors(JSON) / journal / publication_year / doi / abstract_text / pipeline_id / algorithm_id |
| API | `GET /api/literatures`（列表）、`GET /api/literatures/:id`（详情）、`GET /api/literatures/:id/relations`（关联） |
| 导入方式 | 无——仅 seed 脚本手动构建 |
| 自动关联 | 无——关联 ID 在 seed 阶段手工指定 |

### 目标

- 新增 PubMed 批量导入和 DOI 单篇导入能力
- 导入时自动匹配已有的 Pipeline 和 Algorithm 并关联
- 种子数据扩展到至少 10 篇，覆盖更多生信方向
- 不引入前端变更，纯后端能力构建

## 2. 新增 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/literatures/import/pubmed` | PubMed 批量导入 |
| `POST` | `/api/literatures/import/doi` | 单篇 DOI 导入 |

### 2.1 PubMed 批量导入

**请求体：**

```json
{
  "pmids": ["19906852", "37880429"],
  "auto_match": true
}
```

**响应体：**

```json
{
  "code": 200,
  "message": "导入完成",
  "data": {
    "imported": 2,
    "skipped": 0,
    "failed": 0,
    "matched": 1,
    "details": [
      {"pmid": "19906852", "title": "...", "status": "imported", "matched_to": "BWA-MEM"},
      {"pmid": "37880429", "title": "...", "status": "imported", "matched_to": null}
    ]
  }
}
```

**处理逻辑：**

1. 接收 PMID 列表，去重
2. 调用 NCBI E-utilities `efetch` 接口获取 XML
3. 解析 XML 提取 title / authors / journal / publication_year / doi / abstract_text
4. 按 DOI 去重（已存在则 `skipped`）
5. 写入 `literatures` 表
6. 若 `auto_match=true`，调用匹配引擎
7. 返回导入报告

### 2.2 DOI 单篇导入

**请求体：**

```json
{
  "doi": "10.1093/bioinformatics/btp324",
  "pipeline_id": null,
  "algorithm_id": 5,
  "auto_match": true
}
```

**处理逻辑：**

1. 调用 CrossRef API（`api.crossref.org/works/:doi`）
2. 解析 JSON 提取元数据
3. 若用户手动指定了 `pipeline_id` / `algorithm_id`，直接使用（不覆盖）
4. 若 `auto_match=true` 且无手动指定，调匹配引擎补充
5. 写入并返回结果

## 3. 自动匹配引擎

### 3.1 匹配策略（按优先级）

| 优先级 | 策略 | 示例 |
|--------|------|------|
| 1 | **精确匹配** — 文献标题或摘要包含 Pipeline/Algorith 完整名称 | 标题含 "Seurat v5" → `algorithm_id` |
| 2 | **关键词映射** — 预定义映射表 | "BWA" → BWA-MEM；"WGS" → WGS 变异检测流程 |
| 3 | **模糊匹配** — 分词后 Jaccard 相似度 ≥ 0.6 | "single cell RNA" ≈ "10x 单细胞基础降维聚类" |

### 3.2 规则

- 一篇文献可同时匹配多个资源（当前模型支持 pipeline_id + algorithm_id 各一个，取最佳匹配）
- 匹配不上的字段保持 `NULL`，不强制关联
- 手动指定的 `pipeline_id` / `algorithm_id` 优先于自动匹配结果
- `auto_match=false` 时跳过匹配

## 4. 组件结构

```
backend/app/
├── api/v1/controllers/literature_import_controller.py  # 新增导入端点
├── schemas/literature_import.py                        # 新增请求/响应 schema
├── services/
│   ├── literature_importer.py                          # PubMed/CrossRef 数据拉取
│   └── literature_matcher.py                           # 自动匹配引擎
└── seed_data/literatures.py                            # 扩展种子数据
```

## 5. 新增依赖

```
lxml==5.3.0
```

`requests` 已存在于 Python 标准库周边环境，NCBIText XML 解析需 lxml。

## 6. 种子数据扩展

现有 3 篇 → 扩展至 10 篇，新增 7 篇覆盖更多生信方向：

| # | 论文 | 方向 | 关联 |
|---|------|------|------|
| 4 | Kaya-Okur et al. (2019) — CUT&Tag | 表观组学 | → CUT&Tag 流程（如有） |
| 5 | Ståhl et al. (2016) — Spatial Transcriptomics | 空间组学 | — |
| 6 | Landt et al. (2012) — ChIP-seq Guidelines | ChIP-seq | — |
| 7 | Langfelder & Horvath (2008) — WGCNA | 共表达网络 | → WGCNA 流程/算法（如有） |
| 8 | Dobin et al. (2013) — STAR | RNA-seq 比对 | → STAR 算法（如有） |
| 9 | Liao, Smyth & Shi (2014) — featureCounts | 定量 | → featureCounts 算法（如有） |
| 10 | Yu et al. (2012) — clusterProfiler | 富集分析 | — |

> 种子数据注入时通过名称查找 Pipeline/Algorithm ID。如目标资源不存在，`pipeline_id` / `algorithm_id` 留 `NULL`，不影响文献入库。

## 7. 错误处理

| 场景 | 行为 |
|------|------|
| DOI 已存在 | 返回 `skipped`，不出错 |
| PubMed API 返回空/错误 | 单篇 `failed`，不中断其他导入 |
| 网络超时（10s） | 单篇 `failed`，写入 error 信息 |
| 用户传入无效 PMID | 返回 422，列出无效项 |
| 匹配引擎无结果 | 正常入库，关联字段留空 |

## 8. 不包含

- 前端导入界面（后续独立迭代）
- 实时 PubMed 搜索建议
- 被引次数等外部指标拉取
- PDF/全文下载链路
- 批量导入的异步任务队列（首版同步处理，PMID 数量上限 50）
- 文献与数据库教程的关联（当前模型不支持）

## 9. 验证要求

1. `POST /api/literatures/import/pubmed` — 用已知 PMID 验证导入+匹配
2. `POST /api/literatures/import/doi` — 用已知 DOI 验证单篇导入+手动指定关联
3. 去重 —— 重复导入同 DOI 应 skip
4. 网络错误 —— 无效 PMID 应返回 failed 不崩溃
5. 种子数据 —— `init_db.py` 运行后 10 篇文献全部入库
6. 后端回归测试通过
