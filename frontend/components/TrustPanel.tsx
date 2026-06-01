import { DetailSectionCard } from "@/components/DetailPageShell";
import type { TrustMetadata } from "@/lib/trustMetadata";
import {
  getTrustList,
  getTrustValue,
  hasTrustValue
} from "@/lib/trustMetadata";

interface TrustPanelProps {
  metadata: TrustMetadata;
  officialLinkLabel?: string;
}

function TrustTags({ items }: { items?: string[] }): JSX.Element {
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {getTrustList(items).map((item) => (
        <span
          key={item}
          className="rounded bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200"
        >
          {item}
        </span>
      ))}
    </div>
  );
}

export default function TrustPanel({
  metadata,
  officialLinkLabel = "查看官方文档"
}: TrustPanelProps): JSX.Element {
  const hasVersion = hasTrustValue(metadata.version);
  const installation = hasTrustValue(metadata.installation)
    ? metadata.installation
    : null;
  const officialDocsUrl = hasTrustValue(metadata.official_docs_url)
    ? metadata.official_docs_url
    : null;

  return (
    <DetailSectionCard
      eyebrow="Public Trust"
      title="公开使用说明"
      description="快速查看资料校验、适用范围与使用边界。"
    >
      <dl
        className={`grid gap-5 sm:grid-cols-2 ${
          hasVersion ? "xl:grid-cols-4" : "xl:grid-cols-3"
        }`}
      >
        <div>
          <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            校验状态
          </dt>
          <dd className="mt-2 text-sm font-semibold text-ink">
            {getTrustValue(metadata.validation_status)}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            最近复核
          </dt>
          <dd className="mt-2 text-sm font-semibold text-ink">
            {getTrustValue(metadata.last_reviewed_at)}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            难度
          </dt>
          <dd className="mt-2 text-sm font-semibold text-ink">
            {getTrustValue(metadata.difficulty)}
          </dd>
        </div>
        {hasVersion ? (
          <div>
            <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
              版本
            </dt>
            <dd className="mt-2 text-sm font-semibold text-ink">
              {metadata.version}
            </dd>
          </div>
        ) : null}
      </dl>

      <div className="mt-5 grid gap-5 border-t border-slate-100 pt-5 sm:grid-cols-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            适用物种
          </p>
          <TrustTags items={metadata.applicability?.species} />
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            数据类型
          </p>
          <TrustTags items={metadata.applicability?.data_types} />
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            实验类型
          </p>
          <TrustTags items={metadata.applicability?.experiment_types} />
        </div>
      </div>

      {installation ? (
        <div className="mt-5 border-t border-slate-100 pt-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            安装建议
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {installation}
          </p>
        </div>
      ) : null}

      <div className="mt-5 border-t border-slate-100 pt-5">
        {officialDocsUrl ? (
          <a
            href={officialDocsUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex text-sm font-semibold text-teal transition hover:text-emerald-700"
          >
            {officialLinkLabel}
          </a>
        ) : null}
        <p
          className={`text-xs leading-5 text-slate-600 ${
            officialDocsUrl ? "mt-4" : ""
          }`}
        >
          {getTrustValue(metadata.disclaimer)}
        </p>
      </div>
    </DetailSectionCard>
  );
}
