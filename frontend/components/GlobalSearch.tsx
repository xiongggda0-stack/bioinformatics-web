"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import SearchResultCard from "@/components/SearchResultCard";
import { fetchSearchResults } from "@/lib/searchApi";
import type { SearchResultItem } from "@/lib/searchTypes";

export default function GlobalSearch(): JSX.Element {
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [hasError, setHasError] = useState(false);
  const trimmedKeyword = keyword.trim();
  const searchHref = `/search?q=${encodeURIComponent(trimmedKeyword)}`;

  useEffect(() => {
    if (trimmedKeyword.length < 2) {
      setResults([]);
      setIsLoading(false);
      setHasError(false);
      return;
    }

    const controller = new AbortController();

    async function runSearch(): Promise<void> {
      setIsLoading(true);
      setHasError(false);

      try {
        const response = await fetchSearchResults({
          query: trimmedKeyword,
          limit: 8,
          clientSide: true,
          signal: controller.signal
        });

        setResults(response.items);
      } catch {
        if (!controller.signal.aborted) {
          setResults([]);
          setHasError(true);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    const timer = window.setTimeout(runSearch, 250);

    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [trimmedKeyword]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent): void {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const showPanel = isOpen && trimmedKeyword.length >= 2;

  return (
    <div ref={searchRef} className="relative w-full max-w-md">
      <label htmlFor="global-search" className="sr-only">
        搜索全站内容
      </label>
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-base text-slate-400">
          ⌕
        </span>
        <input
          id="global-search"
          value={keyword}
          onChange={(event) => {
            setKeyword(event.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && trimmedKeyword.length >= 2) {
              setIsOpen(false);
              router.push(searchHref);
            }

            if (event.key === "Escape") {
              setIsOpen(false);
            }
          }}
          placeholder="搜索流程、软件、数据库和文献"
          className="h-10 w-full rounded border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm text-ink outline-none transition placeholder:text-slate-400 focus:border-teal focus:bg-white focus:ring-2 focus:ring-teal/15"
        />
      </div>

      {showPanel ? (
        <div className="absolute right-0 top-12 z-50 w-[min(92vw,38rem)] overflow-hidden rounded border border-slate-200 bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">
              全站搜索
            </p>
            <Link
              href={searchHref}
              onClick={() => setIsOpen(false)}
              className="text-xs font-semibold text-slate-500 transition hover:text-teal"
            >
              查看全部结果
            </Link>
          </div>

          <div className="max-h-[70vh] overflow-y-auto p-2">
            {isLoading ? (
              <p className="px-3 py-4 text-sm text-slate-500">正在搜索...</p>
            ) : null}

            {!isLoading && hasError ? (
              <p className="px-3 py-4 text-sm text-slate-500">
                搜索服务暂时不可用，请稍后重试。
              </p>
            ) : null}

            {!isLoading && !hasError && results.length === 0 ? (
              <p className="px-3 py-4 text-sm text-slate-500">
                没有找到匹配内容，试试 RNA-seq、Seurat、GEO 或 WGCNA。
              </p>
            ) : null}

            {!isLoading
              ? results.map((result) => (
                  <SearchResultCard
                    key={`${result.type}-${result.id}`}
                    item={result}
                    query={trimmedKeyword}
                    compact
                    onNavigate={() => setIsOpen(false)}
                  />
                ))
              : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
