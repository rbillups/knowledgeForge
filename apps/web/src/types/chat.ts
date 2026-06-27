export type ChatCitation = {
  document_title: string;
  filename: string;
  chunk_content: string;
  chunk_index: number;
  page_number: number | null;
  similarity_score: number;
};

export type ChatResponse = {
  answer: string;
  citations: ChatCitation[];
  insufficient_context: boolean;
  policy_blocked: boolean;
  model: string | null;
};

export type ChatMessageRole = "user" | "assistant" | "loading";

export type ChatMessage = {
  id: string;
  role: ChatMessageRole;
  content: string;
  timestamp: string;
  citations?: ChatCitation[];
  insufficientContext?: boolean;
  policyBlocked?: boolean;
  isError?: boolean;
};
