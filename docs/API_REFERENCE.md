# API Reference

后端服务地址：

```text
http://localhost:8000
```

Swagger：

```text
http://localhost:8000/docs
```

## Health

### GET `/api/health`

检查服务和数据库状态。

## Pipelines

### GET `/api/pipelines`

获取流程列表。

常用查询参数：

- `keyword`
- `omics_type`
- `category_key`
- `difficulty`
- `tool`
- `input_type`
- `output_type`
- `scenario`
- `skip`
- `limit`

示例：

```text
/api/pipelines?category_key=structure&tool=WGCNA&limit=10
```

### GET `/api/pipelines/{pipeline_id}`

获取单个流程详情。

### GET `/api/pipelines/{pipeline_id}/relations`

获取流程关联的算法和文献。

## Algorithms

### GET `/api/algorithms`

获取算法列表。

### GET `/api/algorithms/{algorithm_id}`

获取算法详情。

### GET `/api/algorithms/{algorithm_id}/relations`

获取算法关联的流程和文献。

## Literatures

### GET `/api/literatures`

获取文献列表。

### GET `/api/literatures/{literature_id}`

获取文献详情。

### GET `/api/literatures/{literature_id}/relations`

获取文献关联的流程和算法。

## 响应格式

当前部分接口直接返回 Pydantic 数据，异常响应由全局异常处理统一包装：

```json
{
  "code": 1,
  "message": "错误信息",
  "data": null
}
```

