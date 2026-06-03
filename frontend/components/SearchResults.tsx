import SearchResultCard from "@/components/SearchResultCard";
import type { SearchResultItem } from "@/lib/searchTypes";

interface SearchResultsProps {
  items: SearchResultItem[];
  hasQuery: boolean;
}

export default function SearchResults({
  items,
  hasQuery
}: SearchResultsProps): JSX.Element {
  if (!hasQuery) {
    return (
      <div className="rounded-md border border-dashed border-slate-200 bg-white px-6 py-12 text-center text-sm text-slate-400">
        输入至少 2 个字符，开始检索平台中的流程、软件、数据库、教程和文献。
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-slate-200 bg-white px-6 py-12 text-center text-sm text-slate-400">
        暂无匹配结果。可以尝试更短的关键词，或使用 RNA-seq、Seurat、GEO、WGCNA 等术语。
      </div>
    );
  }

  return (
    <div className="divide-y divide-slate-100 rounded-md border border-slate-200/60 bg-white">
      {items.map((item) => (
        <SearchResultCard key={`${item.type}-${item.id}`} item={item} />
      ))}
    </div>
  );
}
