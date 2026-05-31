"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState, useTransition } from "react";

export interface Pipeline {
  id: number;
  title: string;
  description: string;
  omics_type: string;
  category_key: string;
  category_name: string;
  dag_json: Record<string, unknown>;
  metadata_json: PipelineMetadata;
  content: string;
  created_at: string;
}

export interface PipelineFilters {
  keyword: string;
  category: string;
  omics_type: string;
  difficulty: string;
  tool: string;
  input_type: string;
  output_type: string;
  scenario: string;
}

interface PipelineMetadata {
  difficulty?: string;
  tools?: string[];
  inputs?: string[];
  outputs?: string[];
  estimated_time?: string;
  scenario?: string;
}

interface PipelineGroup {
  key: string;
  title: string;
  description: string;
  pipelines: Pipeline[];
}

interface PipelineBrowserProps {
  pipelines: Pipeline[];
  allPipelines: Pipeline[];
  initialFilters: PipelineFilters;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

const CLIENT_API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL ?? "http://localhost:8000";

const defaultFilters: PipelineFilters = {
  keyword: "",
  category: "all",
  omics_type: "",
  difficulty: "",
  tool: "",
  input_type: "",
  output_type: "",
  scenario: ""
};

const urlFilterKeys = Object.keys(defaultFilters) as Array<keyof PipelineFilters>;
const backendFilterKeys: Array<Exclude<keyof PipelineFilters, "category">> = [
  "keyword",
  "omics_type",
  "difficulty",
  "tool",
  "input_type",
  "output_type",
  "scenario"
];

const omicsStyles: Record<string, string> = {
  "RNA-Seq": "bg-emerald-50 text-emerald-700 ring-emerald-200",
  "scRNA-Seq": "bg-sky-50 text-sky-700 ring-sky-200",
  "CUT&Tag": "bg-amber-50 text-amber-700 ring-amber-200",
  "BSA-seq": "bg-rose-50 text-rose-700 ring-rose-200",
  "Spatial Transcriptomics": "bg-indigo-50 text-indigo-700 ring-indigo-200",
  "Multi-omics": "bg-fuchsia-50 text-fuchsia-700 ring-fuchsia-200",
  "Regulatory Network": "bg-cyan-50 text-cyan-700 ring-cyan-200",
  "Pathway Analysis": "bg-lime-50 text-lime-700 ring-lime-200",
  Immunogenomics: "bg-orange-50 text-orange-700 ring-orange-200",
  "Cancer Transcriptomics": "bg-red-50 text-red-700 ring-red-200",
  "Long-read Transcriptomics": "bg-teal-50 text-teal-700 ring-teal-200",
  Translatomics: "bg-pink-50 text-pink-700 ring-pink-200",
  "De novo Transcriptomics": "bg-stone-100 text-stone-700 ring-stone-300",
  WGS: "bg-violet-50 text-violet-700 ring-violet-200"
};

const categoryDescriptions: Record<string, string> = {
  basic: "常规 RNA-seq 表达定量、差异表达、时间动态和非编码 RNA 分析。",
  structure: "可变剪接、RNA editing、共表达模块和动态调控网络。",
  mechanism: "整合染色质、转录因子、通路活性和免疫浸润。",
  cancer: "肿瘤 RNA-seq 综合分析、融合基因检测和临床解释。",
  "advanced-transcriptomics": "长读长 isoform discovery、Ribo-seq 和 Trinity de novo 组装。",
  "single-spatial": "scRNA-seq 基础分析、高级下游和 Visium 空间转录组。",
  variant: "WGS 变异检测、BSA-seq 定位和突变候选区域分析。",
  epigenomics: "CUT&Tag 等染色质结合与组蛋白修饰分析流程。",
  other: "暂未归入固定方向的补充流程。"
};

function getOmicsStyle(omicsType: string): string {
  return omicsStyles[omicsType] ?? "bg-slate-100 text-slate-700 ring-slate-200";
}

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean))).sort((a, b) =>
    a.localeCompare(b, "zh-CN")
  );
}

function flattenMetadata(
  pipelines: Pipeline[],
  key: "tools" | "inputs" | "outputs"
): string[] {
  return pipelines.flatMap((pipeline) => pipeline.metadata_json[key] ?? []);
}

function getCategoryOptions(pipelines: Pipeline[]): Array<{ key: string; name: string }> {
  const categories = new Map<string, string>();

  for (const pipeline of pipelines) {
    if (pipeline.category_key && pipeline.category_name) {
      categories.set(pipeline.category_key, pipeline.category_name);
    }
  }

  return Array.from(categories.entries()).map(([key, name]) => ({ key, name }));
}

function groupPipelines(pipelines: Pipeline[]): PipelineGroup[] {
  const grouped = new Map<string, Pipeline[]>();

  for (const pipeline of pipelines) {
    const key = pipeline.category_key || "other";
    grouped.set(key, [...(grouped.get(key) ?? []), pipeline]);
  }

  return Array.from(grouped.entries()).map(([key, groupedPipelines]) => ({
    key,
    title: groupedPipelines[0]?.category_name ?? "其他分析流程",
    description: categoryDescriptions[key] ?? categoryDescriptions.other,
    pipelines: groupedPipelines
  }));
}

function filtersFromSearchParams(searchParams: URLSearchParams): PipelineFilters {
  return {
    keyword: searchParams.get("keyword") ?? "",
    category: searchParams.get("category") ?? "all",
    omics_type: searchParams.get("omics_type") ?? "",
    difficulty: searchParams.get("difficulty") ?? "",
    tool: searchParams.get("tool") ?? "",
    input_type: searchParams.get("input_type") ?? "",
    output_type: searchParams.get("output_type") ?? "",
    scenario: searchParams.get("scenario") ?? ""
  };
}

function buildBackendQuery(filters: PipelineFilters): string {
  const params = new URLSearchParams();

  for (const key of backendFilterKeys) {
    const value = filters[key].trim();
    if (value) {
      params.set(key, value);
    }
  }

  if (filters.category && filters.category !== "all") {
    params.set("category_key", filters.category);
  }

  params.set("limit", "200");
  return params.toString();
}

function getActiveFilterCount(filters: PipelineFilters): number {
  return urlFilterKeys.filter((key) => {
    if (key === "category") {
      return filters.category !== "all";
    }
    return filters[key].trim().length > 0;
  }).length;
}

async function fetchFilteredPipelines(filters: PipelineFilters): Promise<Pipeline[]> {
  const response = await fetch(
    `${CLIENT_API_BASE_URL}/api/pipelines?${buildBackendQuery(filters)}`
  );

  if (!response.ok) {
    return [];
  }

  const payload = (await response.json()) as Pipeline[] | ApiResponse<Pipeline[]>;
  return Array.isArray(payload) ? payload : payload.data ?? [];
}

export default function PipelineBrowser({
  pipelines,
  allPipelines,
  initialFilters
}: PipelineBrowserProps): JSX.Element {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [isFetching, setIsFetching] = useState<boolean>(false);
  const [serverPipelines, setServerPipelines] = useState<Pipeline[]>(pipelines);
  const [filters, setFilters] = useState<PipelineFilters>({
    ...defaultFilters,
    ...initialFilters,
    category: initialFilters.category || "all"
  });

  useEffect(() => {
    const nextFilters = filtersFromSearchParams(searchParams);
    let ignore = false;

    setFilters(nextFilters);
    setIsFetching(true);

    fetchFilteredPipelines(nextFilters)
      .then((nextPipelines) => {
        if (!ignore) {
          setServerPipelines(nextPipelines);
        }
      })
      .catch(() => {
        if (!ignore) {
          setServerPipelines([]);
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

  function pushFilters(nextFilters: PipelineFilters): void {
    const params = new URLSearchParams(searchParams.toString());

    for (const key of urlFilterKeys) {
      const value = nextFilters[key].trim();
      if (!value || (key === "category" && value === "all")) {
        params.delete(key);
      } else {
        params.set(key, value);
      }
    }

    const query = params.toString();
    startTransition(() => {
      router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
    });
  }

  function updateFilter<K extends keyof PipelineFilters>(
    key: K,
    value: PipelineFilters[K]
  ): void {
    const nextFilters = { ...filters, [key]: value };
    setFilters(nextFilters);
    pushFilters(nextFilters);
  }

  function resetFilters(): void {
    setFilters(defaultFilters);
    pushFilters(defaultFilters);
  }

  const optionSource = allPipelines.length > 0 ? allPipelines : pipelines;
  const categoryOptions = useMemo(() => getCategoryOptions(optionSource), [optionSource]);
  const omicsTypes = useMemo(
    () => uniqueSorted(optionSource.map((pipeline) => pipeline.omics_type)),
    [optionSource]
  );
  const difficulties = useMemo(
    () => uniqueSorted(optionSource.map((pipeline) => pipeline.metadata_json.difficulty ?? "")),
    [optionSource]
  );
  const tools = useMemo(
    () => uniqueSorted(flattenMetadata(optionSource, "tools")),
    [optionSource]
  );
  const inputTypes = useMemo(
    () => uniqueSorted(flattenMetadata(optionSource, "inputs")),
    [optionSource]
  );
  const outputTypes = useMemo(
    () => uniqueSorted(flattenMetadata(optionSource, "outputs")),
    [optionSource]
  );
  const scenarios = useMemo(
    () => uniqueSorted(optionSource.map((pipeline) => pipeline.metadata_json.scenario ?? "")),
    [optionSource]
  );

  const visiblePipelines = serverPipelines;
  const groups = useMemo(() => groupPipelines(visiblePipelines), [visiblePipelines]);
  const activeFilterCount = getActiveFilterCount(filters);

  return (
    <div className="space-y-8">
      <section className="rounded border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
          <label className="block">
            <span className="text-sm font-semibold text-ink">搜索流程</span>
            <input
              value={filters.keyword}
              onChange={(event) => updateFilter("keyword", event.target.value)}
              placeholder="输入关键词，例如 DESeq2、WGCNA、肿瘤、单细胞、Trinity"
              className="mt-2 h-11 w-full rounded border border-slate-300 bg-white px-4 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-teal focus:ring-2 focus:ring-teal/20"
            />
          </label>
          <button
            type="button"
            onClick={resetFilters}
            className="h-11 rounded border border-slate-300 bg-slate-50 px-4 text-sm font-semibold text-slate-700 transition hover:border-teal hover:bg-white hover:text-teal"
          >
            重置筛选
          </button>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <FilterSelect
            label="流程分类"
            value={filters.category}
            options={categoryOptions.map((category) => ({
              value: category.key,
              label: category.name
            }))}
            placeholder="全部分类"
            onChange={(value) => updateFilter("category", value || "all")}
          />
          <FilterSelect
            label="组学 / 模块"
            value={filters.omics_type}
            options={omicsTypes.map((value) => ({ value, label: value }))}
            placeholder="全部模块"
            onChange={(value) => updateFilter("omics_type", value)}
          />
          <FilterSelect
            label="难度"
            value={filters.difficulty}
            options={difficulties.map((value) => ({ value, label: value }))}
            placeholder="全部难度"
            onChange={(value) => updateFilter("difficulty", value)}
          />
          <FilterSelect
            label="工具"
            value={filters.tool}
            options={tools.map((value) => ({ value, label: value }))}
            placeholder="全部工具"
            onChange={(value) => updateFilter("tool", value)}
          />
          <FilterSelect
            label="输入数据"
            value={filters.input_type}
            options={inputTypes.map((value) => ({ value, label: value }))}
            placeholder="全部输入"
            onChange={(value) => updateFilter("input_type", value)}
          />
          <FilterSelect
            label="输出结果"
            value={filters.output_type}
            options={outputTypes.map((value) => ({ value, label: value }))}
            placeholder="全部输出"
            onChange={(value) => updateFilter("output_type", value)}
          />
          <FilterSelect
            label="应用场景"
            value={filters.scenario}
            options={scenarios.map((value) => ({ value, label: value }))}
            placeholder="全部场景"
            onChange={(value) => updateFilter("scenario", value)}
          />
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 text-sm text-slate-600">
          <p>
            当前显示{" "}
            <span className="font-semibold text-ink">{visiblePipelines.length}</span> /{" "}
            <span className="font-semibold text-ink">{allPipelines.length}</span> 个流程
          </p>
          <div className="flex items-center gap-2">
            {activeFilterCount > 0 ? (
              <span className="rounded bg-teal/10 px-2.5 py-1 text-xs font-semibold text-teal">
                {activeFilterCount} 个筛选条件
              </span>
            ) : null}
            {isPending ? (
              <span className="rounded bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-500">
                正在同步 URL...
              </span>
            ) : null}
            {isFetching ? (
              <span className="rounded bg-sky-50 px-2.5 py-1 text-xs font-semibold text-sky-700">
                正在查询后端...
              </span>
            ) : null}
          </div>
        </div>
      </section>

      {visiblePipelines.length === 0 ? (
        <div className="rounded border border-dashed border-slate-300 bg-white p-10 text-center">
          <h2 className="text-lg font-semibold text-ink">没有匹配的流程</h2>
          <p className="mt-2 text-sm text-slate-500">
            换一个关键词，或清空分类、标签、工具等筛选条件。
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {groups.map((group) => (
            <section key={group.key}>
              <div className="mb-5 flex flex-wrap items-end justify-between gap-4 border-b border-slate-200 pb-4">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight text-ink">
                    {group.title}
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                    {group.description}
                  </p>
                </div>
                <span className="rounded bg-white px-3 py-1 text-xs font-semibold text-slate-500 ring-1 ring-slate-200">
                  {group.pipelines.length} workflows
                </span>
              </div>
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {group.pipelines.map((pipeline) => (
                  <PipelineCard key={pipeline.id} pipeline={pipeline} />
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
      <span className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        {label}
      </span>
      <select
        value={value === "all" ? "" : value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 h-10 w-full rounded border border-slate-300 bg-white px-3 text-sm text-slate-800 outline-none transition focus:border-teal focus:ring-2 focus:ring-teal/20"
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

function PipelineCard({ pipeline }: { pipeline: Pipeline }): JSX.Element {
  return (
    <Link
      href={`/pipelines/${pipeline.id}`}
      className="group rounded border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-teal hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-wrap gap-2">
          <span
            className={`inline-flex rounded px-3 py-1 text-xs font-semibold ring-1 ${getOmicsStyle(
              pipeline.omics_type
            )}`}
          >
            {pipeline.omics_type}
          </span>
          <span className="inline-flex rounded bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 ring-1 ring-slate-200">
            {pipeline.category_name}
          </span>
          {pipeline.metadata_json.difficulty ? (
            <span className="inline-flex rounded bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 ring-1 ring-slate-200">
              {pipeline.metadata_json.difficulty}
            </span>
          ) : null}
        </div>
        <span className="text-xs text-slate-400">#{pipeline.id}</span>
      </div>
      <h3 className="mt-5 text-xl font-semibold leading-7 text-ink">
        {pipeline.title}
      </h3>
      <p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-600">
        {pipeline.description}
      </p>
      {pipeline.metadata_json.tools?.length ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {pipeline.metadata_json.tools.slice(0, 4).map((tool) => (
            <span
              key={tool}
              className="rounded bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700"
            >
              {tool}
            </span>
          ))}
        </div>
      ) : null}
      <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
        <span className="text-xs text-slate-500">
          {new Date(pipeline.created_at).toLocaleDateString("zh-CN")}
        </span>
        <span className="text-sm font-semibold text-teal transition group-hover:text-coral">
          查看详情
        </span>
      </div>
    </Link>
  );
}
