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
  model: string;
};

export type ChatMessageRole = "user" | "assistant" | "loading";

export type ChatMessage = {
  id: string;
  role: ChatMessageRole;
  content: string;
  timestamp: string;
  citations?: ChatCitation[];
  insufficientContext?: boolean;
  isError?: boolean;
};
