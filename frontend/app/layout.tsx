import type { Metadata } from "next";
import type { ReactNode } from "react";
import Navbar from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "生信知识平台",
  description:
    "面向公开浏览与学习复用的生信知识平台，连接分析流程、软件算法、数据库入口和文献证据。"
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
