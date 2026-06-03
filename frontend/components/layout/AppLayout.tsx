import type { ReactNode } from "react";
import Sidebar from "@/components/layout/Sidebar";

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps): JSX.Element {
  return (
    <div className="min-h-screen">
      <Sidebar />
      <main className="pb-14 lg:ml-[60px] lg:pb-0">{children}</main>
    </div>
  );
}
