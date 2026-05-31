export type SearchResourceType =
  | "all"
  | "pipeline"
  | "algorithm"
  | "database"
  | "tutorial"
  | "literature";

export type SearchItemType = Exclude<SearchResourceType, "all">;

export interface SearchResultItem {
  id: string;
  type: SearchItemType;
  title: string;
  description: string;
  href: string;
  tags: string[];
  score: number;
}

export interface SearchResultCounts {
  pipeline: number;
  algorithm: number;
  database: number;
  tutorial: number;
  literature: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  counts: SearchResultCounts;
  items: SearchResultItem[];
}
