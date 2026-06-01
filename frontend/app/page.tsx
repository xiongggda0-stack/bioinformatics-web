import Link from "next/link";
import { fetchDatabaseResources } from "@/lib/databaseApi";

interface FeatureCard {
  title: string;
  description: string;
  href: string;
  tag: string;
}

interface ResearchScenario {
  title: string;
  description: string;
  href: string;
  tag: string;
}

interface WorkflowStep {
  title: string;
  description: string;
  href: string;
  module: string;
}

interface PlatformMetric {
  label: string;
  value: string;
  description: string;
}

interface CountableResource {
  id: number;
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

const researchScenarios: ResearchScenario[] = [
  {
    title: "Bulk RNA-seq 差异表达",
    description: "从 FASTQ、定量结果或 count matrix 开始，完成质控、统计建模与结果解读。",
    href: "/pipelines?keyword=RNA-seq",
    tag: "Transcriptomics"
  },
  {
    title: "单细胞转录组",
    description: "围绕预处理、细胞质控、聚类注释、多样本整合与高级下游组织分析。",
    href: "/pipelines?keyword=单细胞",
    tag: "Single Cell"
  },
  {
    title: "可变剪接",
    description: "定位剪接事件、差异剪接模式和适合后续解释的结果文件。",
    href: "/pipelines?keyword=可变剪接",
    tag: "RNA Structure"
  },
  {
    title: "WGCNA 共表达网络",
    description: "从表达矩阵识别共表达模块，并关联性状、时间或疾病状态。",
    href: "/pipelines?keyword=WGCNA",
    tag: "Network"
  },
  {
    title: "CUT&Tag",
    description: "完成比对、信号质控、峰识别、差异结合与功能富集分析。",
    href: "/pipelines?keyword=CUT%26Tag",
    tag: "Epigenomics"
  },
  {
    title: "BSA",
    description: "从混池测序变异检测进入 SNP-index、候选区间与突变位点定位。",
    href: "/pipelines?keyword=BSA",
    tag: "Genetics"
  },
  {
    title: "空间转录组",
    description: "结合空间坐标与表达矩阵，探索组织区域、空间特征和细胞状态。",
    href: "/pipelines?keyword=空间转录组",
    tag: "Spatial"
  },
  {
    title: "更多分析流程",
    description: "浏览肿瘤转录组、变异检测、多组学整合和非模式物种等完整流程。",
    href: "/pipelines",
    tag: "Explore"
  }
];

const features: FeatureCard[] = [
  {
    title: "分析流程",
    description:
      "集中管理 RNA-seq、单细胞、WGCNA、BSA、CUT&Tag 等标准化分析流程。",
    href: "/pipelines",
    tag: "Pipelines"
  },
  {
    title: "软件与算法",
    description:
      "沉淀常用生信软件、算法原理、输入输出、关键参数和适用场景。",
    href: "/algorithms",
    tag: "Software"
  },
  {
    title: "数据库导航",
    description:
      "按组学类型、数据对象和分析场景检索全球高质量生物数据库。",
    href: "/databases",
    tag: "Databases"
  },
  {
    title: "文献集",
    description:
      "追踪经典方法论文与前沿研究动态，让方法、证据和项目决策保持同步。",
    href: "/literatures",
    tag: "Literature"
  }
];

const workflowSteps: WorkflowStep[] = [
  {
    title: "选择分析流程",
    description:
      "从 RNA-seq、单细胞、WGCNA、BSA 等流程中选择适合项目问题的分析路径。",
    href: "/pipelines",
    module: "Pipelines"
  },
  {
    title: "查看软件与参数",
    description:
      "进入 STAR、DESeq2、Seurat、Cell Ranger 等工具文档，理解命令、输入输出和关键参数。",
    href: "/algorithms",
    module: "Software"
  },
  {
    title: "学习结果解读",
    description:
      "结合流程文档中的输出文件、图表示例和常见错误，判断结果是否可靠。",
    href: "/pipelines",
    module: "Interpretation"
  },
  {
    title: "关联文献证据",
    description:
      "把方法论文、工具来源和项目结论连接起来，形成可追溯的分析依据。",
    href: "/literatures",
    module: "Evidence"
  }
];

async function fetchResourceCount(path: string): Promise<number> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      return 0;
    }

    const data = (await response.json()) as CountableResource[];
    return Array.isArray(data) ? data.length : 0;
  } catch {
    return 0;
  }
}

async function getPlatformMetrics(): Promise<PlatformMetric[]> {
  const [pipelineCount, algorithmCount, literatureCount, databaseResources] =
    await Promise.all([
      fetchResourceCount("/api/pipelines"),
      fetchResourceCount("/api/algorithms"),
      fetchResourceCount("/api/literatures"),
      fetchDatabaseResources().catch(() => [])
    ]);
  const categoryCount = new Set(
    databaseResources.map((resource) => resource.categoryKey)
  ).size;
  const tutorialCount = databaseResources.reduce(
    (count, resource) => count + (resource.tutorials?.length ?? 0),
    0
  );

  return [
    {
      label: "分析流程",
      value: String(pipelineCount),
      description: "覆盖转录组、单细胞、表观组、变异检测和非模式物种分析。"
    },
    {
      label: "软件与算法",
      value: String(algorithmCount),
      description: "沉淀工具用法、核心参数、性能基准和适用边界。"
    },
    {
      label: "数据库资源",
      value: String(databaseResources.length),
      description: `按 ${categoryCount} 个主题分类组织公共数据入口。`
    },
    {
      label: "文献与教程",
      value: String(literatureCount + tutorialCount),
      description: "把论文证据、数据库使用示例和分析流程串成学习路径。"
    }
  ];
}

export default async function HomePage(): Promise<JSX.Element> {
  const metrics = await getPlatformMetrics();

  return (
    <main>
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-12 lg:py-14">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal">
            Bioinformatics Knowledge Platform
          </p>
          <h1 className="mt-4 max-w-4xl text-4xl font-bold leading-tight text-ink md:text-5xl">
            你正在处理哪类生物信息学数据？
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600 md:text-lg">
            从研究问题进入经过整理的分析流程，再按需查找工具参数、公共数据库和文献证据。
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              href="/pipelines"
              className="rounded bg-teal px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-teal/90"
            >
              浏览全部分析流程
            </Link>
            <Link
              href="/search"
              className="rounded border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-teal hover:text-teal"
            >
              全站检索
            </Link>
            <Link
              href="/learning-paths"
              className="rounded border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-teal hover:text-teal"
            >
              查看新手学习路径
            </Link>
          </div>

          <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {researchScenarios.map((scenario) => (
              <Link
                key={scenario.title}
                href={scenario.href}
                className="group rounded border border-slate-200 bg-slate-50 p-4 transition hover:-translate-y-0.5 hover:border-teal hover:bg-white hover:shadow-sm"
              >
                <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-coral">
                  {scenario.tag}
                </span>
                <h2 className="mt-3 text-base font-semibold text-ink transition group-hover:text-teal">
                  {scenario.title}
                </h2>
                <p className="mt-2 text-xs leading-5 text-slate-600">
                  {scenario.description}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-slate-200 bg-mist">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-end">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-coral">
                Platform Assets
              </p>
              <h2 className="mt-2 text-2xl font-bold tracking-tight text-ink">
                平台资源概览
              </h2>
            </div>
            <p className="max-w-2xl text-sm leading-6 text-slate-600">
              持续整理可公开浏览、可直接检索和可延伸学习的生物信息学知识资源。
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {metrics.map((metric) => (
              <div
                key={metric.label}
                className="rounded border border-slate-200 bg-white p-5 shadow-sm"
              >
                <p className="text-3xl font-bold text-ink">{metric.value}</p>
                <h3 className="mt-3 text-sm font-semibold text-ink">
                  {metric.label}
                </h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {metric.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal">
                Analysis Loop
              </p>
              <h2 className="mt-3 text-2xl font-bold tracking-tight text-ink">
                从流程文档走向证据链
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                选择一个可执行流程，理解软件参数和结果边界，再把分析结论连接到公开数据与文献依据。
              </p>
              <Link
                href="/learning-paths"
                className="mt-6 inline-flex text-sm font-semibold text-teal transition hover:text-teal/80"
              >
                按学习路径开始
              </Link>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {workflowSteps.map((step, index) => (
                <Link
                  key={step.title}
                  href={step.href}
                  className="group flex gap-4 rounded border border-slate-200 bg-slate-50 p-4 transition hover:border-teal hover:bg-white hover:shadow-sm"
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded bg-teal/10 text-sm font-bold text-teal ring-1 ring-teal/20">
                    {index + 1}
                  </span>
                  <span className="min-w-0">
                    <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-coral">
                      {step.module}
                    </span>
                    <span className="mt-1 block text-sm font-semibold text-ink transition group-hover:text-teal">
                      {step.title}
                    </span>
                    <span className="mt-2 block text-xs leading-5 text-slate-600">
                      {step.description}
                    </span>
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-12">
        <div className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-coral">
            Resource Hubs
          </p>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-ink">
            四类知识资源
          </h2>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {features.map((feature) => (
            <Link
              key={feature.href}
              href={feature.href}
              className="group rounded border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-teal hover:shadow-md"
            >
              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-coral">
                {feature.tag}
              </span>
              <h3 className="mt-4 text-xl font-semibold text-ink">
                {feature.title}
              </h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                {feature.description}
              </p>
              <span className="mt-6 inline-flex text-sm font-semibold text-teal">
                开始探索
              </span>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
