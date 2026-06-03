"use client";

interface SearchInputProps {
  size: "sm" | "lg";
  placeholder: string;
  onSubmit: (query: string) => void;
}

export default function SearchInput({
  size,
  placeholder,
  onSubmit
}: SearchInputProps): JSX.Element {
  const height = size === "lg" ? "h-14" : "h-9";
  const iconSize = size === "lg" ? 22 : 16;
  const textSize = size === "lg" ? "text-base" : "text-sm";

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>): void {
    if (e.key === "Enter") {
      const q = (e.target as HTMLInputElement).value.trim();
      if (q.length >= 1) {
        onSubmit(q);
      }
    }
  }

  return (
    <div className="relative w-full">
      <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
        <SearchIcon size={iconSize} />
      </span>
      <input
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={`${height} ${textSize} w-full rounded-md border border-slate-200 bg-slate-50 pl-9 pr-4 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-accent focus:bg-white focus:ring-2 focus:ring-accent/10`}
      />
    </div>
  );
}

function SearchIcon({ size }: { size: number }): JSX.Element {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 256 256"
      fill="currentColor"
    >
      <path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z" />
    </svg>
  );
}
