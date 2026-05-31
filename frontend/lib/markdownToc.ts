import type { TocItem } from "@/components/MarkdownRenderer";

function slugify(text: string, index: number): string {
  return `${index + 1}-${text
    .trim()
    .toLowerCase()
    .replace(/[`~!@#$%^&*()+=\[\]{}|\\:;"'<>,.?/]/g, "")
    .replace(/\s+/g, "-")
    .slice(0, 80)}`;
}

export function extractTocItems(markdown: string): TocItem[] {
  const headingPattern = /^(##|###)\s+(.+)$/gm;
  const items: TocItem[] = [];
  let match: RegExpExecArray | null;

  while ((match = headingPattern.exec(markdown)) !== null) {
    const level = match[1].length as 2 | 3;
    const text = match[2].replace(/[#*`]/g, "").trim();

    if (text.length > 0) {
      items.push({
        id: slugify(text, items.length),
        level,
        text
      });
    }
  }

  return items;
}
