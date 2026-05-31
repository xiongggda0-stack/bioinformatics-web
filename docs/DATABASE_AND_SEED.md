# 数据库与 Seed 数据

数据库使用 PostgreSQL。后端通过 SQLAlchemy ORM 定义表结构，通过 `init_db.py` 初始化表和 mock 数据。

## 数据模型

当前核心表：

- `pipelines`
- `algorithms`
- `literatures`
- `users`
- `database_resources`
- `database_tutorials`

## Pipeline 字段

核心字段：

- `id`
- `title`
- `description`
- `omics_type`
- `category_key`
- `category_name`
- `dag_json`
- `metadata_json`
- `content`
- `created_at`

`category_key/category_name` 已经落库，用于列表分类、详情同类推荐和后续后台管理。

## Seed 数据目录

```text
backend/app/seed_data/
  __init__.py
  pipelines.py
  algorithms.py
  literatures.py
  databases.py
  database_tutorials.py
  database_resources.json
  database_tutorials.json
```

职责：

- `pipelines.py`：分析流程 mock 数据、分类推断、元数据推断、upsert。
- `algorithms.py`：算法工具 mock 数据、性能 JSON、Markdown 文档。
- `literatures.py`：文献 mock 数据、Pipeline/Algorithm 外键关联。
- `databases.py`：数据库导航资源 JSON 加载、字段映射与 upsert。
- `database_tutorials.py`：独立数据库教程 JSON 加载、资源关联与 upsert。
- `__init__.py`：统一导出 seed 函数。

## init_db.py 职责

`backend/init_db.py` 只负责：

1. 创建数据库表。
2. 为旧数据库补充新增字段。
3. 调用各模块 seed 函数。

```python
seed_pipelines(db)
seed_algorithms(db)
seed_literatures(db)
seed_database_resources(db)
seed_database_tutorials(db)
```

## 为什么使用 upsert

seed 脚本需要能反复执行。每次执行时：

- 如果记录不存在，则创建。
- 如果记录已存在，则更新字段。

这样开发时可以不断修改流程文档和 mock 数据，而不需要手动清空数据库。

## 修改 seed 数据后的流程

```powershell
docker compose exec backend python init_db.py
```

然后刷新前端页面。

