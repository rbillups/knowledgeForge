import type { DocumentStatus, UploadFlowStatus } from "@/types/documents";

const ALLOWED_EXTENSIONS = new Set([".pdf", ".txt", ".md", ".markdown"]);

export function isAllowedUploadFile(file: File): boolean {
  const extension = file.name.includes(".")
    ? file.name.slice(file.name.lastIndexOf(".")).toLowerCase()
    : "";

  return ALLOWED_EXTENSIONS.has(extension);
}

export function formatFileType(fileType: string): string {
  switch (fileType.toLowerCase()) {
    case "pdf":
      return "PDF";
    case "txt":
      return "TXT";
    case "markdown":
      return "Markdown";
    default:
      return fileType.toUpperCase();
  }
}

export function formatUploadedDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export function mapDocumentStatusForDisplay(
  status: string,
): DocumentStatus | UploadFlowStatus {
  switch (status) {
    case "indexed":
      return "indexed";
    case "failed":
      return "failed";
    case "processing":
      return "processing";
    case "uploaded":
      return "processing";
    default:
      return "processing";
  }
}

import { DeleteRequestError, UploadRequestError } from "@/lib/api";

export function getUploadErrorMessage(error: unknown): string {
  if (error instanceof UploadRequestError) {
    const status = error.status;

    if (status === 400) {
      if (error.message.toLowerCase().includes("unsupported file type")) {
        return "That file type is not supported. Please upload a PDF, TXT, or Markdown file.";
      }
      if (error.message.toLowerCase().includes("empty")) {
        return "The selected file is empty. Choose a document with readable content and try again.";
      }
      return "We could not accept that upload. Please check the file and try again.";
    }

    if (status === 404) {
      return "The selected collection could not be found. Choose another collection and try again.";
    }

    if (status === 422) {
      return "We could not index that document. Make sure it contains readable text and try again.";
    }

    if (status && status >= 500) {
      return "The server ran into a problem while indexing your document. Please try again shortly.";
    }
  }

  if (error instanceof TypeError) {
    return "We could not reach the KnowledgeForge API. Make sure the backend is running and try again.";
  }

  return "Something went wrong while uploading your document. Please try again.";
}

export function getDeleteErrorMessage(error: unknown): string {
  if (error instanceof DeleteRequestError) {
    if (error.status === 404) {
      return "That document could not be found. Refresh the page and try again.";
    }

    if (error.status && error.status >= 500) {
      return "We could not delete that document right now. Please try again shortly.";
    }
  }

  if (error instanceof TypeError) {
    return "We could not reach the KnowledgeForge API. Make sure the backend is running and try again.";
  }

  return "Something went wrong while deleting the document. Please try again.";
}

export const UPLOAD_SUCCESS_MESSAGE =
  "Document indexed successfully. It is ready for future AI search.";

export const DELETE_SUCCESS_MESSAGE =
  "Document deleted successfully. Its chunks and embeddings were removed from the collection.";
