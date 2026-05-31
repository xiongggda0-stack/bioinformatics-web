# 全栈学习笔记

这份笔记按“一个功能从前端到后端再到数据库”的路径来理解项目。

## 从 Pipeline 列表页开始

用户打开：

```text
http://localhost:3000/pipelines
```

前端文件：

```text
frontend/app/pipelines/page.tsx
frontend/components/PipelineBrowser.tsx
```

发生的事情：

1. `page.tsx` 读取 URL 参数。
2. `page.tsx` 请求后端 `/api/pipelines`。
3. `PipelineBrowser.tsx` 展示搜索框和筛选器。
4. 用户筛选时，组件更新 URL。
5. URL 变化后，组件重新请求后端。

后端文件：

```text
backend/app/api/v1/controllers/pipeline_controller.py
backend/app/services/pipeline_service.py
backend/app/repositories/pipeline_repository.py
backend/app/models/pipeline.py
backend/app/schemas/pipeline.py
```

数据库：

```text
pipelines 表
```

## 从 Pipeline 详情页开始

用户打开：

```text
http://localhost:3000/pipelines/9
```

前端会请求：

```text
/api/pipelines/9
/api/pipelines/9/relations
/api/pipelines?category_key=structure&limit=6
```

这些请求分别用于：

- 当前流程详情
- 相关算法和文献
- 同类推荐

## 学习 Controller-Service-Repository

可以按这个顺序读：

1. Controller：先看 URL 是什么。
2. Schema：看接口返回什么结构。
3. Service：看业务逻辑。
4. Repository：看数据库怎么查。
5. Model：看表字段。

## 学习前端组件

建议按这个顺序读：

1. `layout.tsx`：全局布局和导航。
2. `page.tsx`：页面如何请求数据。
3. `PipelineBrowser.tsx`：交互状态和 URL 同步。
4. `MarkdownRenderer.tsx`：Markdown 如何渲染。
5. `RelatedResources.tsx`：跨模块资源卡片如何复用。

## 学习 seed 数据

建议按这个顺序读：

1. `backend/init_db.py`
2. `backend/app/seed_data/__init__.py`
3. `backend/app/seed_data/pipelines.py`
4. `backend/app/seed_data/algorithms.py`
5. `backend/app/seed_data/literatures.py`

重点理解：

- 为什么 seed 函数要可重复执行。
- 为什么 Pipeline 内容要从 `init_db.py` 拆出来。
- 为什么分类字段要落库，而不是只写在前端。

## 你可以练习的小任务

1. 新增一个 Pipeline seed 数据。
2. 给它补充 `dag_json`。
3. 执行 `docker compose exec backend python init_db.py`。
4. 在 `/pipelines` 搜索它。
5. 打开详情页看 Markdown 是否正常渲染。

