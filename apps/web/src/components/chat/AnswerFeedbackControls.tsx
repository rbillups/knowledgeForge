"use client";

import { useState } from "react";

import { submitFeedback } from "@/lib/api";
import { getFeedbackErrorMessage } from "@/lib/feedback";
import type { ChatCitation } from "@/types/chat";
import type { FeedbackType } from "@/types/feedback";

type AnswerFeedbackControlsProps = {
  collectionId: number;
  question: string;
  answer: string;
  citations?: ChatCitation[];
  onSubmitted: () => void;
};

export function AnswerFeedbackControls({
  collectionId,
  question,
  answer,
  citations,
  onSubmitted,
}: AnswerFeedbackControlsProps) {
  const [mode, setMode] = useState<"idle" | "comment">("idle");
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (feedbackType: FeedbackType, optionalComment?: string) => {
    setIsSubmitting(true);
    setError(null);

    try {
      await submitFeedback({
        collection_id: collectionId,
        question,
        answer,
        feedback_type: feedbackType,
        comment: optionalComment,
        citation_filenames: citations?.map((citation) => citation.filename),
      });
      onSubmitted();
    } catch (submitError) {
      setError(getFeedbackErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full space-y-2 px-1">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-slate-500">Was this answer helpful?</span>
        <button
          type="button"
          onClick={() => void submit("helpful")}
          disabled={isSubmitting}
          className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Helpful
        </button>
        <button
          type="button"
          onClick={() => setMode("comment")}
          disabled={isSubmitting}
          className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Not helpful
        </button>
      </div>

      {mode === "comment" && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <label className="block">
            <span className="mb-1.5 block text-xs font-medium text-slate-600">
              Optional comment
            </span>
            <textarea
              rows={2}
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              maxLength={500}
              disabled={isSubmitting}
              placeholder="Tell us what was missing or unclear..."
              className="w-full resize-none rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none disabled:cursor-not-allowed disabled:bg-slate-50"
            />
          </label>
          <div className="mt-2 flex items-center gap-2">
            <button
              type="button"
              onClick={() => void submit("not_helpful", comment.trim() || undefined)}
              disabled={isSubmitting}
              className="inline-flex h-8 items-center rounded-lg bg-slate-900 px-3 text-xs font-medium text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? "Submitting..." : "Submit feedback"}
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("idle");
                setComment("");
                setError(null);
              }}
              disabled={isSubmitting}
              className="inline-flex h-8 items-center rounded-lg border border-slate-200 px-3 text-xs font-medium text-slate-700 transition-colors hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
