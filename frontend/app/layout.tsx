import type { Metadata } from "next";
import type { ReactNode } from "react";
import Navbar from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "生信云平台 MVP",
  description: "集分析流程、软件与算法、文献动态于一体的一站式生信云平台"
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps): JSX.Element {
  return (
    <html lang="zh-CN">
      <body className="bg-slate-50 text-ink antialiased">
        <Navbar />
        {children}
      </body>
    </html>
  );
}
