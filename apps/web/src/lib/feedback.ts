import { FeedbackRequestError } from "@/lib/api";

export const FEEDBACK_SUCCESS_MESSAGE = "Thanks for the feedback.";

export function getFeedbackErrorMessage(error: unknown): string {
  if (error instanceof FeedbackRequestError) {
    if (error.status === 404) {
      return "That knowledge collection could not be found. Refresh the page and try again.";
    }

    if (error.status && error.status >= 500) {
      return "We could not record your feedback right now. Please try again shortly.";
    }
  }

  if (error instanceof TypeError) {
    return "We could not reach the KnowledgeForge API. Make sure the backend is running and try again.";
  }

  return "Something went wrong while submitting feedback. Please try again.";
}

export function formatFeedbackPercentage(value: number | null): string {
  if (value === null) {
    return "—";
  }

  return `${value.toLocaleString("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  })}%`;
}

export function formatFeedbackTypeLabel(feedbackType: "helpful" | "not_helpful"): string {
  return feedbackType === "helpful" ? "Helpful" : "Not helpful";
}
