import Link from "next/link";
import PageHeader from "@/components/PageHeader";

interface Literature {
  id: number;
  title: string;
  authors: string[];
  journal: string;
  publication_year: number;
  doi: string;
  abstract_text: string;
  pipeline_id: number | null;
  algorithm_id: number | null;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

async function fetchLiteratures(): Promise<Literature[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/literatures`, {
      cache: "no-store"
    });

    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as Literature[] | ApiResponse<Literature[]>;
    return Array.isArray(payload) ? payload : payload.data ?? [];
  } catch {
    return [];
  }
}

export default async function LiteraturesPage(): Promise<JSX.Element> {
  const literatures = await fetchLiteratures();

  return (
    <main className="min-h-screen bg-white">
      <PageHeader
        eyebrow="Literature Hub"
        title="文献与动态集"
        description="将经典方法论文与平台内的分析流程、软件算法和数据库教程相互关联，形成可追溯的证据链。"
        stats={[
          { label: "papers", value: literatures.length },
          {
            label: "linked",
            value: literatures.filter(
              (item) => item.pipeline_id !== null || item.algorithm_id !== null
            ).length
          }
        ]}
      />

      <section className="mx-auto max-w-5xl px-6 py-10">
        {literatures.length === 0 ? (
          <div className="rounded-md border border-dashed border-slate-200 bg-white p-10 text-center">
            <h2 className="text-lg font-semibold text-slate-900">暂无文献数据</h2>
            <p className="mt-2 text-sm text-slate-500">
              请确认 FastAPI 服务已启动，并执行初始化脚本写入 Literature mock 数据。
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 rounded-md border border-slate-200/60 bg-white">
            {literatures.map((literature) => (
              <Link
                key={literature.id}
                href={`/literatures/${literature.id}`}
                className="block px-6 py-5 transition-colors hover:bg-slate-50"
              >
                <div className="flex flex-wrap items-center gap-3 text-sm">
                  <span className="font-medium text-accent">{literature.journal}</span>
                  <span className="text-slate-200">/</span>
                  <span className="text-slate-400">
                    {literature.publication_year}
                  </span>
                </div>
                <h2 className="mt-2 text-lg font-semibold text-slate-900">
                  {literature.title}
                </h2>
                <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-slate-500">
                  {literature.abstract_text}
                </p>
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  <span>{literature.authors.slice(0, 3).join(", ")}</span>
                  {literature.authors.length > 3 ? <span>et al.</span> : null}
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
