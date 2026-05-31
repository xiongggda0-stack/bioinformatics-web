"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  databaseResources,
  getAllDatabaseTutorials
} from "@/lib/databaseResources";

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface PipelineSearchItem {
  id: number;
  title: string;
  description: string;
  omics_type: string;
}

interface AlgorithmSearchItem {
  id: number;
  name: string;
  category_name: string;
  summary: string;
}

interface LiteratureSearchItem {
  id: number;
  title: string;
  journal: string;
  publication_year: number;
  abstract_text: string;
}

interface SearchResult {
  id: string;
  type: "pipeline" | "algorithm" | "database" | "tutorial" | "literature";
  label: string;
  title: string;
  description: string;
  href: string;
}

const CLIENT_API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL ?? "http://localhost:8000";

const resultTypeStyles: Record<SearchResult["type"], string> = {
  pipeline: "bg-teal/10 text-teal ring-teal/20",
  algorithm: "bg-rose-50 text-coral ring-coral/20",
  database: "bg-sky-50 text-sky-700 ring-sky-200",
  tutorial: "bg-amber-50 text-amber-700 ring-amber-200",
  literature: "bg-slate-100 text-slate-700 ring-slate-200"
};

function unwrapPayload<T>(payload: T | ApiResponse<T>): T {
  return "data" in (payload as ApiResponse<T>)
    ? (payload as ApiResponse<T>).data
    : (payload as T);
}

function includesKeyword(value: string | string[], keyword: string): boolean {
  const text = Array.isArray(value) ? value.join(" ") : value;
  return text.toLowerCase().includes(keyword.toLowerCase());
}

function limitResults<T>(items: T[], limit = 4): T[] {
  return items.slice(0, limit);
}

async function fetchJson<T>(url: string): Promise<T[]> {
  const response = await fetch(url);

  if (!response.ok) {
    return [];
  }

  return unwrapPayload((await response.json()) as T[] | ApiResponse<T[]>);
}

export default function GlobalSearch(): JSX.Element {
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const trimmedKeyword = keyword.trim();

  const staticResults = useMemo<SearchResult[]>(() => {
    if (trimmedKeyword.length < 2) {
      return [];
    }

    const databases: SearchResult[] = limitResults(
      databaseResources.filter((resource) =>
        [
          resource.name,
          resource.fullName,
          resource.categoryName,
          resource.description,
          resource.tags,
          resource.useCases
        ].some((value) => includesKeyword(value, trimmedKeyword))
      )
    ).map((resource) => ({
      id: `database-${resource.id}`,
      type: "database",
      label: "数据库",
      title: resource.name,
      description: resource.description,
      href: `/databases?keyword=${encodeURIComponent(resource.name)}`
    }));

    const tutorials: SearchResult[] = limitResults(
      getAllDatabaseTutorials().filter(({ resource, tutorial }) =>
        [
          resource.name,
          resource.categoryName,
          tutorial.title,
          tutorial.scenario,
          tutorial.steps
        ].some((value) => includesKeyword(value, trimmedKeyword))
      )
    ).map(({ resource, tutorial }) => ({
      id: `tutorial-${tutorial.id}`,
      type: "tutorial",
      label: "数据库教程",
      title: tutorial.title,
      description: `${resource.name} · ${tutorial.scenario}`,
      href: `/databases/tutorials/${tutorial.id}`
    }));

    return [...databases, ...tutorials];
  }, [trimmedKeyword]);

  useEffect(() => {
    if (trimmedKeyword.length < 2) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const controller = new AbortController();
    const query = encodeURIComponent(trimmedKeyword);

    async function runSearch(): Promise<void> {
      setIsLoading(true);

      try {
        const [pipelines, algorithms, literatures] = await Promise.all([
          fetchJson<PipelineSearchItem>(
            `${CLIENT_API_BASE_URL}/api/pipelines?keyword=${query}`
          ),
          fetchJson<AlgorithmSearchItem>(
            `${CLIENT_API_BASE_URL}/api/algorithms?keyword=${query}`
          ),
          fetchJson<LiteratureSearchItem>(
            `${CLIENT_API_BASE_URL}/api/literatures`
          )
        ]);

        if (controller.signal.aborted) {
          return;
        }

        const literatureMatches = literatures.filter((literature) =>
          [
            literature.title,
            literature.journal,
            String(literature.publication_year),
            literature.abstract_text
          ].some((value) => includesKeyword(value, trimmedKeyword))
        );

        setResults([
          ...limitResults(pipelines).map((pipeline) => ({
            id: `pipeline-${pipeline.id}`,
            type: "pipeline" as const,
            label: "分析流程",
            title: pipeline.title,
            description: `${pipeline.omics_type} · ${pipeline.description}`,
            href: `/pipelines/${pipeline.id}`
          })),
          ...limitResults(algorithms).map((algorithm) => ({
            id: `algorithm-${algorithm.id}`,
            type: "algorithm" as const,
            label: "软件与算法",
            title: algorithm.name,
            description: `${algorithm.category_name} · ${algorithm.summary}`,
            href: `/algorithms/${algorithm.id}`
          })),
          ...staticResults,
          ...limitResults(literatureMatches).map((literature) => ({
            id: `literature-${literature.id}`,
            type: "literature" as const,
            label: "文献",
            title: literature.title,
            description: `${literature.journal} · ${literature.publication_year}`,
            href: `/literatures/${literature.id}`
          }))
        ]);
      } catch {
        if (!controller.signal.aborted) {
          setResults(staticResults);
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
  }, [trimmedKeyword, staticResults]);

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
  const hasResults = results.length > 0;

  return (
    <div ref={searchRef} className="relative w-full max-w-md">
      <label htmlFor="global-search" className="sr-only">
        搜索全站内容
      </label>
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-slate-400">
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
          placeholder="搜索全站内容"
          className="h-10 w-full rounded border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm text-ink outline-none transition placeholder:text-slate-400 focus:border-teal focus:bg-white focus:ring-2 focus:ring-teal/15"
        />
      </div>

      {showPanel ? (
        <div className="absolute right-0 top-12 z-50 w-[min(92vw,36rem)] overflow-hidden rounded border border-slate-200 bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">
              Global Search
            </p>
            <Link
              href={`/pipelines?keyword=${encodeURIComponent(trimmedKeyword)}`}
              onClick={() => setIsOpen(false)}
              className="text-xs font-semibold text-slate-500 transition hover:text-teal"
            >
              查看流程搜索
            </Link>
          </div>

          <div className="max-h-[70vh] overflow-y-auto p-2">
            {isLoading ? (
              <p className="px-3 py-4 text-sm text-slate-500">正在搜索...</p>
            ) : null}

            {!isLoading && !hasResults ? (
              <p className="px-3 py-4 text-sm text-slate-500">
                没有找到匹配内容，试试 RNA-seq、Seurat、GEO、WGCNA。
              </p>
            ) : null}

            {results.map((result) => (
              <Link
                key={result.id}
                href={result.href}
                onClick={() => setIsOpen(false)}
                className="block rounded p-3 transition hover:bg-slate-50"
              >
                <div className="flex items-start gap-3">
                  <span
                    className={`mt-0.5 shrink-0 rounded px-2 py-1 text-[11px] font-semibold ring-1 ${
                      resultTypeStyles[result.type]
                    }`}
                  >
                    {result.label}
                  </span>
                  <div className="min-w-0">
                    <h3 className="truncate text-sm font-semibold text-ink">
                      {result.title}
                    </h3>
                    <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-600">
                      {result.description}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
