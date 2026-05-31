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
    if (items.length === 0) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

        if (visible[0]?.target.id) {
          setActiveId(visible[0].target.id);
        }
      },
      {
        rootMargin: "-20% 0px -65% 0px",
        threshold: [0, 1]
      }
    );

    items.forEach((item) => {
      const element = document.getElementById(item.id);
      if (element) {
        observer.observe(element);
      }
    });

    return () => observer.disconnect();
  }, [items]);

  if (items.length === 0) {
    return null;
  }

  return (
    <aside className="sticky top-24 hidden max-h-[calc(100vh-7rem)] overflow-y-auto rounded border border-slate-200 bg-white p-5 shadow-sm lg:block">
      <div className="border-b border-slate-100 pb-3">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal">
          On This Page
        </p>
        <h2 className="mt-2 text-sm font-semibold text-ink">{title}</h2>
      </div>
      <nav className="mt-4 space-y-1">
        {items.map((item) => (
          <a
            key={item.id}
            href={`#${item.id}`}
            className={`block rounded px-3 py-2 text-sm leading-5 transition ${
              item.level === 3 ? "ml-4" : ""
            } ${
              activeId === item.id
                ? "bg-sky-50 font-semibold text-teal"
                : "text-slate-600 hover:bg-slate-50 hover:text-ink"
            }`}
          >
            {item.text}
          </a>
        ))}
      </nav>
    </aside>
  );
}
