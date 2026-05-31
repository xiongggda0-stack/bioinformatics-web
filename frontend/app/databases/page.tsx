import DatabaseBrowser from "@/components/DatabaseBrowser";
import PageHeader from "@/components/PageHeader";
import { fetchDatabaseResources } from "@/lib/databaseApi";

interface DatabasesPageProps {
  searchParams?: {
    keyword?: string;
  };
}

export default async function DatabasesPage({
  searchParams
}: DatabasesPageProps): Promise<JSX.Element> {
  const resources = await fetchDatabaseResources();
  const tutorialCount = resources.reduce(
    (count, resource) => count + (resource.tutorials?.length ?? 0),
    0
  );
  const categoryCount = new Set(
    resources.map((resource) => resource.categoryKey)
  ).size;

  return (
    <main className="min-h-screen bg-slate-50">
      <PageHeader
        eyebrow="Database Hub"
        title="数据库导航"
        description="精选全球高质量生信数据库，按组学类型、数据对象和分析场景快速检索。这里不是普通链接合集，而是面向分析项目的数据库入口地图。"
        stats={[
          { label: "databases", value: resources.length },
          { label: "tutorials", value: tutorialCount },
          { label: "categories", value: categoryCount }
        ]}
      />

      <section className="mx-auto max-w-7xl px-6 py-10">
        <DatabaseBrowser
          resources={resources}
          initialKeyword={searchParams?.keyword ?? ""}
        />
      </section>
    </main>
  );
}
