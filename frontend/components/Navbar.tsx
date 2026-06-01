"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import GlobalSearch from "@/components/GlobalSearch";

interface NavItem {
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  { label: "首页", href: "/" },
  { label: "分析流程", href: "/pipelines" },
  { label: "学习路径", href: "/learning-paths" },
  { label: "软件与算法", href: "/algorithms" },
  { label: "数据库导航", href: "/databases" },
  { label: "文献集", href: "/literatures" }
];

function isActivePath(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

export default function Navbar(): JSX.Element {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex w-full min-w-0 max-w-7xl flex-col gap-3 px-6 py-3 lg:h-16 lg:flex-row lg:items-center lg:justify-between lg:py-0">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded bg-teal text-sm font-bold text-white shadow-sm">
              Bio
            </span>
            <span className="text-base font-semibold tracking-tight text-ink">
              生信知识平台
            </span>
          </Link>

          <div className="hidden items-center gap-0.5 2xl:flex">
            {navItems.map((item) => {
              const active = isActivePath(pathname, item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded px-3 py-2 text-sm font-medium transition ${
                    active
                      ? "bg-teal/10 text-teal"
                      : "text-slate-600 hover:bg-mist hover:text-teal"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>

        <div className="flex min-w-0 flex-col gap-3 lg:flex-1 lg:flex-row lg:items-center lg:justify-end">
          <div className="min-w-0 lg:max-w-sm xl:max-w-md">
            <GlobalSearch />
          </div>

          <div className="flex w-full min-w-0 items-center gap-1 overflow-x-auto 2xl:hidden">
            {navItems.map((item) => {
              const active = isActivePath(pathname, item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`shrink-0 rounded px-3 py-2 text-sm font-medium transition ${
                    active
                      ? "bg-teal/10 text-teal"
                      : "text-slate-600 hover:bg-mist hover:text-teal"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
    </header>
  );
}
