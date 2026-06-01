export interface LearningPathStep {
  title: string;
  description: string;
  href: string;
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
    slug: "bulk-rna-seq",
    title: "Bulk RNA-seq 入门",
    description:
      "从原始测序数据到差异表达结果，建立一条适合首次独立分析的基础路线。",
    audience: "适合拿到 bulk RNA-seq FASTQ，希望完成质控、定量和差异表达分析的新手。",
    steps: [
      {
        title: "找到标准差异表达流程",
        description: "先理解 FASTQ、比对或准比对、计数矩阵与差异表达之间的关系。",
        href: "/pipelines?keyword=RNA-seq"
      },
      {
        title: "检索关键工具与参数",
        description: "围绕 STAR、Salmon、featureCounts 和 DESeq2 查找工具说明。",
        href: "/search?q=DESeq2"
      },
      {
        title: "补充公共数据练习素材",
        description: "从 GEO、SRA 等数据库找到可复用的表达数据和原始测序数据。",
        href: "/databases?keyword=RNA-seq"
      },
      {
        title: "回到文献理解结果边界",
        description: "通过方法论文和关联文献确认统计假设、解释范围与报告方式。",
        href: "/literatures"
      }
    ]
  },
  {
    slug: "single-cell-rna-seq",
    title: "单细胞 RNA-seq 入门",
    description:
      "从 10x 数据预处理到质控、聚类、注释和下游解释，形成单细胞分析框架。",
    audience: "适合第一次处理 10x scRNA-seq 数据，或需要系统梳理 Seurat 分析顺序的学习者。",
    steps: [
      {
        title: "定位单细胞综合流程",
        description: "了解 Cell Ranger、表达矩阵、质控、整合、聚类和注释的先后关系。",
        href: "/pipelines?keyword=单细胞"
      },
      {
        title: "检索 Seurat 与 Cell Ranger",
        description: "查看预处理和下游分析工具的输入输出、参数和适用边界。",
        href: "/search?q=Seurat"
      },
      {
        title: "查找公开单细胞数据",
        description: "使用单细胞数据库与公共存储库练习数据检索和复用。",
        href: "/databases?keyword=单细胞"
      },
      {
        title: "延伸到高级下游",
        description: "在基础分析稳定后，再进入拟时序、细胞通讯和 RNA velocity。",
        href: "/pipelines?keyword=RNA%20velocity"
      }
    ]
  },
  {
    slug: "public-data-reuse",
    title: "公共数据库数据下载与复用",
    description:
      "从研究问题出发定位数据库，判断数据层级，并把公开数据接入分析流程。",
    audience: "适合需要寻找公开数据集、复现文献结果或为新项目补充外部证据的研究者。",
    steps: [
      {
        title: "从数据库导航开始",
        description: "按组学类型和数据对象选择 GEO、SRA、TCGA 等合适入口。",
        href: "/databases"
      },
      {
        title: "检索下载与复用教程",
        description: "通过全站检索找到数据库教程、示例查询和常见数据格式说明。",
        href: "/search?q=数据下载"
      },
      {
        title: "匹配可复用分析流程",
        description: "根据 FASTQ、表达矩阵或临床数据等输入类型选择后续流程。",
        href: "/pipelines"
      }
    ]
  },
  {
    slug: "evidence-chain",
    title: "从流程文档到文献证据链",
    description:
      "把分析步骤、工具选择、数据库来源和论文依据串起来，形成可追溯的方法说明。",
    audience: "适合需要撰写方法部分、复核分析依据或整理项目交付文档的研究者。",
    steps: [
      {
        title: "从研究问题选择流程",
        description: "先明确输入、关键步骤、输出结果和需要回答的生物学问题。",
        href: "/pipelines"
      },
      {
        title: "检索工具和数据库来源",
        description: "用全站检索补齐软件参数、数据库入口和使用教程。",
        href: "/search"
      },
      {
        title: "关联方法论文",
        description: "回到文献集核对经典方法论文和相关研究证据。",
        href: "/literatures"
      },
      {
        title: "补充可复用数据入口",
        description: "记录公开数据来源，让流程文档可以复查、复现和继续扩展。",
        href: "/databases"
      }
    ]
  }
];
