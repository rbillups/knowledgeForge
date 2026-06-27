export type DocumentStatus =
  | "uploaded"
  | "processing"
  | "indexed"
  | "failed";

export type UploadFlowStatus =
  | "idle"
  | "uploading"
  | "processing"
  | "indexed"
  | "failed";

export type Document = {
  id: number;
  collection_id: number;
  collection_name: string;
  filename: string;
  title: string;
  file_type: string;
  source_type: string;
  status: DocumentStatus;
  page_count: number | null;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentUploadResponse = {
  id: number;
  filename: string;
  title: string;
  file_type: string;
  status: DocumentStatus;
  chunk_count: number;
  page_count: number | null;
  message: string;
};
