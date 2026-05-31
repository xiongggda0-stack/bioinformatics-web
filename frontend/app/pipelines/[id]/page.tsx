import Link from "next/link";
import { notFound } from "next/navigation";
import DetailPageShell, {
  DetailSectionCard,
  DetailSidebarCard,
  type DetailBadge,
  type DetailMetaItem
} from "@/components/DetailPageShell";
import DocumentToc from "@/components/DocumentToc";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import RelatedResources, {
  type RelatedAlgorithm,
  type RelatedLiterature,
  type RelatedPipeline
} from "@/components/RelatedResources";
import { extractTocItems } from "@/lib/markdownToc";

interface Pipeline {
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

interface PipelineMetadata {
  difficulty?: string;
  tools?: string[];
  inputs?: string[];
  outputs?: string[];
  estimated_time?: string;
  scenario?: string;
}

interface PipelineDagNode {
  id: string;
  label: string;
}

interface PipelineDag {
  nodes?: PipelineDagNode[];
}

interface PipelineRelations {
  pipeline_id: number;
  algorithms: RelatedAlgorithm[];
  literatures: RelatedLiterature[];
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface PipelineDetailPageProps {
  params: {
    id: string;
  };
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

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

const databaseRecommendations: Record<
  string,
  Array<{ name: string; reason: string; keyword: string }>
> = {
  "RNA-Seq": [
    { name: "GEO", reason: "查找表达矩阵与转录组队列", keyword: "GEO" },
    { name: "SRA", reason: "下载 FASTQ 原始测序数据", keyword: "SRA" }
  ],
  "scRNA-Seq": [
    { name: "CellxGene", reason: "检索公开单细胞图谱", keyword: "CellxGene" },
    { name: "HCA", reason: "人类细胞图谱项目入口", keyword: "Human Cell Atlas" }
  ],
  "CUT&Tag": [
    { name: "ENCODE", reason: "查找表观组参考数据", keyword: "ENCODE" },
    { name: "GEO", reason: "检索公开 CUT&Tag 项目", keyword: "CUT&Tag" }
  ],
  WGS: [
    { name: "dbSNP", reason: "查询变异编号与注释", keyword: "dbSNP" },
    { name: "gnomAD", reason: "评估群体频率", keyword: "gnomAD" }
  ]
};

function unwrapPayload<T>(payload: T | ApiResponse<T>): T {
  return "data" in (payload as ApiResponse<T>)
    ? (payload as ApiResponse<T>).data
    : (payload as T);
}

function getOmicsStyle(omicsType: string): string {
  return omicsStyles[omicsType] ?? "bg-slate-100 text-slate-700 ring-slate-200";
}

function getDag(pipeline: Pipeline): PipelineDag {
  return pipeline.dag_json as PipelineDag;
}

function MetadataTags({
  label,
  items
}: {
  label: string;
  items?: string[];
}): JSX.Element | null {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
        {label}
      </p>
      <div className="mt-2 flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={item}
            className="rounded bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function PipelineMetadataPanel({
  metadata
}: {
  metadata: PipelineMetadata;
}): JSX.Element {
  return (
    <DetailSectionCard
      eyebrow="Metadata"
      title="流程元数据"
      description="先看应用场景、输入输出和工具依赖，再进入正文命令细节。"
    >
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            Difficulty
          </p>
          <p className="mt-2 text-sm font-semibold text-ink">
            {metadata.difficulty ?? "未标注"}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            Scenario
          </p>
          <p className="mt-2 text-sm font-semibold text-ink">
            {metadata.scenario ?? "通用分析"}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            Estimated Time
          </p>
          <p className="mt-2 text-sm font-semibold text-ink">
            {metadata.estimated_time ?? "视数据规模而定"}
          </p>
        </div>
        <MetadataTags label="Tools" items={metadata.tools} />
      </div>
      <div className="mt-5 grid gap-5 border-t border-slate-100 pt-5 md:grid-cols-2">
        <MetadataTags label="Inputs" items={metadata.inputs} />
        <MetadataTags label="Outputs" items={metadata.outputs} />
      </div>
    </DetailSectionCard>
  );
}

function PipelineFlow({ dag }: { dag: PipelineDag }): JSX.Element | null {
  const nodes = dag.nodes ?? [];

  if (nodes.length === 0) {
    return null;
  }

  return (
    <DetailSectionCard
      eyebrow="Workflow DAG"
      title="流程图"
      description="用步骤节点快速理解这个分析从原始数据到结果报告的流转关系。"
    >
      <div className="flex flex-wrap items-center gap-3">
        {nodes.map((node, index) => (
          <div key={node.id} className="flex items-center gap-3">
            <div className="min-w-40 rounded border border-sky-100 bg-sky-50 px-4 py-3 shadow-sm">
              <span className="text-xs font-semibold text-sky-600">
                STEP {index + 1}
              </span>
              <p className="mt-1 text-sm font-semibold leading-5 text-slate-800">
                {node.label}
              </p>
            </div>
            {index < nodes.length - 1 ? (
              <span className="text-lg font-semibold text-slate-300">→</span>
            ) : null}
          </div>
        ))}
      </div>
    </DetailSectionCard>
  );
}

function RecommendedDatabases({
  omicsType
}: {
  omicsType: string;
}): JSX.Element {
  const items =
    databaseRecommendations[omicsType] ??
    [
      { name: "NCBI", reason: "通用序列、基因和文献入口", keyword: "NCBI" },
      { name: "GEO", reason: "检索公开表达与组学项目", keyword: "GEO" }
    ];

  return (
    <DetailSidebarCard eyebrow="Database Links" title="推荐数据库入口">
      <div className="space-y-3">
        {items.map((item) => (
          <Link
            key={item.name}
            href={`/databases?keyword=${encodeURIComponent(item.keyword)}`}
            className="block rounded border border-slate-200 bg-slate-50 p-4 transition hover:border-teal hover:bg-white hover:shadow-sm"
          >
            <p className="text-sm font-semibold text-ink">{item.name}</p>
            <p className="mt-2 text-xs leading-5 text-slate-600">{item.reason}</p>
          </Link>
        ))}
      </div>
    </DetailSidebarCard>
  );
}

async function fetchPipeline(id: string): Promise<Pipeline | null> {
  const response = await fetch(`${API_BASE_URL}/api/pipelines/${id}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to fetch pipeline detail.");
  }

  return unwrapPayload((await response.json()) as Pipeline | ApiResponse<Pipeline>);
}

async function fetchPipelineRelations(id: string): Promise<PipelineRelations> {
  const response = await fetch(`${API_BASE_URL}/api/pipelines/${id}/relations`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return { pipeline_id: Number(id), algorithms: [], literatures: [] };
  }

  return unwrapPayload(
    (await response.json()) as PipelineRelations | ApiResponse<PipelineRelations>
  );
}

async function fetchSimilarPipelines(pipeline: Pipeline): Promise<RelatedPipeline[]> {
  if (!pipeline.category_key) {
    return [];
  }

  const params = new URLSearchParams({
    category_key: pipeline.category_key,
    limit: "6"
  });

  const response = await fetch(`${API_BASE_URL}/api/pipelines?${params.toString()}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return [];
  }

  const payload = (await response.json()) as Pipeline[] | ApiResponse<Pipeline[]>;
  const pipelines = unwrapPayload(payload);

  return pipelines
    .filter((item) => item.id !== pipeline.id)
    .slice(0, 4)
    .map((item) => ({
      id: item.id,
      title: item.title,
      description: item.description,
      omics_type: item.omics_type
    }));
}

export default async function PipelineDetailPage({
  params
}: PipelineDetailPageProps): Promise<JSX.Element> {
  const [pipeline, relations] = await Promise.all([
    fetchPipeline(params.id),
    fetchPipelineRelations(params.id)
  ]);

  if (pipeline === null) {
    notFound();
  }

  const similarPipelines = await fetchSimilarPipelines(pipeline);
  const tocItems = extractTocItems(pipeline.content);
  const badges: DetailBadge[] = [
    {
      label: pipeline.omics_type,
      className: getOmicsStyle(pipeline.omics_type)
    },
    {
      label: pipeline.category_name,
      className: "bg-slate-100 text-slate-700 ring-slate-200"
    }
  ];
  const metaItems: DetailMetaItem[] = [
    {
      label: "创建时间",
      value: new Date(pipeline.created_at).toLocaleDateString("zh-CN")
    },
    {
      label: "分析难度",
      value: pipeline.metadata_json?.difficulty ?? "未标注"
    },
    {
      label: "推荐场景",
      value: pipeline.metadata_json?.scenario ?? "通用分析"
    },
    {
      label: "预计耗时",
      value: pipeline.metadata_json?.estimated_time ?? "视数据规模而定"
    }
  ];

  return (
    <DetailPageShell
      backHref="/pipelines"
      backLabel="返回分析流程中心"
      eyebrow="Pipeline Detail"
      title={pipeline.title}
      description={pipeline.description}
      badges={badges}
      metaItems={metaItems}
      sidebar={
        <>
          <RelatedResources
            pipelines={similarPipelines}
            compact
            kicker="Same Category"
            title="同类流程推荐"
            emptyText="暂无同类流程推荐"
          />
          <RelatedResources
            algorithms={relations.algorithms}
            literatures={relations.literatures}
            compact
            title="相关软件与文献"
          />
          <RecommendedDatabases omicsType={pipeline.omics_type} />
          <DocumentToc items={tocItems} />
        </>
      }
    >
      <PipelineMetadataPanel metadata={pipeline.metadata_json ?? {}} />
      <PipelineFlow dag={getDag(pipeline)} />
      <DetailSectionCard
        eyebrow="Protocol"
        title="流程文档"
        description="正文保留 Markdown 排版、代码语言标识和表格样式，适合边学边复现。"
      >
        <MarkdownRenderer content={pipeline.content} tocItems={tocItems} />
      </DetailSectionCard>
    </DetailPageShell>
  );
}
