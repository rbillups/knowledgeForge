import { formatFeedbackPercentage, formatFeedbackTypeLabel } from "@/lib/feedback";
import { formatUploadedDate } from "@/lib/documents";
import type { FeedbackSummary } from "@/types/feedback";

type FeedbackSummaryCardProps = {
  summary: FeedbackSummary | null;
  isLoading: boolean;
  error: string | null;
};

export function FeedbackSummaryCard({
  summary,
  isLoading,
  error,
}: FeedbackSummaryCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-base font-semibold text-slate-900">
          Feedback summary
        </h2>
        <p className="mt-0.5 text-sm text-slate-500">
          Anonymous helpful and not helpful ratings from chat answers
        </p>
      </div>

      {isLoading ? (
        <div className="px-5 py-8 text-sm text-slate-500">
          Loading feedback summary...
        </div>
      ) : error ? (
        <div className="px-5 py-8 text-sm text-slate-500">
          Feedback summary is unavailable right now.
        </div>
      ) : summary && summary.total_feedback > 0 ? (
        <>
          <div className="grid gap-4 border-b border-slate-100 px-5 py-4 sm:grid-cols-2">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Responses rated
              </p>
              <p className="mt-1 text-2xl font-semibold text-slate-900">
                {summary.total_feedback.toLocaleString("en-US")}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Helpful percentage
              </p>
              <p className="mt-1 text-2xl font-semibold text-slate-900">
                {formatFeedbackPercentage(summary.helpful_percentage)}
              </p>
            </div>
          </div>

          <ul className="divide-y divide-slate-100">
            {summary.recent_feedback.map((entry) => (
              <li
                key={`${entry.created_at}-${entry.question_preview}`}
                className="flex flex-col gap-2 px-5 py-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    {entry.question_preview}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {formatFeedbackTypeLabel(entry.feedback_type)}
                  </p>
                </div>
                <span className="text-xs text-slate-400">
                  {formatUploadedDate(entry.created_at)}
                </span>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <div className="px-5 py-8 text-center text-sm text-slate-500">
          No feedback recorded yet. Helpful and not helpful ratings from chat
          will appear here once users start rating answers.
        </div>
      )}
    </div>
  );
}
