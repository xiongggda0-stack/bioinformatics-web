import { notFound } from "next/navigation";
import DetailPageShell, {
  DetailSectionCard,
  DetailSidebarCard,
  type DetailBadge,
  type DetailMetaItem
} from "@/components/DetailPageShell";
import RelatedResources, {
  type RelatedAlgorithm,
  type RelatedPipeline
} from "@/components/RelatedResources";
import MarkdownRenderer from "@/components/MarkdownRenderer";

interface Literature {
  id: number;
  title: string;
  authors: string[];
  journal: string;
  publication_year: number;
  doi: string;
  abstract_text: string;
  pipeline_id: number | null;
  algorithm_id: number | null;
  content?: string;
}

interface LiteratureRelations {
  literature_id: number;
  pipeline: RelatedPipeline | null;
  algorithm: RelatedAlgorithm | null;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface LiteratureDetailPageProps {
  params: {
    id: string;
  };
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

function unwrapPayload<T>(payload: T | ApiResponse<T>): T {
  return "data" in (payload as ApiResponse<T>)
    ? (payload as ApiResponse<T>).data
    : (payload as T);
}

async function fetchLiterature(id: string): Promise<Literature | null> {
  const response = await fetch(`${API_BASE_URL}/api/literatures/${id}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to fetch literature detail.");
  }

  return unwrapPayload((await response.json()) as Literature | ApiResponse<Literature>);
}

async function fetchLiteratureRelations(id: string): Promise<LiteratureRelations> {
  const response = await fetch(`${API_BASE_URL}/api/literatures/${id}/relations`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return { literature_id: Number(id), pipeline: null, algorithm: null };
  }

  return unwrapPayload(
    (await response.json()) as LiteratureRelations | ApiResponse<LiteratureRelations>
  );
}

export default async function LiteratureDetailPage({
  params
}: LiteratureDetailPageProps): Promise<JSX.Element> {
  const [literature, relations] = await Promise.all([
    fetchLiterature(params.id),
    fetchLiteratureRelations(params.id)
  ]);

  if (literature === null) {
    notFound();
  }

  const badges: DetailBadge[] = [
    {
      label: literature.journal,
      className: "bg-slate-900 text-white"
    },
    {
      label: String(literature.publication_year),
      className: "bg-slate-100 text-slate-600"
    }
  ];
  const metaItems: DetailMetaItem[] = [
    { label: "期刊", value: literature.journal },
    { label: "年份", value: literature.publication_year },
    {
      label: "DOI",
      value: (
        <a
          href={`https://doi.org/${literature.doi}`}
          target="_blank"
          rel="noreferrer"
          className="text-accent transition-colors hover:text-accent-hover"
        >
          {literature.doi}
        </a>
      )
    },
    {
      label: "关联状态",
      value:
        literature.pipeline_id || literature.algorithm_id
          ? "已关联平台资源"
          : "暂未关联"
    }
  ];

  return (
    <DetailPageShell
      backHref="/literatures"
      backLabel="返回文献集"
      eyebrow="Literature Detail"
      title={literature.title}
      description="这篇文献会作为平台方法、软件或流程的证据来源，用于帮助理解方法背景和应用边界。"
      badges={badges}
      metaItems={metaItems}
      sidebar={
        <>
          <RelatedResources
            pipelines={relations.pipeline ? [relations.pipeline] : []}
            algorithms={relations.algorithm ? [relations.algorithm] : []}
            compact
            title="关联流程与软件"
            emptyText="这篇文献暂未关联具体流程或软件"
          />
          <DetailSidebarCard eyebrow="External Link" title="文献入口">
            <a
              href={`https://doi.org/${literature.doi}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex rounded-md bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
            >
              打开 DOI 页面
            </a>
          </DetailSidebarCard>
        </>
      }
    >
      <DetailSectionCard
        eyebrow="Authors"
        title="作者信息"
        description="用于判断研究团队、方法出处和后续引用线索。"
      >
        <p className="text-base leading-8 text-slate-700">
          {literature.authors.join(", ")}
        </p>
      </DetailSectionCard>

      <DetailSectionCard
        eyebrow="Abstract"
        title="摘要"
        description="先读摘要确认研究问题、方法贡献和适用数据类型，再进入关联流程复现。"
      >
        <p className="text-base leading-8 text-slate-700">
          {literature.abstract_text}
        </p>
      </DetailSectionCard>
    </DetailPageShell>
  );
}
