import { ChatRequestError } from "@/lib/api";

export const SUGGESTED_PROMPTS = [
  "What is KnowledgeForge?",
  "What documents are available?",
  "How does source-grounded answering work?",
] as const;

export const INSUFFICIENT_CONTEXT_NOTE =
  "This answer is limited to the documents currently indexed in this collection.";

export function formatChatTimestamp(date: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export function formatSimilarityScore(score: number): string | null {
  if (!Number.isFinite(score) || score < 0 || score > 1) {
    return null;
  }

  return `${Math.round(score * 100)}% match`;
}

export function getChatErrorMessage(error: unknown): string {
  if (error instanceof ChatRequestError) {
    if (error.status === 422) {
      return "That question could not be processed. Please check your input and try again.";
    }

    if (error.status === 404) {
      return "The selected collection could not be found. Choose another collection and try again.";
    }

    if (error.status === 503) {
      return "The AI service is not configured yet. Contact your administrator or try again later.";
    }

    if (error.status >= 500 || error.status === 502) {
      return "The server ran into a problem while generating an answer. Please try again shortly.";
    }

    return "We could not get an answer right now. Please try again.";
  }

  if (error instanceof TypeError) {
    return "We could not reach the KnowledgeForge API. Make sure the backend is running and try again.";
  }

  return "Something went wrong while sending your question. Please try again.";
}
