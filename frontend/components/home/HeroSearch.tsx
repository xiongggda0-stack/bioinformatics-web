"use client";

import { useRouter } from "next/navigation";
import SearchInput from "@/components/search/SearchInput";

export default function HeroSearch(): JSX.Element {
  const router = useRouter();

  return (
    <SearchInput
      size="lg"
      placeholder="搜索流程、软件、数据库或文献..."
      onSubmit={(q) => router.push(`/search?q=${encodeURIComponent(q)}`)}
    />
  );
}
