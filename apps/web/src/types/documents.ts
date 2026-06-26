export type DocumentUploadStatus =
  | "indexed"
  | "processing"
  | "queued"
  | "failed";

export type DocumentRecord = {
  id: string;
  name: string;
  type: string;
  size: string;
  collection: string;
  uploadedAt: string;
  status: DocumentUploadStatus;
};
