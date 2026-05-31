# 后端指南

后端使用 FastAPI + Pydantic + SQLAlchemy，并采用 Controller-Service-Repository 分层。

## 核心目录

```text
backend/app/
  main.py
  core/
    config.py
    database.py
    exceptions.py
  models/
  schemas/
  repositories/
  services/
  api/v1/controllers/
  seed_data/
```

## 分层说明

### Controller

位置：`backend/app/api/v1/controllers/`

职责：

- 定义 URL，例如 `/api/pipelines`
- 声明请求参数，例如 `keyword`、`category_key`
- 声明 response_model
- 调用 Service

示例：

```python
@router.get("", response_model=list[PipelineResponse])
def list_pipelines(db: Session = Depends(get_db)) -> list[Pipeline]:
    service = PipelineService(db)
    return service.list_pipelines()
```

### Service

位置：`backend/app/services/`

职责：

- 组织业务逻辑
- 处理不存在、权限、状态等业务错误
- 调用 Repository

### Repository

位置：`backend/app/repositories/`

职责：

- 编写 SQLAlchemy 查询
- 不处理 HTTP 状态码
- 不直接关心页面展示

### Model

位置：`backend/app/models/`

职责：

- 定义数据库表
- 使用 SQLAlchemy ORM

### Schema

位置：`backend/app/schemas/`

职责：

- 定义 API 输入输出结构
- 使用 Pydantic
- 保持前后端类型一致

## 当前主要接口模块

- `pipeline_controller.py`
- `algorithm_controller.py`
- `literature_controller.py`
- `health_controller.py`

## 全局错误处理

`backend/app/core/exceptions.py` 负责把异常转换成统一 JSON 格式：

```json
{
  "code": 1,
  "message": "错误信息",
  "data": null
}
```

