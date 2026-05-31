import DatabaseBrowser from "@/components/DatabaseBrowser";
import PageHeader from "@/components/PageHeader";
import {
  databaseCategories,
  databaseResources,
  getAllDatabaseTutorials
} from "@/lib/databaseResources";

export default function DatabasesPage(): JSX.Element {
  const tutorials = getAllDatabaseTutorials();

  return (
    <main className="min-h-screen bg-slate-50">
      <PageHeader
        eyebrow="Database Hub"
        title="数据库导航"
        description="精选全球高质量生信数据库，按组学类型、数据对象和分析场景快速检索。这里不是普通链接合集，而是面向分析项目的数据库入口地图。"
        stats={[
          { label: "databases", value: databaseResources.length },
          { label: "tutorials", value: tutorials.length },
          { label: "categories", value: databaseCategories.length }
        ]}
      />

      <section className="mx-auto max-w-7xl px-6 py-10">
        <DatabaseBrowser resources={databaseResources} />
      </section>
    </main>
  );
}
