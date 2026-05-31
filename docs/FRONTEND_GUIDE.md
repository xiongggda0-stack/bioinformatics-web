# 前端指南

前端使用 Next.js App Router + React + TypeScript + TailwindCSS。

## 核心目录

```text
frontend/
  app/
    layout.tsx
    page.tsx
    pipelines/
    algorithms/
    literatures/
    databases/
    search/
  components/
    Navbar.tsx
    GlobalSearch.tsx
    SearchResultCard.tsx
    SearchResults.tsx
    PipelineBrowser.tsx
    MarkdownRenderer.tsx
    PipelineToc.tsx
    RelatedResources.tsx
    BenchmarkChart.tsx
```

## 页面组织

### 首页

路径：`/`

文件：`frontend/app/page.tsx`

展示平台三大入口：Pipeline、Algorithm、Literature。

### Pipeline

- `/pipelines`：流程列表页
- `/pipelines/[id]`：流程详情页

列表页支持：

- 关键词搜索
- 分类筛选
- 组学类型筛选
- 难度、工具、输入、输出、场景筛选
- URL 参数同步
- 后端查询

详情页支持：

- 元数据展示
- DAG 步骤展示
- Markdown 渲染
- 右侧 TOC
- 同类推荐
- 相关算法和文献

### Algorithm

- `/algorithms`
- `/algorithms/[id]`

详情页展示：

- 算法文档
- ECharts 性能基准图
- 相关流程和文献

### Literature

- `/literatures`
- `/literatures/[id]`

详情页展示：

- 标题、作者、期刊、年份、DOI
- DOI 外链
- 相关 Pipeline 和 Algorithm

### Database

- `/databases`：从后端读取数据库资源，支持关键词和分类筛选。
- `/databases/tutorials/[id]`：展示独立数据库教程。

### Search

- 顶部 `GlobalSearch.tsx`：调用 `/api/search`，显示最多 8 条快速预览。
- `/search`：完整搜索中心，支持资源类型筛选。
- 搜索关键词和类型都写入 URL，便于刷新、收藏和分享。

## 数据请求模式

目前主要使用 Server Component 发起后端请求：

```typescript
const response = await fetch(`${API_BASE_URL}/api/pipelines`, {
  cache: "no-store"
});
```

需要交互筛选时，使用 Client Component 读取和更新 URL：

```typescript
router.replace(`${pathname}?${query}`, { scroll: false });
```

## Markdown 渲染

组件：`MarkdownRenderer.tsx`

能力：

- `react-markdown`
- `remark-gfm`
- Tailwind typography
- 代码块语言标识
- 表格渲染

