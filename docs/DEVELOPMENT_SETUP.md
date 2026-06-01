# 本地开发与启动

## 目录位置

当前项目位于：

```powershell
<YOUR_PROJECT_DIR>
```

进入项目：

```powershell
cd <YOUR_PROJECT_DIR>
```

## 启动服务

确保 Docker Desktop 已启动，然后运行：

```powershell
docker compose up --build
```

常用地址：

- 前端：http://localhost:3000
- 后端健康检查：http://localhost:8000/api/health
- Swagger 文档：http://localhost:8000/docs

## 初始化数据库

如果修改了 seed 数据或模型字段：

```powershell
docker compose exec backend python init_db.py
```

## 常用验证命令

后端 Python 编译：

```powershell
python -m py_compile backend\init_db.py
docker compose exec backend python -m py_compile init_db.py
```

前端 TypeScript 检查：

```powershell
docker compose exec frontend npx tsc --noEmit --pretty false
```

公开内容安全扫描：

```powershell
docker compose exec -T backend python scripts/scan_public_content.py
```

扫描 docs 目录时，需要显式挂载仓库根目录下的 docs：

```powershell
docker compose run --rm --no-deps -v "${PWD}\docs:/docs:ro" backend python scripts/scan_public_content.py /docs
```

新增或导入公开内容后必须执行安全扫描。禁止提交真实用户名、密码、Token、邮箱、本机绝对路径和 bucket locator。示例中的用户名、密码、Token、路径和 bucket 应分别使用 `<YOUR_USERNAME>`、`<YOUR_PASSWORD>`、`<YOUR_TOKEN>`、`${PROJECT_DIR}` 和 `${BUCKET}`。需要完整 URI 时，在协议后组合 `${BUCKET}`，不要写入真实 bucket 名称。

后端测试：

```powershell
docker compose exec backend python -m pytest -q
```

统一搜索接口验证：

```powershell
Invoke-RestMethod "http://localhost:8000/api/search?q=RNA-seq&type=all&limit=10"
```

查看日志：

```powershell
docker compose logs backend --tail=50
docker compose logs frontend --tail=50
```

重启服务：

```powershell
docker compose restart backend
docker compose restart frontend
```

## 常见问题

### Docker 拉取镜像失败

可能是 Docker Hub 网络问题。可以重试，或配置 Docker Desktop 镜像加速。

### 前端页面缓存异常

可以删除 Next.js 缓存后重启前端：

```powershell
if (Test-Path frontend\.next) { Remove-Item -LiteralPath frontend\.next -Recurse -Force }
docker compose restart frontend
```

### `npm run lint` 弹出交互

当前项目还没有初始化 ESLint 配置，因此优先使用：

```powershell
docker compose exec frontend npx tsc --noEmit --pretty false
```

