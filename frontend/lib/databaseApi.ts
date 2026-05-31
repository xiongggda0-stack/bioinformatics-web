import type {
  DatabaseResource,
  DatabaseResourceDto,
  DatabaseTutorial,
  DatabaseTutorialDetail,
  DatabaseTutorialDetailDto,
  DatabaseTutorialDto
} from "@/lib/databaseTypes";

const SERVER_API_BASE_URL =
  process.env.BACKEND_API_URL ?? "http://localhost:8000";

function mapDatabaseTutorial(dto: DatabaseTutorialDto): DatabaseTutorial {
  return {
    id: dto.slug,
    title: dto.title,
    scenario: dto.scenario,
    steps: dto.steps_json,
    exampleQuery: dto.example_query ?? undefined,
    entryUrl: dto.entry_url,
    content: dto.content
  };
}

export function mapDatabaseResource(dto: DatabaseResourceDto): DatabaseResource {
  return {
    id: dto.slug,
    name: dto.name,
    fullName: dto.full_name,
    categoryKey: dto.category_key,
    categoryName: dto.category_name,
    description: dto.description,
    useCases: dto.use_cases_json,
    dataTypes: dto.data_types_json,
    species: dto.species_json,
    tags: dto.tags_json,
    url: dto.url,
    downloadUrl: dto.download_url ?? undefined,
    apiUrl: dto.api_url ?? undefined,
    tutorials: dto.tutorials.map(mapDatabaseTutorial),
    region: dto.region,
    rating: dto.rating
  };
}

export async function fetchDatabaseResources(): Promise<DatabaseResource[]> {
  const response = await fetch(`${SERVER_API_BASE_URL}/api/databases`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("Failed to fetch database resources.");
  }

  const data = (await response.json()) as DatabaseResourceDto[];
  return data.map(mapDatabaseResource);
}

export async function fetchDatabaseTutorial(
  slug: string
): Promise<DatabaseTutorialDetail | null> {
  const response = await fetch(
    `${SERVER_API_BASE_URL}/api/databases/tutorials/${slug}`,
    {
      cache: "no-store"
    }
  );

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to fetch database tutorial.");
  }

  const dto = (await response.json()) as DatabaseTutorialDetailDto;
  return {
    resource: mapDatabaseResource({
      ...dto.resource,
      tutorials: []
    }),
    tutorial: mapDatabaseTutorial(dto)
  };
}
