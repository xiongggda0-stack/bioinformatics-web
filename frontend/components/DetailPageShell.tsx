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
    <section className="rounded-md border border-slate-200/60 bg-white p-6 md:p-8">
      <div className="mb-6 border-b border-slate-100 pb-4">
        {eyebrow ? (
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
            {eyebrow}
          </p>
        ) : null}
        <h2 className={eyebrow ? "mt-2 text-lg font-semibold text-slate-900" : "text-lg font-semibold text-slate-900"}>
          {title}
        </h2>
        {description ? (
          <p className="mt-2 text-sm leading-relaxed text-slate-500">{description}</p>
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
    <section className="rounded-md border border-slate-200/60 bg-white p-5">
      {eyebrow ? (
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
          {eyebrow}
        </p>
      ) : null}
      <h2 className={eyebrow ? "mt-2 text-sm font-semibold text-slate-900" : "text-sm font-semibold text-slate-900"}>
        {title}
      </h2>
      <div className="mt-3">{children}</div>
    </section>
  );
}

export function DetailMetaGrid({
  items
}: {
  items: DetailMetaItem[];
}): JSX.Element | null {
  if (items.length === 0) return null;

  return (
    <dl className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded-md border border-slate-100 bg-slate-50 px-4 py-3"
        >
          <dt className="text-xs text-slate-400">{item.label}</dt>
          <dd className="mt-2 text-sm font-medium text-slate-900">{item.value}</dd>
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
    <main className="min-h-screen bg-white">
      {/* Header */}
      <section className="border-b border-slate-100 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <Link href={backHref} className="text-sm font-medium text-accent transition-colors hover:text-accent-hover">
            &larr; {backLabel}
          </Link>

          <p className="mt-6 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
            {eyebrow}
          </p>

          {badges.length > 0 ? (
            <div className="mt-4 flex flex-wrap items-center gap-2">
              {badges.map((badge) => (
                <span
                  key={badge.label}
                  className={`inline-flex rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-500 ${badge.className ?? ""}`}
                >
                  {badge.label}
                </span>
              ))}
            </div>
          ) : null}

          <h1 className="mt-4 max-w-5xl text-2xl font-semibold tracking-tight text-slate-900 md:text-3xl">
            {title}
          </h1>

          {description ? (
            <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-500">
              {description}
            </p>
          ) : null}

          {metaItems.length > 0 ? (
            <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {metaItems.map((item) => (
                <div key={item.label} className="rounded-md border border-slate-100 bg-slate-50 px-4 py-3">
                  <dt className="text-xs text-slate-400">{item.label}</dt>
                  <dd className="mt-2 text-sm font-medium text-slate-900">{item.value}</dd>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      </section>

      {/* Body */}
      <section className="mx-auto grid max-w-7xl gap-8 px-6 py-10 lg:grid-cols-[minmax(0,1fr)_260px]">
        <div className="min-w-0 space-y-8">{children}</div>
        {sidebar ? <aside className="space-y-6">{sidebar}</aside> : null}
      </section>
    </main>
  );
}
