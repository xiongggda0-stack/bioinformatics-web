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
    <section className="border-b border-slate-100 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
              {eyebrow}
            </p>
            <h1 className="mt-3 max-w-4xl text-2xl font-semibold tracking-tight text-slate-900 md:text-3xl">
              {title}
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-500">
              {description}
            </p>
          </div>

          {stats.length > 0 ? (
            <div className="flex gap-6">
              {stats.map((stat) => (
                <div key={stat.label} className="text-right">
                  <p className="text-2xl font-bold tabular-nums text-slate-900">
                    {stat.value}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-400">{stat.label}</p>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        {children ? <div className="mt-5">{children}</div> : null}
      </div>
    </section>
  );
}
