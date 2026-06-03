"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

interface SidebarItemProps {
  icon: ReactNode;
  label: string;
  href: string;
  expanded: boolean;
}

function isActivePath(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export default function SidebarItem({
  icon,
  label,
  href,
  expanded
}: SidebarItemProps): JSX.Element {
  const pathname = usePathname();
  const active = isActivePath(pathname, href);

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 rounded-md px-2.5 py-2 text-sm font-medium transition-colors ${
        active
          ? "bg-accent-subtle text-accent"
          : "text-slate-500 hover:bg-slate-50 hover:text-slate-700"
      }`}
    >
      <span className="flex h-5 w-5 shrink-0 items-center justify-center">
        {icon}
      </span>
      {expanded ? <span>{label}</span> : null}
    </Link>
  );
}
