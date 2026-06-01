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

const popularQueries = ["RNA-seq", "Seurat", "GEO", "WGCNA", "CUT&Tag"];

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
    <main className="min-h-screen bg-slate-50">
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
            className="h-12 flex-1 rounded border border-slate-300 bg-white px-4 text-sm text-ink outline-none transition placeholder:text-slate-400 focus:border-teal focus:ring-2 focus:ring-teal/15"
          />
          <button
            type="submit"
            className="h-12 rounded bg-teal px-6 text-sm font-semibold text-white transition hover:bg-teal/90"
          >
            搜索
          </button>
        </form>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">
            热门搜索
          </span>
          {popularQueries.map((item) => (
            <Link
              key={item}
              href={`/search?q=${encodeURIComponent(item)}`}
              className="rounded bg-white px-2.5 py-1 text-xs text-slate-600 ring-1 ring-slate-200 transition hover:text-teal hover:ring-teal"
            >
              {item}
            </Link>
          ))}
        </div>

        <p className="mt-4 text-xs leading-5 text-slate-500">
          结果按相关度排序：标题完全匹配优先，其次是标题包含、分类标签、摘要和正文命中。
        </p>

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
                className={`shrink-0 rounded px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-teal text-white"
                    : "border border-slate-200 bg-white text-slate-600 hover:border-teal hover:text-teal"
                }`}
              >
                {tab.label} {getTabCount(tab.type, response)}
              </Link>
            );
          })}
        </div>

        <div className="mt-6">
          {hasError ? (
            <div className="rounded border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
              搜索服务暂时不可用，请稍后重试。
            </div>
          ) : (
            <SearchResults
              items={response.items}
              hasQuery={hasQuery}
              query={query}
            />
          )}
        </div>
      </section>
    </main>
  );
}
