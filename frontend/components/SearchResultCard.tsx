import Link from "next/link";
import type { SearchItemType, SearchResultItem } from "@/lib/searchTypes";

interface SearchResultCardProps {
  item: SearchResultItem;
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

export default function SearchResultCard({
  item,
  compact = false,
  onNavigate
}: SearchResultCardProps): JSX.Element {
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      className={`block rounded-md transition-colors hover:bg-slate-50 ${
        compact ? "p-3" : "p-4"
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 shrink-0 rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-500">
          {resultTypeLabels[item.type]}
        </span>
        <div className="min-w-0">
          <h2
            className={`font-semibold text-slate-900 ${
              compact ? "truncate text-sm" : "text-base"
            }`}
          >
            {item.title}
          </h2>
          <p
            className={`mt-1 text-slate-500 ${
              compact
                ? "line-clamp-2 text-xs leading-5"
                : "line-clamp-3 text-sm leading-6"
            }`}
          >
            {item.description}
          </p>

          {!compact && item.tags.length > 0 ? (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {item.tags.slice(0, 5).map((tag) => (
                <span
                  key={tag}
                  className="rounded bg-slate-50 px-2 py-0.5 text-xs text-slate-500"
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
