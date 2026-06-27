export type FeedbackType = "helpful" | "not_helpful";

export type FeedbackCreateRequest = {
  collection_id: number;
  question: string;
  answer: string;
  feedback_type: FeedbackType;
  comment?: string;
  citation_filenames?: string[];
};

export type FeedbackCreateResponse = {
  message: string;
};

export type FeedbackRecentEntry = {
  question_preview: string;
  feedback_type: FeedbackType;
  created_at: string;
};

export type FeedbackSummary = {
  total_feedback: number;
  helpful_count: number;
  not_helpful_count: number;
  helpful_percentage: number | null;
  recent_feedback: FeedbackRecentEntry[];
};
