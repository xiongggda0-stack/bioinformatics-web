import Link from "next/link";
import HeroSearch from "@/components/home/HeroSearch";
import { fetchDatabaseResources } from "@/lib/databaseApi";

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

const QUICK_TAGS = [
  { label: "RNA-seq", query: "RNA-seq" },
  { label: "Seurat", query: "Seurat" },
  { label: "GEO", query: "GEO" },
  { label: "WGCNA", query: "WGCNA" },
  { label: "DESeq2", query: "DESeq2" }
];

interface CountableResource {
  id: number;
}

async function fetchCount(path: string): Promise<number> {
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!res.ok) return 0;
    const data = (await res.json()) as CountableResource[];
    return Array.isArray(data) ? data.length : 0;
  } catch {
    return 0;
  }
}

interface Metric {
  label: string;
  value: string;
}

async function getMetrics(): Promise<Metric[]> {
  const [pipelineCount, algorithmCount, literatureCount, dbResources] =
    await Promise.all([
      fetchCount("/api/pipelines"),
      fetchCount("/api/algorithms"),
      fetchCount("/api/literatures"),
      fetchDatabaseResources().catch(() => [])
    ]);
  const tutorialCount = dbResources.reduce(
    (sum, r) => sum + (r.tutorials?.length ?? 0),
    0
  );

  return [
    { label: "分析流程", value: String(pipelineCount) },
    { label: "软件与算法", value: String(algorithmCount) },
    { label: "数据库资源", value: String(dbResources.length) },
    { label: "文献与教程", value: String(literatureCount + tutorialCount) }
  ];
}

export default async function HeroSection(): Promise<JSX.Element> {
  let metrics: Metric[];

  try {
    metrics = await getMetrics();
  } catch {
    metrics = [];
  }

  return (
    <section className="border-b border-slate-100 bg-white">
      <div className="mx-auto grid min-h-[480px] max-w-7xl items-center gap-10 px-6 py-14 lg:grid-cols-[1.05fr_0.95fr] lg:py-16">
        {/* Left column */}
        <div>
          <p className="mb-4 text-xs font-medium uppercase tracking-[0.12em] text-slate-400">
            Bioinformatics Workbench
          </p>
          <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-900 md:text-6xl">
            连接流程、软件与文献的生信工作台
          </h1>
          <p className="mt-5 max-w-[52ch] text-base leading-relaxed text-slate-500">
            从标准化分析流程开始，沉淀软件工具、算法参数与文献证据，构建可复用、可追溯的研究知识库。
          </p>

          <div className="mt-6 max-w-md">
            <HeroSearch />
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {QUICK_TAGS.map((tag) => (
              <Link
                key={tag.query}
                href={`/search?q=${encodeURIComponent(tag.query)}`}
                className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-500 transition-colors hover:border-slate-400 hover:text-slate-700"
              >
                {tag.label}
              </Link>
            ))}
          </div>
        </div>

        {/* Right column: metrics */}
        <div className="rounded-lg border border-slate-200/60 bg-white p-6">
          {metrics.length > 0 ? (
            <>
              <p className="mb-5 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
                平台资产
              </p>
              <div className="space-y-0">
                {metrics.map((m, i) => (
                  <div
                    key={m.label}
                    className={`flex items-baseline justify-between py-3 ${
                      i < metrics.length - 1 ? "border-b border-slate-100" : ""
                    }`}
                  >
                    <span className="text-xs text-slate-400">{m.label}</span>
                    <span className="text-2xl font-bold tabular-nums text-slate-900">
                      {m.value}
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-sm text-slate-400">数据加载失败</p>
          )}
        </div>
      </div>
    </section>
  );
}
