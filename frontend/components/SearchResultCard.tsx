import Link from "next/link";
import SearchHighlight from "@/components/SearchHighlight";
import type { SearchItemType, SearchResultItem } from "@/lib/searchTypes";

interface SearchResultCardProps {
  item: SearchResultItem;
  query?: string;
  compact?: boolean;
  onNavigate?: () => void;
}

const resultTypeLabels: Record<SearchItemType, string> = {
  pipeline: "分析流程",
  algorithm: "软件与算法",
  database: "数据库",
  tutorial: "数据库教程",
  literature: "文献"
};

const resultTypeStyles: Record<SearchItemType, string> = {
  pipeline: "bg-teal/10 text-teal ring-teal/20",
  algorithm: "bg-rose-50 text-coral ring-coral/20",
  database: "bg-sky-50 text-sky-700 ring-sky-200",
  tutorial: "bg-amber-50 text-amber-700 ring-amber-200",
  literature: "bg-slate-100 text-slate-700 ring-slate-200"
};

export default function SearchResultCard({
  item,
  query,
  compact = false,
  onNavigate
}: SearchResultCardProps): JSX.Element {
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      className={`block rounded border border-transparent transition hover:border-slate-200 hover:bg-slate-50 ${
        compact ? "p-3" : "bg-white p-5 shadow-sm"
      }`}
    >
      <div className="flex items-start gap-3">
        <span
          className={`mt-0.5 shrink-0 rounded px-2 py-1 text-[11px] font-semibold ring-1 ${resultTypeStyles[item.type]}`}
        >
          {resultTypeLabels[item.type]}
        </span>
        <div className="min-w-0">
          <h2
            className={`font-semibold text-ink ${
              compact ? "truncate text-sm" : "text-base"
            }`}
          >
            <SearchHighlight text={item.title} query={query} />
          </h2>
          <p
            className={`mt-1 text-slate-600 ${
              compact
                ? "line-clamp-2 text-xs leading-5"
                : "line-clamp-3 text-sm leading-6"
            }`}
          >
            <SearchHighlight text={item.description} query={query} />
          </p>

          {!compact && item.tags.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {item.tags.slice(0, 5).map((tag) => (
                <span
                  key={tag}
                  className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-500"
                >
                  {tag}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </Link>
  );
}
