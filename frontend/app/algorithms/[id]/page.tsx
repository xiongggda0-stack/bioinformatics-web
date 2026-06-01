import { notFound } from "next/navigation";
import BenchmarkChart from "@/components/BenchmarkChart";
import DetailPageShell, {
  DetailSectionCard,
  type DetailBadge,
  type DetailMetaItem
} from "@/components/DetailPageShell";
import DocumentToc from "@/components/DocumentToc";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import RelatedResources, {
  type RelatedLiterature,
  type RelatedPipeline
} from "@/components/RelatedResources";
import TrustPanel from "@/components/TrustPanel";
import { formatDisplayDate } from "@/lib/dateFormat.mjs";
import { extractTocItems } from "@/lib/markdownToc";
import type { TrustMetadata } from "@/lib/trustMetadata";

interface Algorithm {
  id: number;
  name: string;
  category: string;
  category_key: string;
  category_name: string;
  tool_type: string;
  summary: string;
  performance_json: Record<string, unknown>;
  metadata_json: TrustMetadata;
  markdown_docs: string;
  created_at: string;
}

interface AlgorithmRelations {
  algorithm_id: number;
  pipelines: RelatedPipeline[];
  literatures: RelatedLiterature[];
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface AlgorithmDetailPageProps {
  params: {
    id: string;
  };
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

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

function unwrapPayload<T>(payload: T | ApiResponse<T>): T {
  return "data" in (payload as ApiResponse<T>)
    ? (payload as ApiResponse<T>).data
    : (payload as T);
}

function getCategoryStyle(categoryKey: string): string {
  return categoryStyles[categoryKey] ?? categoryStyles.other;
}

function getToolTypeLabel(toolType: string): string {
  const labels: Record<string, string> = {
    software: "软件",
    algorithm: "算法",
    workflow: "流程工具",
    database: "数据库工具"
  };

  return labels[toolType] ?? toolType;
}

async function fetchAlgorithm(id: string): Promise<Algorithm | null> {
  const response = await fetch(`${API_BASE_URL}/api/algorithms/${id}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to fetch algorithm detail.");
  }

  return unwrapPayload((await response.json()) as Algorithm | ApiResponse<Algorithm>);
}

async function fetchAlgorithmRelations(id: string): Promise<AlgorithmRelations> {
  const response = await fetch(`${API_BASE_URL}/api/algorithms/${id}/relations`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return { algorithm_id: Number(id), pipelines: [], literatures: [] };
  }

  return unwrapPayload(
    (await response.json()) as AlgorithmRelations | ApiResponse<AlgorithmRelations>
  );
}

export default async function AlgorithmDetailPage({
  params
}: AlgorithmDetailPageProps): Promise<JSX.Element> {
  const [algorithm, relations] = await Promise.all([
    fetchAlgorithm(params.id),
    fetchAlgorithmRelations(params.id)
  ]);

  if (algorithm === null) {
    notFound();
  }

  const tocItems = extractTocItems(algorithm.markdown_docs);
  const badges: DetailBadge[] = [
    {
      label: algorithm.category_name,
      className: getCategoryStyle(algorithm.category_key)
    },
    {
      label: algorithm.category,
      className: "bg-slate-100 text-slate-700 ring-slate-200"
    },
    {
      label: getToolTypeLabel(algorithm.tool_type),
      className: "bg-white text-slate-600 ring-slate-200"
    }
  ];
  const metaItems: DetailMetaItem[] = [
    {
      label: "资源类型",
      value: getToolTypeLabel(algorithm.tool_type)
    },
    {
      label: "方法分类",
      value: algorithm.category_name
    },
    {
      label: "原始分类",
      value: algorithm.category
    },
    {
      label: "创建时间",
      value: formatDisplayDate(algorithm.created_at)
    }
  ];

  return (
    <DetailPageShell
      backHref="/algorithms"
      backLabel="返回软件与算法"
      eyebrow="Software & Algorithm Detail"
      title={algorithm.name}
      description={algorithm.summary}
      badges={badges}
      metaItems={metaItems}
      sidebar={
        <>
          <RelatedResources
            pipelines={relations.pipelines}
            literatures={relations.literatures}
            compact
            title="关联流程与文献"
          />
          <DocumentToc items={tocItems} title="软件文档目录" />
        </>
      }
    >
      <TrustPanel
        metadata={algorithm.metadata_json ?? {}}
        officialLinkLabel="查看官方文档"
      />

      <DetailSectionCard
        eyebrow="Benchmark"
        title="性能基准测试"
        description="当前图表用于比较不同数据规模下的时间消耗和内存消耗。"
      >
        <BenchmarkChart performanceJson={algorithm.performance_json} />
      </DetailSectionCard>

      <DetailSectionCard
        eyebrow="Documentation"
        title="软件原理、用法与参数"
        description="统一使用 Markdown 文档渲染，保留命令行代码块、参数表和示例说明。"
      >
        <MarkdownRenderer content={algorithm.markdown_docs} tocItems={tocItems} />
      </DetailSectionCard>
    </DetailPageShell>
  );
}
