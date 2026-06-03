"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Dna, Code, Database, BookOpenText, House } from "@phosphor-icons/react";
import SidebarItem from "@/components/layout/SidebarItem";
import SearchInput from "@/components/search/SearchInput";
import { useRouter } from "next/navigation";

const NAV_ITEMS = [
  { icon: <House size={20} weight="bold" />, label: "首页", href: "/" },
  { icon: <Dna size={20} weight="bold" />, label: "分析流程", href: "/pipelines" },
  { icon: <Code size={20} weight="bold" />, label: "软件与算法", href: "/algorithms" },
  { icon: <Database size={20} weight="bold" />, label: "数据库导航", href: "/databases" },
  { icon: <BookOpenText size={20} weight="bold" />, label: "文献集", href: "/literatures" }
];

export default function Sidebar(): JSX.Element {
  const router = useRouter();
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("sidebar-expanded");
    if (stored !== null) {
      setExpanded(stored === "true");
    }
  }, []);

  function toggle(): void {
    const next = !expanded;
    setExpanded(next);
    localStorage.setItem("sidebar-expanded", String(next));
  }

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={`fixed bottom-0 left-0 top-0 z-30 hidden flex-col border-r border-slate-200/60 bg-white transition-all duration-200 lg:flex ${
          expanded ? "w-[220px]" : "w-[60px]"
        }`}
      >
        {/* Logo */}
        <div className="flex h-14 items-center gap-3 border-b border-slate-100 px-3">
          <Link href="/" className="flex items-center gap-3 shrink-0">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-accent text-sm font-bold text-white">
              B
            </span>
          </Link>
          {expanded ? (
            <Link href="/" className="text-sm font-semibold tracking-tight text-slate-900">
              Bioinformatics
            </Link>
          ) : null}
        </div>

        {/* Nav items */}
        <nav className="flex-1 space-y-0.5 px-3 py-4">
          {NAV_ITEMS.map((item) => (
            <SidebarItem
              key={item.href}
              icon={item.icon}
              label={item.label}
              href={item.href}
              expanded={expanded}
            />
          ))}
        </nav>

        {/* Search */}
        <div className="border-t border-slate-100 px-3 py-3">
          {expanded ? (
            <SearchInput
              size="sm"
              placeholder="搜索..."
              onSubmit={(q) => router.push(`/search?q=${encodeURIComponent(q)}`)}
            />
          ) : (
            <button
              onClick={() => router.push("/search")}
              className="flex h-9 w-9 items-center justify-center rounded-md text-slate-400 hover:bg-slate-50 hover:text-slate-600 transition-colors"
              aria-label="搜索"
            >
              <SearchIcon />
            </button>
          )}
        </div>

        {/* Toggle */}
        <button
          onClick={toggle}
          className="flex h-10 items-center justify-center border-t border-slate-100 text-slate-400 hover:bg-slate-50 hover:text-slate-600 transition-colors"
          aria-label={expanded ? "收起侧边栏" : "展开侧边栏"}
        >
          <ToggleIcon expanded={expanded} />
        </button>
      </aside>

      {/* Mobile bottom tab bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 flex h-14 items-center justify-around border-t border-slate-200 bg-white lg:hidden">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex flex-col items-center gap-0.5 px-2 py-1 text-[10px] font-medium text-slate-400 transition-colors hover:text-slate-600"
          >
            {item.icon}
            <span className="leading-none">{item.label}</span>
          </Link>
        ))}
      </nav>
    </>
  );
}

function SearchIcon(): JSX.Element {
  return (
    <svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor">
      <path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z" />
    </svg>
  );
}

function ToggleIcon({ expanded }: { expanded: boolean }): JSX.Element {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 256 256"
      fill="currentColor"
      className={`transition-transform ${expanded ? "" : "rotate-180"}`}
    >
      <path d="M165.66,202.34a8,8,0,0,1-11.32,11.32l-80-80a8,8,0,0,1,0-11.32l80-80a8,8,0,0,1,11.32,11.32L91.31,128Z" />
    </svg>
  );
}
