export interface DatabaseTutorialDto {
  id: number;
  slug: string;
  database_resource_id: number;
  title: string;
  scenario: string;
  steps_json: string[];
  example_query: string | null;
  entry_url: string;
  content: string;
  created_at: string;
}

export interface DatabaseResourceDto {
  id: number;
  slug: string;
  name: string;
  full_name: string;
  category_key: string;
  category_name: string;
  description: string;
  use_cases_json: string[];
  data_types_json: string[];
  species_json: string[];
  tags_json: string[];
  url: string;
  download_url: string | null;
  api_url: string | null;
  region: string;
  rating: 1 | 2 | 3 | 4 | 5;
  created_at: string;
  tutorials: DatabaseTutorialDto[];
}

export interface DatabaseTutorialDetailDto extends DatabaseTutorialDto {
  resource: Omit<DatabaseResourceDto, "tutorials">;
}

export interface DatabaseTutorial {
  id: string;
  title: string;
  scenario: string;
  steps: string[];
  exampleQuery?: string;
  entryUrl: string;
  content: string;
}

export interface DatabaseResource {
  id: string;
  name: string;
  fullName: string;
  categoryKey: string;
  categoryName: string;
  description: string;
  useCases: string[];
  dataTypes: string[];
  species: string[];
  tags: string[];
  url: string;
  downloadUrl?: string;
  apiUrl?: string;
  tutorials?: DatabaseTutorial[];
  region: string;
  rating: 1 | 2 | 3 | 4 | 5;
}

export interface DatabaseTutorialDetail {
  resource: DatabaseResource;
  tutorial: DatabaseTutorial;
}
