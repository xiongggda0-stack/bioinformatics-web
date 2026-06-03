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
    <p className="rounded-md border border-dashed border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-400">
      {text}
    </p>
  );
}

export default function RelatedResources({
  pipelines = [],
  algorithms = [],
  literatures = [],
  compact = false,
  title = "相关资源",
  emptyText = "暂无明确关联资源"
}: RelatedResourcesProps): JSX.Element {
  const hasResources =
    pipelines.length > 0 || algorithms.length > 0 || literatures.length > 0;

  return (
    <section>
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-[0.12em] text-slate-400">
        {title}
      </h2>

      <div className={compact ? "space-y-3" : "grid gap-3 md:grid-cols-2"}>
        {!hasResources ? <EmptyState text={emptyText} /> : null}

        {pipelines.map((pipeline) => (
          <Link
            key={`pipeline-${pipeline.id}`}
            href={`/pipelines/${pipeline.id}`}
            className="block rounded-md border border-slate-200/60 bg-white p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300"
          >
            <span className="text-xs font-medium text-accent">分析流程</span>
            <h3 className="mt-1 text-sm font-semibold text-slate-900">
              {pipeline.title}
            </h3>
            <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
              {pipeline.description}
            </p>
          </Link>
        ))}

        {algorithms.map((algorithm) => (
          <Link
            key={`algorithm-${algorithm.id}`}
            href={`/algorithms/${algorithm.id}`}
            className="block rounded-md border border-slate-200/60 bg-white p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300"
          >
            <span className="text-xs font-medium text-indigo-500">软件与算法</span>
            <h3 className="mt-1 text-sm font-semibold text-slate-900">
              {algorithm.name}
            </h3>
            <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
              {algorithm.summary}
            </p>
          </Link>
        ))}

        {literatures.map((literature) => (
          <Link
            key={`literature-${literature.id}`}
            href={`/literatures/${literature.id}`}
            className="block rounded-md border border-slate-200/60 bg-white p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300"
          >
            <span className="text-xs font-medium text-amber-600">
              {literature.journal} &middot; {literature.publication_year}
            </span>
            <h3 className="mt-1 text-sm font-semibold text-slate-900">
              {literature.title}
            </h3>
            <p className="mt-1 text-xs text-slate-400">DOI: {literature.doi}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
