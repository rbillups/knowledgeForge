"use client";

import { useId, useState } from "react";

import { CitationCard } from "@/components/chat/CitationCard";
import { getCitationDisclosureLabel } from "@/lib/citations";
import type { ChatCitation } from "@/types/chat";

type CitationDisclosureProps = {
  citations: ChatCitation[];
};

export function CitationDisclosure({ citations }: CitationDisclosureProps) {
  const [expanded, setExpanded] = useState(false);
  const panelId = useId();
  const label = getCitationDisclosureLabel(citations.length);

  return (
    <div className="w-full pt-1">
      <button
        type="button"
        aria-expanded={expanded}
        aria-controls={panelId}
        onClick={() => setExpanded((current) => !current)}
        className="inline-flex w-full items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-left text-sm font-medium text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-100"
      >
        <span>{label}</span>
        <svg
          className={`h-4 w-4 shrink-0 text-slate-500 transition-transform ${
            expanded ? "rotate-180" : ""
          }`}
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
      </button>

      {expanded && (
        <div id={panelId} className="mt-2 space-y-2">
          {citations.map((citation, index) => (
            <CitationCard
              key={`${citation.filename}-${citation.chunk_index}-${index}`}
              citation={citation}
              index={index + 1}
              showSimilarityScore={false}
              showExcerptInline
            />
          ))}
        </div>
      )}
    </div>
  );
}
