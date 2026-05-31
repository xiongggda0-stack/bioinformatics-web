import type { ReactNode } from "react";

interface PageHeaderStat {
  label: string;
  value: string | number;
}

interface PageHeaderProps {
  eyebrow: string;
  title: string;
  description: string;
  stats?: PageHeaderStat[];
  children?: ReactNode;
}

export default function PageHeader({
  eyebrow,
  title,
  description,
  stats = [],
  children
}: PageHeaderProps): JSX.Element {
  return (
    <section className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal">
              {eyebrow}
            </p>
            <h1 className="mt-4 max-w-4xl text-4xl font-bold tracking-tight text-ink">
              {title}
            </h1>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              {description}
            </p>
          </div>

          {stats.length > 0 ? (
            <div className="grid min-w-[220px] grid-cols-2 gap-3">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded border border-slate-200 bg-slate-50 px-4 py-3"
                >
                  <p className="text-2xl font-bold text-ink">{stat.value}</p>
                  <p className="mt-1 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
                    {stat.label}
                  </p>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        {children ? <div className="mt-6">{children}</div> : null}
      </div>
    </section>
  );
}
