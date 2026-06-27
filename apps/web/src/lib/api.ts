import type { Collection } from "@/types/collection";
import type { ChatResponse } from "@/types/chat";
import type {
  Document,
  DocumentDeleteResponse,
  DocumentUploadResponse,
} from "@/types/documents";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export type HealthResponse = {
  status: string;
  service: string;
};

function getApiUrl(): string {
  if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured.");
  }
  return API_URL;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string | unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Fall through to generic messaging.
  }

  return "Something went wrong while communicating with the server.";
}

export async function getApiHealth(): Promise<HealthResponse> {
  const response = await fetch(`${getApiUrl()}/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to connect to the KnowledgeForge API.");
  }

  return response.json() as Promise<HealthResponse>;
}

export async function getCollections(): Promise<Collection[]> {
  const response = await fetch(`${getApiUrl()}/api/v1/collections`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load knowledge collections.");
  }

  return response.json() as Promise<Collection[]>;
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${getApiUrl()}/api/v1/documents`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load documents.");
  }

  return response.json() as Promise<Document[]>;
}

export async function uploadDocument(
  collectionId: number,
  file: File,
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("collection_id", String(collectionId));
  formData.append("file", file);

  const response = await fetch(`${getApiUrl()}/api/v1/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const detail = await readErrorMessage(response);
    throw new UploadRequestError(response.status, detail);
  }

  return response.json() as Promise<DocumentUploadResponse>;
}

export async function deleteDocument(
  documentId: number,
): Promise<DocumentDeleteResponse> {
  const response = await fetch(`${getApiUrl()}/api/v1/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const detail = await readErrorMessage(response);
    throw new DeleteRequestError(response.status, detail);
  }

  return response.json() as Promise<DocumentDeleteResponse>;
}

export async function chatWithKnowledgeBase(
  collectionId: number,
  question: string,
  retrievalLimit?: number,
): Promise<ChatResponse> {
  const payload: {
    collection_id: number;
    question: string;
    retrieval_limit?: number;
  } = {
    collection_id: collectionId,
    question: question.trim(),
  };

  if (retrievalLimit !== undefined) {
    payload.retrieval_limit = retrievalLimit;
  }

  const response = await fetch(`${getApiUrl()}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await readErrorMessage(response);
    throw new ChatRequestError(response.status, detail);
  }

  return response.json() as Promise<ChatResponse>;
}

export class UploadRequestError extends Error {
  status: number;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "UploadRequestError";
    this.status = status;
  }
}

export class DeleteRequestError extends Error {
  status: number;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "DeleteRequestError";
    this.status = status;
  }
}

export class ChatRequestError extends Error {
  status: number;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ChatRequestError";
    this.status = status;
  }
}
