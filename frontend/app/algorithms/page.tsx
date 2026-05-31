import AlgorithmBrowser, {
  type Algorithm,
  type AlgorithmFilters
} from "@/components/AlgorithmBrowser";
import PageHeader from "@/components/PageHeader";

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface AlgorithmsPageProps {
  searchParams?: {
    keyword?: string;
    category?: string;
  };
}

const API_BASE_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";

function unwrapPayload<T>(payload: T | ApiResponse<T>): T {
  return "data" in (payload as ApiResponse<T>) ? (payload as ApiResponse<T>).data : (payload as T);
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

async function fetchAlgorithms(filters?: AlgorithmFilters): Promise<Algorithm[]> {
  const query = filters ? `?${buildBackendQuery(filters)}` : "?limit=200";

  try {
    const response = await fetch(`${API_BASE_URL}/api/algorithms${query}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      return [];
    }

    return unwrapPayload((await response.json()) as Algorithm[] | ApiResponse<Algorithm[]>);
  } catch {
    return [];
  }
}

export default async function AlgorithmsPage({
  searchParams
}: AlgorithmsPageProps): Promise<JSX.Element> {
  const initialFilters: AlgorithmFilters = {
    keyword: searchParams?.keyword ?? "",
    category: searchParams?.category ?? "all"
  };

  const [algorithms, allAlgorithms] = await Promise.all([
    fetchAlgorithms(initialFilters),
    fetchAlgorithms()
  ]);

  return (
    <main className="min-h-screen bg-slate-50">
      <PageHeader
        eyebrow="Software & Algorithm Gallery"
        title="软件与算法"
        description="沉淀常用生信软件、算法原理、工具参数与性能基准，帮助你从会跑流程进阶到理解工具选型与方法依据。"
        stats={[
          { label: "tools", value: allAlgorithms.length },
          { label: "matched", value: algorithms.length }
        ]}
      />

      <section className="mx-auto max-w-7xl px-6 py-10">
        <AlgorithmBrowser
          algorithms={algorithms}
          allAlgorithms={allAlgorithms}
          initialFilters={initialFilters}
        />
      </section>
    </main>
  );
}
