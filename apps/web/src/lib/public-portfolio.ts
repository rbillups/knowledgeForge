import { ChatRequestError } from "@/lib/api";

export const PUBLIC_PORTFOLIO_PROMPTS = [
  "What kind of software engineer is Key'Shawn?",
  "What is KnowledgeForge?",
  "What projects has he built?",
  "What technical skills does he use?",
  "What career areas is he focused on?",
] as const;

export const PUBLIC_PORTFOLIO_INTRO =
  "Answers are generated only from Key'Shawn Billups' public portfolio materials.";

export const PUBLIC_PORTFOLIO_INCOMPLETE_NOTE =
  "Answers may be incomplete when information is not included in public portfolio sources.";

export const PUBLIC_INSUFFICIENT_CONTEXT_NOTE =
  "This answer is limited to the public portfolio materials currently indexed.";

export function getPublicPortfolioChatErrorMessage(error: unknown): string {
  if (error instanceof ChatRequestError) {
    if (error.status === 429) {
      return "Too many questions were sent in a short period. Please wait a few minutes and try again.";
    }

    if (error.status === 404) {
      return "The portfolio assistant is not available right now. Please try again later.";
    }

    if (error.status === 422) {
      return "That question could not be processed. Please check your input and try again.";
    }

    if (error.status === 503) {
      return "The assistant is temporarily unavailable. Please try again later.";
    }

    if (error.status >= 500 || error.status === 502) {
      return "The assistant ran into a problem while generating an answer. Please try again shortly.";
    }
  }

  if (error instanceof TypeError) {
    return "We could not reach the assistant service. Please try again later.";
  }

  return "Something went wrong while sending your question. Please try again.";
}
