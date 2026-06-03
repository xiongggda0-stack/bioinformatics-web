import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import SearchResults from "@/components/SearchResults";
import { fetchSearchResults } from "@/lib/searchApi";
import type {
  SearchResourceType,
  SearchResponse
} from "@/lib/searchTypes";

interface SearchPageProps {
  searchParams?: {
    q?: string;
    type?: string;
  };
}

interface SearchTab {
  type: SearchResourceType;
  label: string;
}

const searchTabs: SearchTab[] = [
  { type: "all", label: "全部" },
  { type: "pipeline", label: "分析流程" },
  { type: "algorithm", label: "软件与算法" },
  { type: "database", label: "数据库" },
  { type: "tutorial", label: "教程" },
  { type: "literature", label: "文献" }
];

const emptyResponse: SearchResponse = {
  query: "",
  total: 0,
  counts: {
    pipeline: 0,
    algorithm: 0,
    database: 0,
    tutorial: 0,
    literature: 0
  },
  items: []
};

function resolveType(type?: string): SearchResourceType {
  return searchTabs.some((tab) => tab.type === type)
    ? (type as SearchResourceType)
    : "all";
}

function getTabCount(type: SearchResourceType, response: SearchResponse): number {
  return type === "all" ? response.total : response.counts[type];
}

export default async function SearchPage({
  searchParams
}: SearchPageProps): Promise<JSX.Element> {
  const query = searchParams?.q?.trim() ?? "";
  const type = resolveType(searchParams?.type);
  const hasQuery = query.length >= 2;
  let response = emptyResponse;
  let hasError = false;

  if (hasQuery) {
    try {
      response = await fetchSearchResults({ query, type, limit: 50 });
    } catch {
      hasError = true;
    }
  }

  return (
    <main className="min-h-screen bg-white">
      <PageHeader
        eyebrow="Search Center"
        title="全站搜索"
        description="一次检索分析流程、软件与算法、数据库资源、使用教程和文献证据。搜索结果按相关度排序，筛选状态可以通过 URL 分享。"
        stats={[
          { label: "matched", value: response.total },
          { label: "resource types", value: 5 }
        ]}
      />

      <section className="mx-auto max-w-5xl px-6 py-10">
        <form action="/search" className="flex flex-col gap-3 sm:flex-row">
          <label htmlFor="search-page-input" className="sr-only">
            搜索关键词
          </label>
          <input
            id="search-page-input"
            name="q"
            defaultValue={query}
            placeholder="输入关键词，例如 RNA-seq、Seurat、GEO、WGCNA"
            className="h-12 flex-1 rounded-md border border-slate-200 bg-slate-50 px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-accent focus:bg-white focus:ring-2 focus:ring-accent/10"
          />
          <button
            type="submit"
            className="h-12 rounded-md bg-accent px-6 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
          >
            搜索
          </button>
        </form>

        <div className="mt-6 flex gap-2 overflow-x-auto pb-1">
          {searchTabs.map((tab) => {
            const href = `/search?q=${encodeURIComponent(query)}${
              tab.type === "all" ? "" : `&type=${tab.type}`
            }`;
            const isActive = tab.type === type;

            return (
              <Link
                key={tab.type}
                href={href}
                className={`shrink-0 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-slate-900 text-white"
                    : "border border-slate-200 bg-white text-slate-600 hover:border-slate-400 hover:text-slate-900"
                }`}
              >
                {tab.label} {getTabCount(tab.type, response)}
              </Link>
            );
          })}
        </div>

        <div className="mt-6">
          {hasError ? (
            <div className="rounded-md border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              搜索服务暂时不可用，请稍后重试。
            </div>
          ) : (
            <SearchResults items={response.items} hasQuery={hasQuery} />
          )}
        </div>
      </section>
    </main>
  );
}
