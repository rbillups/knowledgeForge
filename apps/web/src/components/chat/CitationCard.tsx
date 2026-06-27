import { formatSimilarityScore } from "@/lib/chat";
import type { ChatCitation } from "@/types/chat";

type CitationCardProps = {
  citation: ChatCitation;
  index: number;
};

export function CitationCard({ citation, index }: CitationCardProps) {
  const similarityLabel = formatSimilarityScore(citation.similarity_score);

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50">
      <div className="flex items-start justify-between gap-3 p-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded bg-slate-200 text-xs font-medium text-slate-600">
              {index}
            </span>
            <p className="truncate text-sm font-medium text-slate-900">
              {citation.document_title}
            </p>
          </div>
          <p className="mt-1 truncate pl-7 text-xs text-slate-500">
            {citation.filename}
            {citation.page_number !== null
              ? ` · Page ${citation.page_number}`
              : ""}
          </p>
        </div>
        {similarityLabel && (
          <span className="shrink-0 rounded-full bg-white px-2 py-0.5 text-xs text-slate-500 ring-1 ring-slate-200">
            {similarityLabel}
          </span>
        )}
      </div>

      <details className="group border-t border-slate-200">
        <summary className="cursor-pointer list-none px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-100 [&::-webkit-details-marker]:hidden">
          <span className="inline-flex items-center gap-1">
            View source
            <svg
              className="h-3.5 w-3.5 transition-transform group-open:rotate-180"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m19.5 8.25-7.5 7.5-7.5-7.5"
              />
            </svg>
          </span>
        </summary>
        <div className="border-t border-slate-200 bg-white px-3 py-3">
          <p className="text-sm leading-relaxed text-slate-600">
            {citation.chunk_content}
          </p>
        </div>
      </details>
    </div>
  );
}
