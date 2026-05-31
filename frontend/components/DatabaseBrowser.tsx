"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  databaseCategories,
  type DatabaseResource
} from "@/lib/databaseResources";

interface DatabaseBrowserProps {
  resources: DatabaseResource[];
}

const categoryStyles: Record<string, string> = {
  portal: "bg-teal/10 text-teal ring-teal/20",
  literature: "bg-rose-50 text-rose-700 ring-rose-200",
  genome: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  "raw-sequence": "bg-amber-50 text-amber-700 ring-amber-200",
  expression: "bg-cyan-50 text-cyan-700 ring-cyan-200",
  "single-cell": "bg-sky-50 text-sky-700 ring-sky-200",
  variant: "bg-violet-50 text-violet-700 ring-violet-200",
  cancer: "bg-red-50 text-red-700 ring-red-200",
  protein: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  pathway: "bg-lime-50 text-lime-700 ring-lime-200",
  "model-organism": "bg-fuchsia-50 text-fuchsia-700 ring-fuchsia-200",
  microbiome: "bg-stone-100 text-stone-700 ring-stone-300"
};

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean))).sort((a, b) =>
    a.localeCompare(b, "zh-CN")
  );
}

function matchesText(resource: DatabaseResource, keyword: string): boolean {
  const normalized = keyword.trim().toLowerCase();
  if (!normalized) {
    return true;
  }

  return [
    resource.name,
    resource.fullName,
    resource.categoryName,
    resource.description,
    ...resource.useCases,
    ...resource.dataTypes,
    ...resource.species,
    ...resource.tags,
    ...(resource.tutorials ?? []).flatMap((tutorial) => [
      tutorial.title,
      tutorial.scenario,
      tutorial.exampleQuery ?? "",
      ...tutorial.steps
    ])
  ]
    .join(" ")
    .toLowerCase()
    .includes(normalized);
}

function getCategoryStyle(categoryKey: string): string {
  return categoryStyles[categoryKey] ?? "bg-slate-100 text-slate-700 ring-slate-200";
}

export default function DatabaseBrowser({
  resources
}: DatabaseBrowserProps): JSX.Element {
  const [keyword, setKeyword] = useState<string>("");
  const [category, setCategory] = useState<string>("all");
  const [dataType, setDataType] = useState<string>("all");
  const [species, setSpecies] = useState<string>("all");

  const dataTypes = useMemo(
    () => uniqueSorted(resources.flatMap((resource) => resource.dataTypes)),
    [resources]
  );
  const speciesOptions = useMemo(
    () => uniqueSorted(resources.flatMap((resource) => resource.species)),
    [resources]
  );

  const filteredResources = useMemo(
    () =>
      resources.filter((resource) => {
        if (!matchesText(resource, keyword)) {
          return false;
        }

        if (category !== "all" && resource.categoryKey !== category) {
          return false;
        }

        if (dataType !== "all" && !resource.dataTypes.includes(dataType)) {
          return false;
        }

        if (species !== "all" && !resource.species.includes(species)) {
          return false;
        }

        return true;
      }),
    [category, dataType, keyword, resources, species]
  );

  function resetFilters(): void {
    setKeyword("");
    setCategory("all");
    setDataType("all");
    setSpecies("all");
  }

  return (
    <div className="space-y-8">
      <section className="rounded border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
          <label className="block">
            <span className="text-sm font-semibold text-ink">搜索数据库</span>
            <input
              value={keyword}
              onChange={(event) => setKeyword(event.target.value)}
              placeholder="输入关键词，例如 GEO、TCGA、single-cell、variant、protein、rice"
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

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <FilterSelect
            label="数据库分类"
            value={category}
            options={databaseCategories.map((item) => ({
              value: item.key,
              label: item.name
            }))}
            placeholder="全部分类"
            onChange={(value) => setCategory(value || "all")}
          />
          <FilterSelect
            label="数据类型"
            value={dataType}
            options={dataTypes.map((item) => ({ value: item, label: item }))}
            placeholder="全部数据类型"
            onChange={(value) => setDataType(value || "all")}
          />
          <FilterSelect
            label="物种 / 范围"
            value={species}
            options={speciesOptions.map((item) => ({ value: item, label: item }))}
            placeholder="全部物种"
            onChange={(value) => setSpecies(value || "all")}
          />
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 text-sm text-slate-600">
          <p>
            当前显示{" "}
            <span className="font-semibold text-ink">{filteredResources.length}</span> /{" "}
            <span className="font-semibold text-ink">{resources.length}</span> 个数据库
          </p>
          <span className="rounded bg-teal/10 px-2.5 py-1 text-xs font-semibold text-teal">
            高质量公共数据库导航
          </span>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filteredResources.map((resource) => (
          <DatabaseCard key={resource.id} resource={resource} />
        ))}
      </section>

      {filteredResources.length === 0 ? (
        <div className="rounded border border-dashed border-slate-300 bg-white p-10 text-center">
          <h2 className="text-lg font-semibold text-ink">没有匹配的数据库</h2>
          <p className="mt-2 text-sm text-slate-500">
            换一个关键词，或清空分类、数据类型和物种筛选条件。
          </p>
        </div>
      ) : null}
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

function DatabaseCard({ resource }: { resource: DatabaseResource }): JSX.Element {
  return (
    <article className="flex h-full flex-col rounded border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-teal hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <span
          className={`inline-flex rounded px-3 py-1 text-xs font-semibold ring-1 ${getCategoryStyle(
            resource.categoryKey
          )}`}
        >
          {resource.categoryName}
        </span>
        <span className="text-xs font-semibold text-slate-400">
          {"★".repeat(resource.rating)}
        </span>
      </div>

      <h2 className="mt-5 text-2xl font-semibold tracking-tight text-ink">
        {resource.name}
      </h2>
      <p className="mt-1 text-xs font-medium text-slate-500">{resource.fullName}</p>
      <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">
        {resource.description}
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {resource.dataTypes.slice(0, 4).map((item) => (
          <span
            key={item}
            className="rounded bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600"
          >
            {item}
          </span>
        ))}
      </div>

      <div className="mt-5 border-t border-slate-100 pt-4">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          适合场景
        </p>
        <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-600">
          {resource.useCases.slice(0, 3).map((item) => (
            <li key={item}>• {item}</li>
          ))}
        </ul>
      </div>

      {resource.tutorials?.length ? (
        <div className="mt-5 border-t border-slate-100 pt-4">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal">
              使用示例
            </p>
            <span className="rounded bg-teal/10 px-2 py-1 text-[11px] font-semibold text-teal">
              {resource.tutorials.length} tutorials
            </span>
          </div>
          <div className="mt-3 space-y-3">
            {resource.tutorials.slice(0, 2).map((tutorial) => (
              <div
                key={tutorial.title}
                className="rounded border border-slate-200 bg-slate-50 p-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="text-sm font-semibold text-ink">
                    {tutorial.title}
                  </h3>
                  <Link
                    href={`/databases/tutorials/${tutorial.id}`}
                    className="text-xs font-semibold text-teal hover:text-coral"
                  >
                    查看教程
                  </Link>
                </div>
                <p className="mt-2 text-xs leading-5 text-slate-600">
                  {tutorial.scenario}
                </p>
                {tutorial.exampleQuery ? (
                  <p className="mt-2 rounded bg-white px-2.5 py-1.5 font-mono text-[11px] leading-5 text-slate-700 ring-1 ring-slate-200">
                    {tutorial.exampleQuery}
                  </p>
                ) : null}
                <ol className="mt-2 space-y-1 text-xs leading-5 text-slate-600">
                  {tutorial.steps.slice(0, 3).map((step, index) => (
                    <li key={step}>
                      <span className="font-semibold text-teal">{index + 1}.</span>{" "}
                      {step}
                    </li>
                  ))}
                </ol>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mt-auto flex flex-wrap gap-2 pt-5">
        <a
          href={resource.url}
          target="_blank"
          rel="noreferrer"
          className="rounded bg-teal px-3 py-2 text-xs font-semibold text-white transition hover:bg-teal/90"
        >
          访问数据库
        </a>
        {resource.downloadUrl ? (
          <a
            href={resource.downloadUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-teal hover:text-teal"
          >
            下载入口
          </a>
        ) : null}
        {resource.apiUrl ? (
          <a
            href={resource.apiUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-teal hover:text-teal"
          >
            API / 文档
          </a>
        ) : null}
      </div>
    </article>
  );
}
