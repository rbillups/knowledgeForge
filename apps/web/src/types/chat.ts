export type Citation = {
  id: string;
  title: string;
  excerpt: string;
  page?: string;
  relevance: number;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  citations?: Citation[];
};
