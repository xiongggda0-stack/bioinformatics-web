import Link from "next/link";
import { fetchDatabaseResources } from "@/lib/databaseApi";

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

interface ModuleCard {
  title: string;
  description: string;
  href: string;
  count: number;
}

async function fetchCount(path: string): Promise<number> {
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!res.ok) return 0;
    const data = (await res.json()) as { id: number }[];
    return Array.isArray(data) ? data.length : 0;
  } catch {
    return 0;
  }
}

async function getModules(): Promise<ModuleCard[]> {
  const [pipelineCount, algorithmCount, dbResources, literatureCount] =
    await Promise.all([
      fetchCount("/api/pipelines"),
      fetchCount("/api/algorithms"),
      fetchDatabaseResources().catch(() => []),
      fetchCount("/api/literatures")
    ]);

  return [
    {
      title: "分析流程",
      description: "集中管理 RNA-seq、单细胞、WGCNA、BSA、CUT&Tag 等标准化分析流程。",
      href: "/pipelines",
      count: pipelineCount
    },
    {
      title: "软件与算法",
      description: "沉淀常用生信软件、算法原理、输入输出、关键参数和适用场景。",
      href: "/algorithms",
      count: algorithmCount
    },
    {
      title: "数据库导航",
      description: "按组学类型、数据对象和分析场景检索全球高质量生物数据库。",
      href: "/databases",
      count: Array.isArray(dbResources) ? dbResources.length : 0
    },
    {
      title: "文献集",
      description: "追踪经典方法论文与前沿研究动态，让方法、证据和项目决策保持同步。",
      href: "/literatures",
      count: literatureCount
    }
  ];
}

export default async function ModuleGrid(): Promise<JSX.Element> {
  const modules = await getModules();
  const [pipelines, algorithms, databases, literatures] = modules;

  return (
    <section className="bg-slate-50 py-16">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-4 lg:grid-cols-[3fr_2fr]">
          {/* Pipelines - large card, spans 2 rows */}
          <Link
            href={pipelines.href}
            className="group row-span-2 rounded-lg border border-slate-200/60 bg-white p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)]"
          >
            <span className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
              Pipelines
            </span>
            <h2 className="mt-3 text-2xl font-semibold text-slate-900">
              {pipelines.title}
            </h2>
            <p className="mt-2 max-w-[48ch] text-sm leading-relaxed text-slate-500">
              {pipelines.description}
            </p>
            <p className="mt-4 text-3xl font-bold tabular-nums text-slate-900">
              {pipelines.count}
            </p>
            <span className="mt-6 inline-flex text-sm font-medium text-accent group-hover:text-accent-hover transition-colors">
              浏览流程
            </span>
          </Link>

          {/* Algorithms - top right */}
          <Link
            href={algorithms.href}
            className="group rounded-lg border border-slate-200/60 bg-white p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)]"
          >
            <span className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
              Software
            </span>
            <h2 className="mt-3 text-xl font-semibold text-slate-900">
              {algorithms.title}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-500 line-clamp-2">
              {algorithms.description}
            </p>
            <p className="mt-3 text-2xl font-bold tabular-nums text-slate-900">
              {algorithms.count}
            </p>
          </Link>

          {/* Databases - bottom right */}
          <Link
            href={databases.href}
            className="group rounded-lg border border-slate-200/60 bg-white p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)]"
          >
            <span className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
              Databases
            </span>
            <h2 className="mt-3 text-xl font-semibold text-slate-900">
              {databases.title}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-500 line-clamp-2">
              {databases.description}
            </p>
            <p className="mt-3 text-2xl font-bold tabular-nums text-slate-900">
              {databases.count}
            </p>
          </Link>
        </div>

        {/* Literatures - full width bottom */}
        <div className="mt-4">
          <Link
            href={literatures.href}
            className="group block rounded-lg border border-slate-200/60 bg-white p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)]"
          >
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <span className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
                  Literature
                </span>
                <h2 className="mt-2 text-2xl font-semibold text-slate-900">
                  {literatures.title}
                </h2>
                <p className="mt-2 max-w-[56ch] text-sm leading-relaxed text-slate-500">
                  {literatures.description}
                </p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold tabular-nums text-slate-900">
                  {literatures.count}
                </p>
                <span className="text-sm font-medium text-accent group-hover:text-accent-hover transition-colors">
                  浏览文献
                </span>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </section>
  );
}
