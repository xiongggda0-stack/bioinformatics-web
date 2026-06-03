"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState, useTransition } from "react";

export interface Algorithm {
  id: number;
  name: string;
  category: string;
  category_key: string;
  category_name: string;
  tool_type: string;
  summary: string;
  performance_json: Record<string, unknown>;
  markdown_docs: string;
  created_at: string;
}

export interface AlgorithmFilters {
  keyword: string;
  category: string;
}

interface AlgorithmBrowserProps {
  algorithms: Algorithm[];
  allAlgorithms: Algorithm[];
  initialFilters: AlgorithmFilters;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface AlgorithmGroup {
  key: string;
  title: string;
  description: string;
  algorithms: Algorithm[];
}

const CLIENT_API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL ?? "http://localhost:8000";

const defaultFilters: AlgorithmFilters = {
  keyword: "",
  category: "all"
};

const categoryDescriptions: Record<string, string> = {
  alignment: "基因组和转录组 reads 比对、索引构建、剪接感知定位，是多数测序流程的入口层。",
  quantification: "从 FASTQ 或 BAM 汇总表达量，输出 transcript/gene count、TPM 或矩阵。",
  "differential-expression": "对 count matrix 建模，识别差异表达基因、效应量和显著性。",
  "single-cell": "覆盖单细胞预处理、整合、聚类、拟时序、通讯和 RNA velocity。",
  "variant-calling": "从基因组比对结果中识别 SNV、Indel 等遗传变异。",
  epigenomics: "处理 ChIP-seq、CUT&Tag、CUT&RUN 等表观组学富集区域。",
  "enrichment-network": "面向基因集解释、通路富集、共表达网络和 hub gene 发现。",
  other: "暂未归入固定体系的补充软件或算法。"
};

const categoryStyles: Record<string, string> = {
  alignment: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  quantification: "bg-cyan-50 text-cyan-700 ring-cyan-200",
  "differential-expression": "bg-rose-50 text-rose-700 ring-rose-200",
  "single-cell": "bg-sky-50 text-sky-700 ring-sky-200",
  "variant-calling": "bg-violet-50 text-violet-700 ring-violet-200",
  epigenomics: "bg-amber-50 text-amber-700 ring-amber-200",
  "enrichment-network": "bg-lime-50 text-lime-700 ring-lime-200",
  other: "bg-slate-100 text-slate-700 ring-slate-200"
};

function getCategoryStyle(categoryKey: string): string {
  return categoryStyles[categoryKey] ?? categoryStyles.other;
}

function getCategoryOptions(algorithms: Algorithm[]): Array<{ key: string; name: string }> {
  const categories = new Map<string, string>();

  for (const algorithm of algorithms) {
    if (algorithm.category_key && algorithm.category_name) {
      categories.set(algorithm.category_key, algorithm.category_name);
    }
  }

  return Array.from(categories.entries()).map(([key, name]) => ({ key, name }));
}

function groupAlgorithms(algorithms: Algorithm[]): AlgorithmGroup[] {
  const grouped = new Map<string, Algorithm[]>();

  for (const algorithm of algorithms) {
    const key = algorithm.category_key || "other";
    grouped.set(key, [...(grouped.get(key) ?? []), algorithm]);
  }

  return Array.from(grouped.entries()).map(([key, groupedAlgorithms]) => ({
    key,
    title: groupedAlgorithms[0]?.category_name ?? "其他软件与算法",
    description: categoryDescriptions[key] ?? categoryDescriptions.other,
    algorithms: groupedAlgorithms
  }));
}

function filtersFromSearchParams(searchParams: URLSearchParams): AlgorithmFilters {
  return {
    keyword: searchParams.get("keyword") ?? "",
    category: searchParams.get("category") ?? "all"
  };
}

function buildBackendQuery(filters: AlgorithmFilters): string {
  const params = new URLSearchParams();

  if (filters.keyword.trim()) {
    params.set("keyword", filters.keyword.trim());
  }

  if (filters.category && filters.category !== "all") {
    params.set("category_key", filters.category);
  }

  params.set("limit", "200");
  return params.toString();
}

async function fetchFilteredAlgorithms(filters: AlgorithmFilters): Promise<Algorithm[]> {
  const response = await fetch(
    `${CLIENT_API_BASE_URL}/api/algorithms?${buildBackendQuery(filters)}`
  );

  if (!response.ok) {
    return [];
  }

  const payload = (await response.json()) as Algorithm[] | ApiResponse<Algorithm[]>;
  return Array.isArray(payload) ? payload : payload.data ?? [];
}

export default function AlgorithmBrowser({
  algorithms,
  allAlgorithms,
  initialFilters
}: AlgorithmBrowserProps): JSX.Element {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [isFetching, setIsFetching] = useState<boolean>(false);
  const [serverAlgorithms, setServerAlgorithms] = useState<Algorithm[]>(algorithms);
  const [filters, setFilters] = useState<AlgorithmFilters>({
    ...defaultFilters,
    ...initialFilters,
    category: initialFilters.category || "all"
  });

  useEffect(() => {
    const nextFilters = filtersFromSearchParams(searchParams);
    let ignore = false;

    setFilters(nextFilters);
    setIsFetching(true);

    fetchFilteredAlgorithms(nextFilters)
      .then((nextAlgorithms) => {
        if (!ignore) {
          setServerAlgorithms(nextAlgorithms);
        }
      })
      .catch(() => {
        if (!ignore) {
          setServerAlgorithms([]);
        }
      })
      .finally(() => {
        if (!ignore) {
          setIsFetching(false);
        }
      });

    return () => {
      ignore = true;
    };
  }, [searchParams]);

  function pushFilters(nextFilters: AlgorithmFilters): void {
    const params = new URLSearchParams(searchParams.toString());

    if (nextFilters.keyword.trim()) {
      params.set("keyword", nextFilters.keyword.trim());
    } else {
      params.delete("keyword");
    }

    if (nextFilters.category && nextFilters.category !== "all") {
      params.set("category", nextFilters.category);
    } else {
      params.delete("category");
    }

    const query = params.toString();
    startTransition(() => {
      router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
    });
  }

  function updateFilter<K extends keyof AlgorithmFilters>(
    key: K,
    value: AlgorithmFilters[K]
  ): void {
    const nextFilters = { ...filters, [key]: value };
    setFilters(nextFilters);
    pushFilters(nextFilters);
  }

  function resetFilters(): void {
    setFilters(defaultFilters);
    pushFilters(defaultFilters);
  }

  const optionSource = allAlgorithms.length > 0 ? allAlgorithms : algorithms;
  const categoryOptions = useMemo(() => getCategoryOptions(optionSource), [optionSource]);
  const groups = useMemo(() => groupAlgorithms(serverAlgorithms), [serverAlgorithms]);
  const activeFilterCount =
    Number(filters.keyword.trim().length > 0) + Number(filters.category !== "all");

  return (
    <div className="space-y-8">
      <section className="rounded-md border border-slate-200/60 bg-white p-5">
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_260px_auto] lg:items-end">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">搜索软件与算法</span>
            <input
              value={filters.keyword}
              onChange={(event) => updateFilter("keyword", event.target.value)}
              placeholder="输入关键词，例如 STAR、DESeq2、Seurat、WGCNA、peak calling"
              className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-slate-50 px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-accent focus:bg-white focus:ring-2 focus:ring-accent/10"
            />
          </label>

          <FilterSelect
            label="软件分类"
            value={filters.category}
            options={categoryOptions.map((category) => ({
              value: category.key,
              label: category.name
            }))}
            placeholder="全部分类"
            onChange={(value) => updateFilter("category", value || "all")}
          />

          <button
            type="button"
            onClick={resetFilters}
            className="h-10 rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-600 transition-colors hover:border-slate-400 hover:text-slate-900"
          >
            重置筛选
          </button>
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 text-sm text-slate-500">
          <p>
            当前显示{" "}
            <span className="font-medium text-slate-900">{serverAlgorithms.length}</span> /{" "}
            <span className="font-medium text-slate-900">{allAlgorithms.length}</span> 个软件与算法
          </p>
          <div className="flex items-center gap-2">
            {activeFilterCount > 0 ? (
              <span className="rounded-full bg-accent-subtle px-2.5 py-0.5 text-xs font-medium text-accent">
                {activeFilterCount} 个筛选条件
              </span>
            ) : null}
            {isPending ? (
              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500">
                正在同步 URL...
              </span>
            ) : null}
            {isFetching ? (
              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500">
                正在查询后端...
              </span>
            ) : null}
          </div>
        </div>
      </section>

      {serverAlgorithms.length === 0 ? (
        <div className="rounded-md border border-dashed border-slate-200 bg-white p-10 text-center">
          <h2 className="text-lg font-semibold text-slate-900">没有匹配的软件与算法</h2>
          <p className="mt-2 text-sm text-slate-500">
            换一个关键词，或清空分类筛选条件后再试。
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {groups.map((group) => (
            <section key={group.key}>
              <div className="mb-5 flex flex-wrap items-end justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900">
                    {group.title}
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-500">
                    {group.description}
                  </p>
                </div>
                <span className="text-xs font-medium text-slate-400">
                  {group.algorithms.length} tools
                </span>
              </div>

              <div className="divide-y divide-slate-100 rounded-md border border-slate-200/60 bg-white">
                {group.algorithms.map((algorithm) => (
                  <AlgorithmRow key={algorithm.id} algorithm={algorithm} />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

function FilterSelect({
  label,
  value,
  options,
  placeholder,
  onChange
}: {
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  placeholder: string;
  onChange: (value: string) => void;
}): JSX.Element {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
        {label}
      </span>
      <select
        value={value === "all" ? "" : value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function AlgorithmRow({ algorithm }: { algorithm: Algorithm }): JSX.Element {
  return (
    <Link
      href={`/algorithms/${algorithm.id}`}
      className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-slate-50"
    >
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="text-base font-semibold text-slate-900">
            {algorithm.name}
          </h3>
          <span className="shrink-0 rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-500">
            {algorithm.category_name}
          </span>
          <span className="shrink-0 rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-500">
            {algorithm.tool_type}
          </span>
        </div>
        <p className="mt-1 line-clamp-1 text-sm text-slate-500">
          {algorithm.summary}
        </p>
      </div>
      <span className="shrink-0 text-xs text-slate-400">
        {new Date(algorithm.created_at).toLocaleDateString("zh-CN")}
      </span>
    </Link>
  );
}
