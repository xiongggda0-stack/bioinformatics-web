import type {
  SearchResourceType,
  SearchResponse
} from "@/lib/searchTypes";

const SERVER_API_BASE_URL =
  process.env.BACKEND_API_URL ?? "http://localhost:8000";
const CLIENT_API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL ?? "http://localhost:8000";

interface SearchParams {
  query: string;
  type?: SearchResourceType;
  limit?: number;
  clientSide?: boolean;
  signal?: AbortSignal;
}

export async function fetchSearchResults({
  query,
  type = "all",
  limit = 20,
  clientSide = false,
  signal
}: SearchParams): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    type,
    limit: String(limit)
  });
  const baseUrl = clientSide ? CLIENT_API_BASE_URL : SERVER_API_BASE_URL;
  const response = await fetch(`${baseUrl}/api/search?${params.toString()}`, {
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error("Failed to fetch search results.");
  }

  return (await response.json()) as SearchResponse;
}
