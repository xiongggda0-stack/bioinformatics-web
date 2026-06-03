# 生信云平台全站 UI 翻新设计文档

> 日期: 2026-06-03
> 状态: 已确认，待制定实现计划
> Dial 配置: DESIGN_VARIANCE=5 / MOTION_INTENSITY=3 / VISUAL_DENSITY=4

---

## 1. 整体风格定位

**设计口号:** "安静的研究工作站"——生信科研人员的一张干净大白桌子，工具和数据整齐摆放，视觉噪音收敛到最低。

### 基础参数

| Dial | 值 | 含义 |
|---|---|---|
| DESIGN_VARIANCE | 5 | 轻微的布局不对称（Hero 非对称分栏、首页不等高网格），不追求艺术化混乱 |
| MOTION_INTENSITY | 3 | 仅 CSS :hover / :active 状态变化，不安装 framer-motion，无任何 JS 动画 |
| VISUAL_DENSITY | 4 | 适中的信息密度，学术工具不需要"艺术画廊"也不应该是"数据驾驶舱" |

### 视觉关键词

- **克制** —— 单一灰阶 + 一个强调色，无渐变、无发光、无装饰图形
- **清晰** —— 每条分割线和间距都有明确的信息层级目的
- **微弱质感** —— 卡片：白底 + `border-slate-200/60` + `shadow-[0_1px_3px_rgba(0,0,0,0.04)]`；hover: `translateY(-2px)` 纯 CSS transition
- **学术感** —— 列表和表格优先于装饰性卡片，数据以最直接方式呈现

### 布局架构

- **侧边栏主导航**——替代现有顶部 Navbar。左侧固定，收起时仅图标（60px），展开时显示模块名+子链接（220px）。状态存入 localStorage
- **不对称首页网格**——Hero 左侧标题 + 右侧数据摘要；模块入口 2×2 不等高卡片；数据概览横滚条
- **统一详情页骨架**——每个内页共用 DetailPageShell（页眉+主体+侧边工具栏），只改样式不改结构

### 衬线体边界

| 区域 | 字体 |
|---|---|
| 导航、按钮、标签、搜索框、表格、列表、表单、页面标题、Hero | Geist Sans（无例外） |
| 文献详情页正文段落 | Source Serif 4（整站唯一允许位置） |
| 文献详情页标题和元信息 | Geist Sans（仅正文用衬线体） |

### 动效策略

- 纯 CSS transition，零 JS 动画，不安装 framer-motion
- 卡片 hover：`transition-all duration-200`，`hover:-translate-y-0.5`
- 按钮 :active：`active:scale-[0.98]`
- 链接 hover 颜色过渡：`transition-colors duration-150`
- 侧边栏展开/收起：CSS transition width + opacity

### 图标方案

- 安装 `@phosphor-icons/react`，统一 `strokeWidth: 1.5`
- 替代当前 Unicode 字符和散装图标

### 组件变更清单

| 现有组件 | 操作 |
|---|---|
| Navbar.tsx | 删除，替换为 Sidebar.tsx |
| GlobalSearch.tsx | 删除，拆分为 SearchInput.tsx + SearchDropdown.tsx |
| page.tsx | 重写——新首页布局 |
| layout.tsx | 重写——引入侧边栏布局 |
| DetailPageShell.tsx | 重新设计样式 |
| AlgorithmBrowser.tsx | 保留逻辑，重新设计样式 |
| DatabaseBrowser.tsx | 保留逻辑，重新设计样式 |
| PipelineBrowser.tsx | 保留逻辑，重新设计样式 |
| MarkdownRenderer.tsx | 增强——支持 useSerif 配置 |
| SearchResultCard.tsx | 重新设计样式 |
| SearchResults.tsx | 保留逻辑，重新设计样式 |
| PageHeader.tsx | 重新设计样式 |
| BenchmarkChart.tsx | 保留不改（ECharts 封装） |
| DocumentToc.tsx | 重新设计样式 |
| RelatedResources.tsx | 重新设计样式 |

---

## 2. 首页信息架构

5 个纵向区域，从上到下：

### 区域 1: Hero（不对称双栏）

**左栏（1.05fr）：**
- 品牌标识文字 "Bioinformatics Workbench"，`text-xs font-medium tracking-[0.12em] uppercase text-slate-400`
- 主标题："连接流程、软件与文献的生信工作台"，`text-4xl md:text-6xl font-bold tracking-tight`，最多 2 行
- 描述：不超过 25 词，`text-base text-slate-500 leading-relaxed max-w-[52ch]`
- 超大搜索框 SearchInput(lg)：`h-14`，Phosphor MagnifyingGlass 图标，回车跳转 /search
- 5 个热门标签 pill：RNA-seq, Seurat, GEO, WGCNA, DESeq2

**右栏（0.95fr）：**
- 4 行数据摘要，无卡片包裹，border-b 分隔
- 每行：大号数字（`text-3xl font-bold text-slate-900`）+ 标签（`text-xs text-slate-400`）
- 指标：分析流程数、软件算法数、数据库资源数、文献与教程数
- 加载态：3 行骨架占位条
- 错误态：Phosphor Warning 图标 + "数据加载失败"

**布局:** `grid grid-cols-1 lg:grid-cols-[1.05fr_0.95fr] gap-10`，`min-h-[480px]`

### 区域 2: 四大模块入口（2×2 不对称网格）

背景 `bg-slate-50`，`py-16`

```
lg: grid grid-cols-[3fr_2fr] gap-4
├── 分析流程（大卡片，row-span-2，≈320px 高）
│   └── 展示最多 3 个流程的缩略预览
├── 软件与算法（矮卡片，≈152px 高）
├── 数据库导航（矮卡片，≈152px 高）
└── 文献集（底部全宽卡片，≈180px 高）
    └── 横向排列 3 篇最新文献摘要
```

**卡片样式:** `bg-white border border-slate-200/60 rounded-lg p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)]`
**Hover:** `hover:border-slate-300 hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] hover:-translate-y-0.5 transition-all duration-200`

### 区域 3: 快速入口横滚条

- `flex overflow-x-auto gap-2 pb-2`，背景 `bg-white`，`py-12`
- 每个入口为 pill 按钮：`px-4 py-2 rounded-full border border-slate-200 text-sm`
- 示例："RNA-seq 差异表达", "单细胞聚类", "WGCNA 共表达网络", "BSA 性状定位", "CUT&Tag 富集分析"

### 区域 4: 最近更新

- 3 列网格 `grid-cols-1 md:grid-cols-3 gap-8`
- 列 1 "最新流程"、列 2 "新增工具"、列 3 "数据库更新"
- 每列顶部小标题 L3，下方列表项带 Phosphor Circle 小圆点（模块对应颜色）
- 空态：Phosphor Empty 图标 + "暂无数据"

### 区域 5: 页脚

- 极简一行，`border-t border-slate-100 py-8`
- "Bioinformatics Workbench / 2026"，`text-xs text-slate-400`

---

## 3. 色彩方案

### 主色板

```
Accent (暗青)            #0d6b63     ← 替代现有 teal #0f766e
Accent-hover             #095650
Accent-subtle            #e6f2f0     ← 极淡背景（hover 行、选中态）

Page BG                  #ffffff
Surface-subtle           #f8fafc     ← slate-50
Border                   #e2e8f0     ← slate-200
Border-subtle            #e2e8f0/60
Border-hover             #cbd5e1     ← slate-300
Divider                  #f1f5f9     ← slate-100

Text-primary             #0f172a     ← slate-900
Text-body                #475569     ← slate-600
Text-secondary           #64748b     ← slate-500
Text-tertiary            #94a3b8     ← slate-400
Text-on-accent           #ffffff
```

### 语义色（极简使用）

```
Tag-pipeline             #0d6b63     ← accent 同色
Tag-algorithm            #6366f1     ← 低饱和 indigo
Tag-database             #059669     ← 低饱和 emerald
Tag-literature           #d97706     ← 低饱和 amber
Tag-search-result        #475569     ← slate-600（无彩色）

Success                  #059669
Warning                  #d97706
Error                    #dc2626

Skeleton-base            #f1f5f9
Skeleton-shimmer         #e2e8f0
```

### 规则

- 全局仅使用 Slate 冷灰系列，不混用 Warm Gray / Zinc / Neutral / Stone
- 不使用 purple / violet / fuchsia / pink 色系
- 无纯黑 `#000000`，最深色为 `#0f172a`（slate-900）
- 分类标签仅用于各自模块的范围，搜索结果统一 slate-500 无彩色
- `tailwind.config.ts` 不需自定义 color token，全部使用内置 slate 色阶

---

## 4. 字体与字号层级

### 字体选型

| 用途 | 字体 | 加载方式 |
|---|---|---|
| UI 全局 | Geist Sans (400/500/600/700) | next/font/google |
| 代码/mono | Geist Mono (400/500) | next/font/google |
| 文献正文 | Source Serif 4 (400) | next/font/google |

### 6 级字号体系

| 级别 | 用途 | 规格 |
|---|---|---|
| L1 | Hero 主标题 | `text-4xl md:text-6xl font-bold tracking-tight leading-tight` |
| L2 | 页面标题/卡片大标题 | `text-2xl md:text-3xl font-semibold leading-tight` |
| L3 | 区块小标题/侧边栏标题 | `text-sm font-semibold uppercase tracking-[0.12em]` |
| L4 | 正文/卡片描述 | `text-base leading-relaxed max-w-[65ch]` |
| L5 | 辅助文字/caption | `text-xs leading-normal` |
| L6 | mono 代码/文件名 | `text-sm font-mono leading-normal` |

### 规则

- 不用 Inter，不用衬线体做 UI
- 一个页面最多同时出现 4 种字号
- 相邻区块字号落差不超过 2 级
- 移动端 Hero 标题从 text-6xl 降为 text-3xl

---

## 5. 页面组件列表

```
components/
├── layout/                    ← 新增
│   ├── Sidebar.tsx            [新增] "use client"，固定左侧 60px/220px
│   ├── SidebarItem.tsx        [新增] 导航单项，icon + 文字
│   └── AppLayout.tsx          [新增] Server Component，包裹全站
│
├── search/                    ← 重构
│   ├── SearchInput.tsx        [新增] "use client"，纯输入框（sm/lg 变体）
│   ├── SearchDropdown.tsx     [重构] "use client"，250ms 防抖 + 下拉面板
│   └── SearchResultCard.tsx   [重样式] 搜索结果卡片
│
├── home/                      ← 新增
│   ├── HeroSection.tsx        [新增] Server Component
│   ├── HeroMetrics.tsx        [新增] "use client"，骨架加载
│   ├── ModuleGrid.tsx         [新增] Server Component，2×2 网格
│   ├── QuickTags.tsx          [新增] Server Component，横滚标签
│   └── RecentUpdates.tsx      [新增] "use client"，3 列列表
│
├── common/                    ← 重样式
│   ├── PageHeader.tsx         [重样式] border-b 替代当前样式
│   ├── DetailPageShell.tsx    [重样式] max-w-7xl 布局
│   ├── DocumentToc.tsx        [重样式] sticky 右侧 + 活跃指示线
│   ├── RelatedResources.tsx   [重样式] divide-y 列表
│   └── MarkdownRenderer.tsx   [增强] useSerif 配置
│
├── data/                      ← 重样式 + 保留
│   ├── PipelineBrowser.tsx    [重样式] divide-y 行替代卡片
│   ├── AlgorithmBrowser.tsx   [重样式] 同上
│   ├── DatabaseBrowser.tsx    [重样式] 双栏：分类侧栏 + 列表
│   ├── SearchResults.tsx      [重样式] 统一标签
│   └── BenchmarkChart.tsx     [保留] ECharts 封装不改
│
├── Navbar.tsx                 [删除]
└── GlobalSearch.tsx           [删除]
```

**汇总:** 9 新增 + 11 重样式 + 1 保留不改 + 2 删除 = 21 组件

---

## 6. 每个模块的布局说明

### 6.1 全局布局（AppLayout）

- 桌面：侧边栏 + 主内容区（`max-w-7xl mx-auto px-8 py-8`）
- 移动：无侧边栏，底部固定 Tab bar（h-14, 5 图标+搜索），主内容 `pb-16`

### 6.2 首页

5 个区域纵向排列：
1. Hero（非对称双栏, min-h-[480px], bg-white）
2. 模块入口（2×2 不对称网格, bg-slate-50, py-16）
3. 快速入口横滚条（bg-white, py-12）
4. 最近更新（3 列, bg-white, py-12）
5. 页脚（bg-white, border-t, py-8）

### 6.3 分析流程列表页（/pipelines）

- PageHeader + 分类筛选 pill 行 + divide-y 列表
- 每行：流程名(L2) + 标签 pill(L5) + 步骤数(L5) + 描述(L4, line-clamp-2)
- 空态：Phosphor Empty 图标 + "暂无分析流程"
- 不使用卡片包裹

### 6.4 流程详情页（/pipelines/[id]）

- PageHeader(breadcrumb) + 正文(max-w-[65ch]) + DocumentToc(sticky right)
- MarkdownRenderer useSerif=false
- 移动端 DocumentToc 折叠为 `<details>`
- 底部 RelatedResources 全宽

### 6.5 软件与算法列表页（/algorithms）

- 与流程列表页布局一致
- 分类标签色使用 Tag-algorithm (indigo)
- 行末可选缩略 BenchmarkChart

### 6.6 数据库导航页（/databases）

- 桌面双栏：左侧分类栏(sticky, w-48) + 右侧列表
- 移动端分类退化为顶部横滚 pill 组
- 每行：数据库名(L2) + 分类标签(L5, Tag-database emerald) + 描述(L4)

### 6.7 文献集列表页（/literatures）

- PageHeader + 搜索框 + 年份筛选 + divide-y 列表
- 每行：标题(L2) + 作者/期刊/年份(L5) + 引用数标签(Tag-literature amber)

### 6.8 文献详情页（/literatures/[id]）

- 与流程详情页布局一致
- MarkdownRenderer useSerif=true（整站唯一衬线体位置）
- 顶部额外元信息行（作者/期刊/年份）

### 6.9 全站搜索结果页（/search?q=xxx）

- PageHeader "搜索结果: {q}" + 统计摘要 + 类型筛选 tabs + 列表
- SearchResultCard 所有类型标签统一 slate-500（无彩色）
- 每项：类型标签 + 标题(L2) + 摘要(L4, line-clamp-2)

---

## 7. 移动端适配

### 断点

| 断点 | 宽度 | 策略 |
|---|---|---|
| sm | >= 640px | 列表单列→双列 |
| md | >= 768px | 关键转折：单列→多列 |
| lg | >= 1024px | 侧边栏显示，收起/展开启用 |
| xl | >= 1280px | 全宽桌面，更宽内边距 |

### 核心策略

- 渐进增强，同一 HTML 通过 Tailwind 响应式前缀适配
- VARIANCE 4-7 的不对称布局在 < 768px 时激进回退为 `w-full` 单列
- 不做横屏适配、平板专属布局、原生手势、PWA

### 各组件移动端行为

| 组件 | 桌面 | 移动端 |
|---|---|---|
| 侧边栏 | 固定左侧 60px/220px | 隐藏，底部固定 Tab bar |
| Hero | 非对称双栏 | 单列堆叠，数据摘要横排，标题 text-3xl |
| 模块入口 | 2×2 不对称网格 | 单列等高铁卡片 |
| 快速入口 | 横滚 pill | 横滚 pill（尺寸缩小） |
| 最近更新 | 3 列 | 单列，border-b 分隔 |
| 列表页分类筛选 | 水平 pill 行 | 横滚 pill，sticky top |
| 数据库双栏 | 左分类 + 右列表 | 顶部横滚分类 pill + 全宽列表 |
| 详情页目录 | sticky 右侧 | 顶部 `<details>` 折叠 |
| 搜索弹窗 | 侧边栏内嵌 | 全屏模态框，fixed inset-0 |

### 触摸与间距

- 可点击元素最小 44×44px
- 列表行整行可点击
- 页面 px-4（移动）/ px-8（桌面），section py-8（移动）/ py-16（桌面）
- 全局最小字号 text-xs（12px）

---

## 附录: 数据获取策略

| 区域 | 获取方式 | 说明 |
|---|---|---|
| Hero 右栏指标 | SSR（fetch API） | 同现状，服务端获取 |
| 模块入口卡片内数据 | SSR | 服务端 fetch |
| 最近更新列表 | SSR | 服务端 fetch |
| 快速入口横滚标签 | 静态 | 前端预设配置 |
| Hero 搜索框 | Client | 仅输入+路由跳转，不做下拉搜索 |
| 侧边栏搜索 | Client | SearchDropdown + 防抖 |

## 附录: 实施顺序建议

1. **基础设施:** 安装 phosphor-icons，加载 Geist 字体，更新 tailwind.config.ts 颜色
2. **布局重构:** AppLayout + Sidebar（最大的结构变化）
3. **通用组件重样式:** PageHeader, DetailPageShell, MarkdownRenderer
4. **首页重写:** HeroSection, ModuleGrid, QuickTags, RecentUpdates
5. **列表页重样式:** PipelineBrowser, AlgorithmBrowser, DatabaseBrowser
6. **搜索重构:** SearchInput + SearchDropdown + SearchResultCard + SearchResults
7. **详情页调整:** DocumentToc, RelatedResources
8. **收尾:** 删除 Navbar, GlobalSearch，全局 check
