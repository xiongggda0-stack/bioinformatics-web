import PageHeader from "@/components/PageHeader";
import PipelineBrowser, {
  type Pipeline,
  type PipelineFilters
} from "@/components/PipelineBrowser";

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface PipelinesPageProps {
  searchParams?: Record<string, string | string[] | undefined>;
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

const backendFilterKeys = [
  "keyword",
  "omics_type",
  "difficulty",
  "tool",
  "input_type",
  "output_type",
  "scenario"
] as const;

function getSearchParam(
  searchParams: PipelinesPageProps["searchParams"],
  key: string
): string {
  const value = searchParams?.[key];
  if (Array.isArray(value)) {
    return value[0] ?? "";
  }
  return value ?? "";
}

function getInitialFilters(
  searchParams: PipelinesPageProps["searchParams"]
): PipelineFilters {
  return {
    keyword: getSearchParam(searchParams, "keyword"),
    category: getSearchParam(searchParams, "category") || "all",
    omics_type: getSearchParam(searchParams, "omics_type"),
    difficulty: getSearchParam(searchParams, "difficulty"),
    tool: getSearchParam(searchParams, "tool"),
    input_type: getSearchParam(searchParams, "input_type"),
    output_type: getSearchParam(searchParams, "output_type"),
    scenario: getSearchParam(searchParams, "scenario")
  };
}

function buildPipelineQuery(filters: PipelineFilters): string {
  const params = new URLSearchParams();

  for (const key of backendFilterKeys) {
    const value = filters[key]?.trim();
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

async function fetchPipelines(filters?: PipelineFilters): Promise<Pipeline[]> {
  try {
    const query = filters ? buildPipelineQuery(filters) : "limit=200";
    const response = await fetch(`${API_BASE_URL}/api/pipelines?${query}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as Pipeline[] | ApiResponse<Pipeline[]>;
    return Array.isArray(payload) ? payload : payload.data ?? [];
  } catch {
    return [];
  }
}

export default async function PipelinesPage({
  searchParams
}: PipelinesPageProps): Promise<JSX.Element> {
  const filters = getInitialFilters(searchParams);
  const [pipelines, allPipelines] = await Promise.all([
    fetchPipelines(filters),
    fetchPipelines()
  ]);

  return (
    <main className="min-h-screen bg-slate-50">
      <PageHeader
        eyebrow="Pipeline Hub"
        title="分析流程中心"
        description="汇总常用生信分析模板，从流程说明、DAG 结构、工具依赖到下游报告形成统一入口。"
        stats={[
          { label: "workflows", value: allPipelines.length },
          { label: "matched", value: pipelines.length }
        ]}
      />

      <section className="mx-auto max-w-7xl px-6 py-10">
        <PipelineBrowser
          pipelines={pipelines}
          allPipelines={allPipelines}
          initialFilters={filters}
        />
      </section>
    </main>
  );
}
