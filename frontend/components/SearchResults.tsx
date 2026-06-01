import SearchResultCard from "@/components/SearchResultCard";
import type { SearchResultItem } from "@/lib/searchTypes";

interface SearchResultsProps {
  items: SearchResultItem[];
  hasQuery: boolean;
  query?: string;
}

export default function SearchResults({
  items,
  hasQuery,
  query
}: SearchResultsProps): JSX.Element {
  if (!hasQuery) {
    return (
      <div className="rounded border border-dashed border-slate-300 bg-white px-6 py-12 text-center text-sm leading-6 text-slate-500">
        输入至少 2 个字符，开始检索平台中的流程、软件、数据库、教程和文献。
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded border border-dashed border-slate-300 bg-white px-6 py-12 text-center text-sm leading-6 text-slate-500">
        暂无匹配结果。可以尝试更短的关键词，或使用 RNA-seq、Seurat、GEO、WGCNA
        等术语。
      </div>
    );
  }

  return (
    <div className="grid gap-3">
      {items.map((item) => (
        <SearchResultCard
          key={`${item.type}-${item.id}`}
          item={item}
          query={query}
        />
      ))}
    </div>
  );
}
