# Bioinformatics Web 文档中心

这个目录记录 Bioinformatics Web MVP 的架构、开发方式、模块关系和学习笔记。项目目标是构建一个集分析流程、算法库和文献动态于一体的一站式生信云平台。

## 推荐阅读顺序

1. `ARCHITECTURE.md`：先理解整体系统如何运转。
2. `DEVELOPMENT_SETUP.md`：学习如何在本地启动和排错。
3. `BACKEND_GUIDE.md`：理解 FastAPI 后端分层架构。
4. `FRONTEND_GUIDE.md`：理解 Next.js 前端页面和组件。
5. `DATABASE_AND_SEED.md`：理解 PostgreSQL、初始化脚本和 seed 数据。
6. `MODULES.md`：理解 Pipeline、Algorithm、Literature 三大业务模块。
7. `API_REFERENCE.md`：查看当前接口清单。
8. `FULLSTACK_LEARNING_NOTES.md`：按文件结构学习全栈联动。
9. `ROADMAP.md`：查看下一阶段开发方向。

## 当前技术栈

- Frontend: Next.js App Router, React, TypeScript, TailwindCSS
- Backend: FastAPI, Pydantic, SQLAlchemy
- Database: PostgreSQL
- Runtime: Docker Compose

## 当前核心能力

- Pipeline Hub：分析流程列表、详情、Markdown 渲染、目录导航、同类推荐。
- Algorithm Gallery：算法工具列表、详情、Markdown 文档、ECharts 性能图。
- Literature Hub：文献列表、详情、DOI 外链、关联流程和算法跳转。
- Cross-linking：Pipeline、Algorithm、Literature 之间可以互相关联。

