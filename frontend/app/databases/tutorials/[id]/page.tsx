import Link from "next/link";
import { notFound } from "next/navigation";
import DetailPageShell, {
  DetailSectionCard,
  DetailSidebarCard,
  type DetailBadge,
  type DetailMetaItem
} from "@/components/DetailPageShell";
import DocumentToc from "@/components/DocumentToc";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import {
  getAllDatabaseTutorials,
  getDatabaseTutorialById
} from "@/lib/databaseResources";
import { extractTocItems } from "@/lib/markdownToc";

interface DatabaseTutorialPageProps {
  params: {
    id: string;
  };
}

const pipelineRecommendations: Record<
  string,
  Array<{ title: string; href: string; reason: string }>
> = {
  "raw-sequence": [
    {
      title: "Bulk RNA-seq 标准差异表达分析",
      href: "/pipelines?keyword=RNA-seq",
      reason: "公共 FASTQ 下载后可直接进入质控、比对和差异分析。"
    },
    {
      title: "De novo 转录组组装 Trinity",
      href: "/pipelines?keyword=Trinity",
      reason: "非模式物种项目常从 SRA/ENA 原始数据开始。"
    }
  ],
  expression: [
    {
      title: "WGCNA 共表达网络分析",
      href: "/pipelines?keyword=WGCNA",
      reason: "表达矩阵可直接作为网络构建和模块挖掘的输入。"
    },
    {
      title: "时间序列 RNA-seq 分析",
      href: "/pipelines?keyword=时间序列",
      reason: "适合下载公开表达矩阵后复现动态表达模式。"
    }
  ],
  "single-cell": [
    {
      title: "单细胞高级下游分析",
      href: "/pipelines?keyword=单细胞",
      reason: "公开单细胞图谱可用于拟时序、通讯和注释练习。"
    }
  ],
  cancer: [
    {
      title: "融合基因检测 STAR-Fusion/Arriba",
      href: "/pipelines?keyword=fusion",
      reason: "肿瘤队列数据适合练习融合基因候选筛选。"
    }
  ]
};

export function generateStaticParams(): Array<{ id: string }> {
  return getAllDatabaseTutorials().map(({ tutorial }) => ({
    id: tutorial.id
  }));
}

function TutorialSteps({ steps }: { steps: string[] }): JSX.Element {
  return (
    <DetailSectionCard
      eyebrow="Quick Steps"
      title="教程步骤速览"
      description="先快速看完整操作路径，再进入下方详细教程。"
    >
      <ol className="grid gap-3 md:grid-cols-2">
        {steps.map((step, index) => (
          <li
            key={step}
            className="rounded border border-slate-200 bg-slate-50 p-4"
          >
            <span className="text-xs font-semibold text-teal">
              STEP {index + 1}
            </span>
            <p className="mt-2 text-sm font-semibold leading-6 text-ink">
              {step}
            </p>
          </li>
        ))}
      </ol>
    </DetailSectionCard>
  );
}

function PipelineSuggestionCard({
  categoryKey
}: {
  categoryKey: string;
}): JSX.Element {
  const suggestions =
    pipelineRecommendations[categoryKey] ??
    [
      {
        title: "分析流程中心",
        href: "/pipelines",
        reason: "从数据库获取数据后，可回到流程中心选择适合的分析模板。"
      }
    ];

  return (
    <DetailSidebarCard eyebrow="Apply To" title="适用流程推荐">
      <div className="space-y-3">
        {suggestions.map((item) => (
          <Link
            key={item.title}
            href={item.href}
            className="block rounded border border-slate-200 bg-slate-50 p-4 transition hover:border-teal hover:bg-white hover:shadow-sm"
          >
            <p className="text-sm font-semibold text-ink">{item.title}</p>
            <p className="mt-2 text-xs leading-5 text-slate-600">{item.reason}</p>
          </Link>
        ))}
      </div>
    </DetailSidebarCard>
  );
}

export default function DatabaseTutorialPage({
  params
}: DatabaseTutorialPageProps): JSX.Element {
  const detail = getDatabaseTutorialById(params.id);

  if (detail === null) {
    notFound();
  }

  const { resource, tutorial } = detail;
  const tocItems = extractTocItems(tutorial.content);
  const badges: DetailBadge[] = [
    {
      label: resource.name,
      className: "bg-teal/10 text-teal ring-teal/20"
    },
    {
      label: resource.categoryName,
      className: "bg-slate-100 text-slate-700 ring-slate-200"
    },
    {
      label: "Database Tutorial",
      className: "bg-white text-slate-600 ring-slate-200"
    }
  ];
  const metaItems: DetailMetaItem[] = [
    {
      label: "数据库",
      value: resource.name
    },
    {
      label: "资源类型",
      value: resource.categoryName
    },
    {
      label: "地区",
      value: resource.region
    },
    {
      label: "推荐等级",
      value: `${resource.rating}/5`
    }
  ];

  return (
    <DetailPageShell
      backHref="/databases"
      backLabel="返回数据库导航"
      eyebrow="Database Tutorial"
      title={tutorial.title}
      description={tutorial.scenario}
      badges={badges}
      metaItems={metaItems}
      sidebar={
        <>
          <DetailSidebarCard eyebrow="Database" title={resource.name}>
            <p className="text-sm leading-6 text-slate-600">
              {resource.description}
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              <a
                href={resource.url}
                target="_blank"
                rel="noreferrer"
                className="rounded bg-teal px-3 py-2 text-xs font-semibold text-white transition hover:bg-teal/90"
              >
                访问数据库
              </a>
              <a
                href={tutorial.entryUrl}
                target="_blank"
                rel="noreferrer"
                className="rounded border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-teal hover:text-teal"
              >
                官方入口
              </a>
            </div>
          </DetailSidebarCard>
          <PipelineSuggestionCard categoryKey={resource.categoryKey} />
          <DocumentToc items={tocItems} title="教程目录" />
        </>
      }
    >
      <TutorialSteps steps={tutorial.steps} />

      {tutorial.exampleQuery ? (
        <DetailSectionCard
          eyebrow="Example Query"
          title="示例查询"
          description="复制这个关键词或编号，可以快速进入数据库检索练习。"
        >
          <div className="rounded border border-slate-200 bg-slate-50 p-4 font-mono text-sm leading-6 text-slate-800">
            {tutorial.exampleQuery}
          </div>
        </DetailSectionCard>
      ) : null}

      <DetailSectionCard
        eyebrow="Tutorial"
        title="数据库使用教程"
        description="按教程完成检索、筛选、下载和结果确认。"
      >
        <MarkdownRenderer content={tutorial.content} tocItems={tocItems} />
      </DetailSectionCard>
    </DetailPageShell>
  );
}
