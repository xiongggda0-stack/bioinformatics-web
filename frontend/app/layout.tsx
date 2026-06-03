import type { Metadata } from "next";
import type { ReactNode } from "react";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { Source_Serif_4 } from "next/font/google";
import { AppLayout } from "@/components/layout/AppLayout";
import "./globals.css";

const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-source-serif"
});

export const metadata: Metadata = {
  title: "生信云平台",
  description: "集分析流程、软件与算法、文献动态于一体的一站式生信云平台"
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps): JSX.Element {
  return (
    <html
      lang="zh-CN"
      className={`${GeistSans.variable} ${GeistMono.variable} ${sourceSerif.variable}`}
    >
      <body className="bg-white text-slate-900 antialiased">
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
