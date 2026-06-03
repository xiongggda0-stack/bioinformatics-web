"use client";

import { useEffect, useState } from "react";
import type { TocItem } from "@/components/MarkdownRenderer";

interface DocumentTocProps {
  items: TocItem[];
  title?: string;
}

export default function DocumentToc({
  items,
  title = "文档目录"
}: DocumentTocProps): JSX.Element | null {
  const [activeId, setActiveId] = useState<string>(items[0]?.id ?? "");

  useEffect(() => {
    if (items.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]?.target.id) {
          setActiveId(visible[0].target.id);
        }
      },
      { rootMargin: "-20% 0px -65% 0px", threshold: [0, 1] }
    );

    items.forEach((item) => {
      const element = document.getElementById(item.id);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [items]);

  if (items.length === 0) return null;

  return (
    <>
      {/* Desktop: sticky sidebar */}
      <aside className="sticky top-24 hidden max-h-[calc(100vh-7rem)] overflow-y-auto lg:block">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
          本页目录
        </p>
        <nav className="border-l-2 border-slate-100">
          {items.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`block border-l-2 py-1.5 pl-4 text-sm leading-5 transition-colors ${
                item.level === 3 ? "pl-7" : ""
              } ${
                activeId === item.id
                  ? "-ml-0.5 border-l-2 border-accent font-medium text-accent"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              {item.text}
            </a>
          ))}
        </nav>
      </aside>

      {/* Mobile: collapsible details */}
      <details className="mb-6 lg:hidden">
        <summary className="cursor-pointer text-sm font-medium text-slate-500 hover:text-slate-700">
          {title}
        </summary>
        <nav className="mt-3 space-y-1 border-l-2 border-slate-100">
          {items.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`block border-l-2 py-1.5 pl-4 text-sm leading-5 transition-colors ${
                item.level === 3 ? "pl-7" : ""
              } border-transparent text-slate-500 hover:text-slate-700`}
            >
              {item.text}
            </a>
          ))}
        </nav>
      </details>
    </>
  );
}
