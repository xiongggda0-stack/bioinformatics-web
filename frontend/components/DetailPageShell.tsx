import Link from "next/link";
import type { ReactNode } from "react";

export interface DetailBadge {
  label: string;
  className?: string;
}

export interface DetailMetaItem {
  label: string;
  value: ReactNode;
}

interface DetailPageShellProps {
  backHref: string;
  backLabel: string;
  eyebrow: string;
  title: string;
  description?: string;
  badges?: DetailBadge[];
  metaItems?: DetailMetaItem[];
  children: ReactNode;
  sidebar?: ReactNode;
}

interface DetailSectionCardProps {
  eyebrow?: string;
  title: string;
  description?: string;
  children: ReactNode;
}

interface DetailSidebarCardProps {
  eyebrow?: string;
  title: string;
  children: ReactNode;
}

export function DetailSectionCard({
  eyebrow,
  title,
  description,
  children
}: DetailSectionCardProps): JSX.Element {
  return (
    <section className="rounded border border-slate-200 bg-white p-6 shadow-sm md:p-8">
      <div className="mb-6 border-b border-slate-100 pb-4">
        {eyebrow ? (
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal">
            {eyebrow}
          </p>
        ) : null}
        <h2 className={eyebrow ? "mt-2 text-lg font-semibold text-ink" : "text-lg font-semibold text-ink"}>
          {title}
        </h2>
        {description ? (
          <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
        ) : null}
      </div>
      {children}
    </section>
  );
}

export function DetailSidebarCard({
  eyebrow,
  title,
  children
}: DetailSidebarCardProps): JSX.Element {
  return (
    <section className="rounded border border-slate-200 bg-white p-5 shadow-sm">
      {eyebrow ? (
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal">
          {eyebrow}
        </p>
      ) : null}
      <h2 className={eyebrow ? "mt-2 text-lg font-semibold text-ink" : "text-lg font-semibold text-ink"}>
        {title}
      </h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

export function DetailMetaGrid({
  items
}: {
  items: DetailMetaItem[];
}): JSX.Element | null {
  if (items.length === 0) {
    return null;
  }

  return (
    <dl className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded border border-slate-200 bg-slate-50 px-4 py-3"
        >
          <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            {item.label}
          </dt>
          <dd className="mt-2 text-sm font-semibold leading-6 text-ink">
            {item.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}

export default function DetailPageShell({
  backHref,
  backLabel,
  eyebrow,
  title,
  description,
  badges = [],
  metaItems = [],
  children,
  sidebar
}: DetailPageShellProps): JSX.Element {
  return (
    <main className="min-h-screen bg-slate-50">
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <Link href={backHref} className="text-sm font-semibold text-teal">
            {backLabel}
          </Link>

          <p className="mt-6 text-xs font-semibold uppercase tracking-[0.18em] text-coral">
            {eyebrow}
          </p>

          {badges.length > 0 ? (
            <div className="mt-4 flex flex-wrap items-center gap-3">
              {badges.map((badge) => (
                <span
                  key={badge.label}
                  className={`inline-flex rounded px-3 py-1 text-xs font-semibold ring-1 ${
                    badge.className ?? "bg-slate-100 text-slate-700 ring-slate-200"
                  }`}
                >
                  {badge.label}
                </span>
              ))}
            </div>
          ) : null}

          <h1 className="mt-5 max-w-5xl text-4xl font-bold leading-tight text-ink">
            {title}
          </h1>

          {description ? (
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              {description}
            </p>
          ) : null}

          <DetailMetaGrid items={metaItems} />
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-8 px-6 py-10 lg:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0 space-y-8">{children}</div>
        {sidebar ? <aside className="space-y-6">{sidebar}</aside> : null}
      </section>
    </main>
  );
}
