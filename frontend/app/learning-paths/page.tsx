import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import { learningPaths } from "@/lib/learningPaths";

export default function LearningPathsPage(): JSX.Element {
  const stepCount = learningPaths.reduce(
    (count, learningPath) => count + learningPath.steps.length,
    0
  );

  return (
    <main className="min-h-screen bg-slate-50">
      <PageHeader
        eyebrow="Learning Paths"
        title="从一个真实问题开始学习生物信息学"
        description="为常见入门任务整理可执行的学习顺序。每条路线从流程文档出发，连接工具说明、数据库入口与文献证据，帮助你逐步建立完整分析视角。"
        stats={[
          { label: "paths", value: learningPaths.length },
          { label: "steps", value: stepCount }
        ]}
      />

      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="grid gap-5 lg:grid-cols-2">
          {learningPaths.map((learningPath) => (
            <article
              key={learningPath.slug}
              className="rounded border border-slate-200 bg-white p-6 shadow-sm"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-coral">
                {learningPath.steps.length} Steps
              </p>
              <h2 className="mt-3 text-xl font-semibold text-ink">
                {learningPath.title}
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                {learningPath.description}
              </p>

              <div className="mt-5 border-l-2 border-teal/30 pl-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal">
                  适合人群
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {learningPath.audience}
                </p>
              </div>

              <ol className="mt-6 divide-y divide-slate-100 border-y border-slate-100">
                {learningPath.steps.map((step, index) => (
                  <li key={step.title}>
                    <Link
                      href={step.href}
                      className="group flex gap-4 py-4 transition hover:text-teal"
                    >
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded bg-teal/10 text-xs font-bold text-teal">
                        {index + 1}
                      </span>
                      <span className="min-w-0">
                        <span className="block text-[11px] font-semibold uppercase tracking-[0.12em] text-coral">
                          {step.resourceType}
                        </span>
                        <span className="block text-sm font-semibold text-ink transition group-hover:text-teal">
                          {step.title}
                        </span>
                        <span className="mt-1 block text-xs leading-5 text-slate-600">
                          {step.description}
                        </span>
                      </span>
                    </Link>
                  </li>
                ))}
              </ol>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
