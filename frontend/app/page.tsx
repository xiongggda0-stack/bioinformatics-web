import Link from "next/link";
import { fetchDatabaseResources } from "@/lib/databaseApi";

interface FeatureCard {
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
        <div className="mx-auto grid min-h-[560px] max-w-7xl items-center gap-10 px-6 py-14 lg:grid-cols-[1.05fr_0.95fr] lg:py-16">
          <div>
            <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-teal">
              Bioinformatics Cloud MVP
            </p>
            <h1 className="max-w-3xl text-4xl font-bold leading-tight text-ink md:text-6xl">
              连接流程、软件算法与文献的一站式生信工作台
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              面向研发团队的轻量级云平台，从可复用流程开始，逐步沉淀软件工具、
              算法资产、数据库入口与文献证据链。
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/pipelines"
                className="rounded bg-teal px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-teal/90"
              >
                进入分析流程
              </Link>
              <Link
                href="/algorithms"
                className="rounded border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-teal hover:text-teal"
              >
                查看软件与算法
              </Link>
            </div>
          </div>

          <div className="rounded border border-slate-200 bg-slate-50 p-6 shadow-sm">
            <div className="border-b border-slate-200 pb-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal">
                Analysis Loop
              </p>
              <h2 className="mt-3 text-2xl font-bold tracking-tight text-ink">
                平台分析闭环
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                从选择流程到查看软件参数，再到结果解读和文献证据，形成一条可学习、
                可复用、可追溯的分析路径。
              </p>
            </div>

            <div className="mt-5 grid gap-3">
              {workflowSteps.map((step, index) => (
                <Link
                  key={step.title}
                  href={step.href}
                  className="group rounded border border-slate-200 bg-white p-4 transition hover:-translate-y-0.5 hover:border-teal hover:shadow-sm"
                >
                  <div className="flex items-start gap-4">
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded bg-teal/10 text-sm font-bold text-teal ring-1 ring-teal/20">
                      {index + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h3 className="text-sm font-semibold text-ink">
                          {step.title}
                        </h3>
                        <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-coral">
                          {step.module}
                        </span>
                      </div>
                      <p className="mt-2 text-xs leading-5 text-slate-600">
                        {step.description}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
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
                平台资产概览
              </h2>
            </div>
            <p className="max-w-2xl text-sm leading-6 text-slate-600">
              首页直接展示当前平台已经沉淀的核心资产，帮助你判断下一步应该补流程、
              补工具文档、补数据库教程，还是补文献证据。
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

      <section className="mx-auto max-w-7xl px-6 py-12">
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
              <h2 className="mt-4 text-xl font-semibold text-ink">
                {feature.title}
              </h2>
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
