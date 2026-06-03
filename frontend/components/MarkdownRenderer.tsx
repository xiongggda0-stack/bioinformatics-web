import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface TocItem {
  id: string;
  level: 2 | 3;
  text: string;
}

interface MarkdownRendererProps {
  content: string;
  tocItems?: TocItem[];
  useSerif?: boolean;
}

export default function MarkdownRenderer({
  content,
  tocItems = [],
  useSerif = false
}: MarkdownRendererProps): JSX.Element {
  const proseClass = useSerif
    ? "prose prose-slate font-serif max-w-none"
    : "prose prose-slate max-w-none";

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className={`${proseClass} prose-headings:scroll-mt-24 prose-headings:font-semibold prose-h1:text-2xl prose-h2:border-b prose-h2:border-slate-100 prose-h2:pb-2 prose-h2:text-xl prose-a:text-accent prose-a:no-underline prose-strong:text-slate-900 prose-code:rounded prose-code:bg-slate-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:text-[0.86em] prose-code:font-medium prose-code:text-slate-700 prose-code:before:content-none prose-code:after:content-none prose-pre:m-0 prose-pre:bg-transparent prose-pre:p-0 prose-table:text-sm prose-th:bg-slate-900 prose-th:text-white prose-td:border-slate-100`}
      components={{
        h2: ({ children }) => {
          const text = String(children);
          const item = tocItems.find((tocItem) => tocItem.text === text && tocItem.level === 2);
          return (
            <h2 id={item?.id} className="scroll-mt-24">
              {children}
            </h2>
          );
        },
        h3: ({ children }) => {
          const text = String(children);
          const item = tocItems.find((tocItem) => tocItem.text === text && tocItem.level === 3);
          return (
            <h3 id={item?.id} className="scroll-mt-24">
              {children}
            </h3>
          );
        },
        pre: ({ children }) => <>{children}</>,
        code: ({ children, className, node: _node, ...props }) => {
          const isCodeBlock = Boolean(className);
          if (!isCodeBlock) {
            return (
              <code className="rounded bg-slate-100 px-1.5 py-0.5 font-medium text-slate-700" {...props}>
                {children}
              </code>
            );
          }
          return (
            <div className="relative my-6 overflow-hidden rounded-md border border-slate-200 bg-slate-50">
              <pre className="m-0 overflow-x-auto p-5 pb-10 text-sm leading-7 text-slate-800">
                <code className={`${className ?? ""} block min-w-max bg-transparent p-0 font-mono text-slate-800`} {...props}>
                  {children}
                </code>
              </pre>
            </div>
          );
        },
        table: ({ children }) => (
          <div className="my-8 overflow-hidden rounded-md border border-slate-200">
            <div className="overflow-x-auto">
              <table className="m-0 w-full border-collapse">{children}</table>
            </div>
          </div>
        ),
        th: ({ children }) => (
          <th className="border-b border-slate-200 bg-slate-900 px-4 py-3 text-left text-xs font-medium uppercase tracking-[0.12em] text-white">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="border-b border-slate-100 px-4 py-3 align-top text-sm text-slate-600">
            {children}
          </td>
        )
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
