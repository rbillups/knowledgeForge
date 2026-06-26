import type { Citation } from "@/types/chat";

type CitationCardProps = {
  citation: Citation;
  index: number;
};

export function CitationCard({ citation, index }: CitationCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded bg-slate-200 text-xs font-medium text-slate-600">
            {index}
          </span>
          <p className="text-sm font-medium text-slate-900">{citation.title}</p>
        </div>
        {citation.page && (
          <span className="shrink-0 text-xs text-slate-400">{citation.page}</span>
        )}
      </div>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">
        {citation.excerpt}
      </p>
      <p className="mt-2 text-xs text-slate-400">
        Relevance: {Math.round(citation.relevance * 100)}%
      </p>
    </div>
  );
}
