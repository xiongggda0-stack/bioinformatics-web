interface SearchHighlightProps {
  text: string;
  query?: string;
}

export default function SearchHighlight({
  text,
  query = ""
}: SearchHighlightProps): JSX.Element {
  const keyword = query.trim();

  if (!keyword) {
    return <>{text}</>;
  }

  const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const parts = text.split(new RegExp(`(${escapedKeyword})`, "ig"));

  return (
    <>
      {parts.map((part, index) =>
        part.toLowerCase() === keyword.toLowerCase() ? (
          <mark
            key={`${part}-${index}`}
            className="rounded-sm bg-amber-100 px-0.5 text-inherit"
          >
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </>
  );
}
