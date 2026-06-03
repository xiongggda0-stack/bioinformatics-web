import Link from "next/link";

const TAGS = [
  { label: "RNA-seq 差异表达", href: "/search?q=RNA-seq+差异表达" },
  { label: "单细胞聚类", href: "/search?q=单细胞+聚类" },
  { label: "WGCNA 共表达网络", href: "/search?q=WGCNA" },
  { label: "BSA 性状定位", href: "/search?q=BSA+性状定位" },
  { label: "CUT&Tag 富集分析", href: "/search?q=CUT%26Tag+富集分析" },
  { label: "ChIP-seq 峰注释", href: "/search?q=ChIP-seq" }
];

export default function QuickTags(): JSX.Element {
  return (
    <section className="bg-white py-12">
      <div className="mx-auto max-w-7xl px-6">
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
          快速入口
        </p>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {TAGS.map((tag) => (
            <Link
              key={tag.href}
              href={tag.href}
              className="shrink-0 rounded-full border border-slate-200 px-4 py-2 text-sm text-slate-600 transition-colors hover:border-slate-400 hover:text-slate-900"
            >
              {tag.label}
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
