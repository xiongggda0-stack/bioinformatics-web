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
}

function getLanguageLabel(className?: string): string {
  const language = className?.replace("language-", "").trim();

  if (!language) {
    return "Code";
  }

  const labels: Record<string, string> = {
    bash: "Bash",
    sh: "Shell",
    shell: "Shell",
    zsh: "Shell",
    r: "R",
    python: "Python",
    py: "Python",
    javascript: "JavaScript",
    js: "JavaScript",
    typescript: "TypeScript",
    ts: "TypeScript",
    sql: "SQL",
    yaml: "YAML",
    yml: "YAML",
    json: "JSON",
    text: "Text"
  };

  return labels[language.toLowerCase()] ?? language.toUpperCase();
}

export default function MarkdownRenderer({
  content,
  tocItems = []
}: MarkdownRendererProps): JSX.Element {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className="prose prose-slate max-w-none prose-headings:scroll-mt-24 prose-headings:font-semibold prose-h1:text-3xl prose-h2:border-b prose-h2:border-slate-200 prose-h2:pb-2 prose-a:text-teal prose-a:no-underline hover:prose-a:text-coral prose-strong:text-ink prose-code:rounded prose-code:bg-sky-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:text-[0.86em] prose-code:font-semibold prose-code:text-sky-800 prose-code:before:content-none prose-code:after:content-none prose-pre:m-0 prose-pre:bg-transparent prose-pre:p-0 prose-table:text-sm prose-th:bg-slate-950 prose-th:text-cyan-50 prose-td:border-slate-200"
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
              <code
                className="rounded bg-sky-50 px-1.5 py-0.5 font-semibold text-sky-800"
                {...props}
              >
                {children}
              </code>
            );
          }

          return (
            <div className="relative my-6 overflow-hidden rounded-lg border border-slate-200 bg-slate-50 shadow-sm">
              <pre className="m-0 overflow-x-auto p-5 pb-10 text-sm leading-7 text-slate-800">
                <code
                  className={`${className ?? ""} block min-w-max bg-transparent p-0 font-mono text-slate-800`}
                  {...props}
                >
                  {children}
                </code>
              </pre>
              <span className="pointer-events-none absolute bottom-2 right-3 rounded border border-slate-200 bg-white/90 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500 shadow-sm">
                {getLanguageLabel(className)}
              </span>
            </div>
          );
        },
        table: ({ children }) => (
          <div className="my-8 overflow-hidden rounded-lg border border-slate-200 shadow-sm">
            <div className="overflow-x-auto">
              <table className="m-0 w-full border-collapse">{children}</table>
            </div>
          </div>
        ),
        th: ({ children }) => (
          <th className="border-b border-slate-800 bg-slate-950 px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.12em] text-cyan-50">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="border-b border-slate-100 px-4 py-3 align-top text-sm text-slate-700">
            {children}
          </td>
        )
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
