"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import SearchResultCard from "@/components/SearchResultCard";
import { fetchSearchResults } from "@/lib/searchApi";
import type { SearchResultItem } from "@/lib/searchTypes";

interface SearchDropdownProps {
  size: "sm" | "lg";
}

export default function SearchDropdown({ size }: SearchDropdownProps): JSX.Element {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [hasError, setHasError] = useState(false);
  const trimmedKeyword = keyword.trim();
  const searchHref = `/search?q=${encodeURIComponent(trimmedKeyword)}`;

  const height = size === "lg" ? "h-14" : "h-9";
  const textSize = size === "lg" ? "text-base" : "text-sm";

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
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const showPanel = isOpen && trimmedKeyword.length >= 2;

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <SearchIcon />
        </span>
        <input
          value={keyword}
          onChange={(e) => {
            setKeyword(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && trimmedKeyword.length >= 2) {
              setIsOpen(false);
              router.push(searchHref);
            }
            if (e.key === "Escape") {
              setIsOpen(false);
            }
          }}
          placeholder="搜索流程、软件、数据库和文献"
          className={`${height} ${textSize} w-full rounded-md border border-slate-200 bg-slate-50 pl-9 pr-3 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-accent focus:bg-white focus:ring-2 focus:ring-accent/10`}
        />
      </div>

      {showPanel ? (
        <div className="absolute right-0 top-full z-50 mt-1 w-[min(92vw,38rem)] overflow-hidden rounded-md border border-slate-200 bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
              全站搜索
            </p>
            <Link
              href={searchHref}
              onClick={() => setIsOpen(false)}
              className="text-xs font-medium text-slate-500 transition-colors hover:text-slate-700"
            >
              查看全部结果
            </Link>
          </div>

          <div className="max-h-[70vh] overflow-y-auto p-2">
            {isLoading ? (
              <p className="px-3 py-4 text-sm text-slate-400">正在搜索...</p>
            ) : null}

            {!isLoading && hasError ? (
              <p className="px-3 py-4 text-sm text-slate-400">
                搜索服务暂时不可用，请稍后重试。
              </p>
            ) : null}

            {!isLoading && !hasError && results.length === 0 ? (
              <p className="px-3 py-4 text-sm text-slate-400">
                没有找到匹配内容，试试 RNA-seq、Seurat、GEO 或 WGCNA。
              </p>
            ) : null}

            {!isLoading
              ? results.map((result) => (
                  <SearchResultCard
                    key={`${result.type}-${result.id}`}
                    item={result}
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

function SearchIcon(): JSX.Element {
  return (
    <svg width="16" height="16" viewBox="0 0 256 256" fill="currentColor">
      <path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z" />
    </svg>
  );
}
