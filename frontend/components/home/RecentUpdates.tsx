import Link from "next/link";

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

interface RecentItem {
  title: string;
  href: string;
}

async function fetchRecent(
  path: string,
  limit: number
): Promise<RecentItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!res.ok) return [];
    const data = (await res.json()) as { title?: string; name?: string; id: number }[];
    return data.slice(0, limit).map((item) => ({
      title: item.title ?? item.name ?? String(item.id),
      href: `${path}/${item.id}`
    }));
  } catch {
    return [];
  }
}

export default async function RecentUpdates(): Promise<JSX.Element> {
  const [pipelines, algorithms, databases] = await Promise.all([
    fetchRecent("/api/pipelines", 3),
    fetchRecent("/api/algorithms", 3),
    fetchRecent("/api/databases", 3)
  ]);

  const columns = [
    { title: "最新流程", items: pipelines },
    { title: "新增工具", items: algorithms },
    { title: "数据库更新", items: databases }
  ];

  return (
    <section className="bg-white py-12">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-8 md:grid-cols-3">
          {columns.map((col) => (
            <div key={col.title}>
              <h3 className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
                {col.title}
              </h3>
              {col.items.length === 0 ? (
                <p className="mt-3 text-sm text-slate-400">暂无数据</p>
              ) : (
                <ul className="mt-3 space-y-2">
                  {col.items.map((item) => (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className="block text-sm text-slate-600 transition-colors hover:text-slate-900"
                      >
                        {item.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
