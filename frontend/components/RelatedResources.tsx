import Link from "next/link";

export interface RelatedPipeline {
  id: number;
  title: string;
  description: string;
  omics_type: string;
}

export interface RelatedAlgorithm {
  id: number;
  name: string;
  category: string;
  summary: string;
}

export interface RelatedLiterature {
  id: number;
  title: string;
  journal: string;
  publication_year: number;
  doi: string;
}

interface RelatedResourcesProps {
  pipelines?: RelatedPipeline[];
  algorithms?: RelatedAlgorithm[];
  literatures?: RelatedLiterature[];
  compact?: boolean;
  kicker?: string;
  title?: string;
  emptyText?: string;
}

function EmptyState({ text }: { text: string }): JSX.Element {
  return (
    <p className="rounded border border-dashed border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
      {text}
    </p>
  );
}

export default function RelatedResources({
  pipelines = [],
  algorithms = [],
  literatures = [],
  compact = false,
  kicker = "Cross Links",
  title = "相关资源",
  emptyText = "暂无明确关联资源"
}: RelatedResourcesProps): JSX.Element {
  const hasResources =
    pipelines.length > 0 || algorithms.length > 0 || literatures.length > 0;

  return (
    <section className="rounded border border-slate-200 bg-white p-6 shadow-sm">
      <div className="border-b border-slate-100 pb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal">
          {kicker}
        </p>
        <h2 className="mt-2 text-lg font-semibold text-ink">{title}</h2>
      </div>

      <div className={compact ? "mt-5 space-y-4" : "mt-5 grid gap-4 md:grid-cols-2"}>
        {!hasResources ? <EmptyState text={emptyText} /> : null}

        {pipelines.map((pipeline) => (
          <Link
            key={`pipeline-${pipeline.id}`}
            href={`/pipelines/${pipeline.id}`}
            className="block rounded border border-teal/25 bg-teal-50/40 p-4 transition hover:-translate-y-0.5 hover:border-teal hover:bg-white hover:shadow-sm"
          >
            <span className="text-xs font-semibold text-teal">分析流程</span>
            <h3 className="mt-2 text-sm font-semibold leading-6 text-ink">
              {pipeline.title}
            </h3>
            <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-600">
              {pipeline.description}
            </p>
            <span className="mt-3 inline-flex rounded bg-white px-2 py-1 text-[11px] font-semibold text-slate-600 ring-1 ring-slate-200">
              {pipeline.omics_type}
            </span>
          </Link>
        ))}

        {algorithms.map((algorithm) => (
          <Link
            key={`algorithm-${algorithm.id}`}
            href={`/algorithms/${algorithm.id}`}
            className="block rounded border border-coral/25 bg-rose-50/40 p-4 transition hover:-translate-y-0.5 hover:border-coral hover:bg-white hover:shadow-sm"
          >
            <span className="text-xs font-semibold text-coral">软件与算法</span>
            <h3 className="mt-2 text-sm font-semibold leading-6 text-ink">
              {algorithm.name}
            </h3>
            <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-600">
              {algorithm.summary}
            </p>
            <span className="mt-3 inline-flex rounded bg-white px-2 py-1 text-[11px] font-semibold text-slate-600 ring-1 ring-slate-200">
              {algorithm.category}
            </span>
          </Link>
        ))}

        {literatures.map((literature) => (
          <Link
            key={`literature-${literature.id}`}
            href={`/literatures/${literature.id}`}
            className="block rounded border border-slate-200 bg-slate-50 p-4 transition hover:-translate-y-0.5 hover:border-slate-400 hover:bg-white hover:shadow-sm"
          >
            <span className="text-xs font-semibold text-slate-500">
              {literature.journal} · {literature.publication_year}
            </span>
            <h3 className="mt-2 text-sm font-semibold leading-6 text-ink">
              {literature.title}
            </h3>
            <p className="mt-2 text-xs font-medium text-slate-500">
              DOI: {literature.doi}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
