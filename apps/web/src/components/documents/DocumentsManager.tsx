"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { DeleteConfirmDialog } from "@/components/documents/DeleteConfirmDialog";
import { DocumentTable } from "@/components/documents/DocumentTable";
import { StatusBadge } from "@/components/documents/StatusBadge";
import { deleteDocument, getCollections, getDocuments, uploadDocument } from "@/lib/api";
import {
  DELETE_SUCCESS_MESSAGE,
  getDeleteErrorMessage,
  getUploadErrorMessage,
  isAllowedUploadFile,
  UPLOAD_SUCCESS_MESSAGE,
} from "@/lib/documents";
import type { Collection } from "@/types/collection";
import type { Document, UploadFlowStatus } from "@/types/documents";

const PORTFOLIO_SLUG = "portfolio";

export function DocumentsManager() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState<number | null>(
    null,
  );
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadFlowStatus>("idle");
  const [feedback, setFeedback] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Document | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);

  const loadPageData = useCallback(async () => {
    setIsLoading(true);
    setPageError(null);

    try {
      const [nextCollections, nextDocuments] = await Promise.all([
        getCollections(),
        getDocuments(),
      ]);

      setCollections(nextCollections);
      setDocuments(nextDocuments);

      setSelectedCollectionId((current) => {
        if (
          current &&
          nextCollections.some((collection) => collection.id === current)
        ) {
          return current;
        }

        const portfolioCollection = nextCollections.find(
          (collection) => collection.slug === PORTFOLIO_SLUG,
        );

        return portfolioCollection?.id ?? nextCollections[0]?.id ?? null;
      });
    } catch {
      setPageError(
        "We could not load your document library. Make sure the KnowledgeForge API is running and refresh the page.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPageData();
  }, [loadPageData]);

  const handleFileSelection = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setFeedback(null);
    setUploadStatus("idle");
    setSelectedFileName(file?.name ?? null);
  };

  const handleUpload = async () => {
    const file = fileInputRef.current?.files?.[0];

    setFeedback(null);

    if (!selectedCollectionId) {
      setFeedback({
        type: "error",
        message:
          "Choose a knowledge collection before uploading a document.",
      });
      return;
    }

    if (!file) {
      setFeedback({
        type: "error",
        message: "Choose a PDF, TXT, or Markdown file to upload.",
      });
      return;
    }

    if (!isAllowedUploadFile(file)) {
      setFeedback({
        type: "error",
        message:
          "That file type is not supported. Please upload a PDF, TXT, or Markdown file.",
      });
      return;
    }

    setIsUploading(true);
    setUploadStatus("uploading");

    try {
      setUploadStatus("processing");
      await uploadDocument(selectedCollectionId, file);

      setUploadStatus("indexed");
      setFeedback({
        type: "success",
        message: UPLOAD_SUCCESS_MESSAGE,
      });
      setSelectedFileName(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      const nextDocuments = await getDocuments();
      setDocuments(nextDocuments);
    } catch (error) {
      setUploadStatus("failed");
      setFeedback({
        type: "error",
        message: getUploadErrorMessage(error),
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteRequest = (document: Document) => {
    setFeedback(null);
    setDeleteTarget(document);
  };

  const handleDeleteCancel = () => {
    if (!isDeleting) {
      setDeleteTarget(null);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) {
      return;
    }

    setIsDeleting(true);
    setFeedback(null);

    try {
      await deleteDocument(deleteTarget.id);
      const nextDocuments = await getDocuments();
      setDocuments(nextDocuments);
      setDeleteTarget(null);
      setFeedback({
        type: "success",
        message: DELETE_SUCCESS_MESSAGE,
      });
    } catch (error) {
      setFeedback({
        type: "error",
        message: getDeleteErrorMessage(error),
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const selectedCollection = collections.find(
    (collection) => collection.id === selectedCollectionId,
  );

  return (
    <div className="space-y-6">
      {pageError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {pageError}
        </div>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-4">
            <div>
              <h2 className="text-base font-semibold text-slate-900">
                Upload a document
              </h2>
              <p className="mt-0.5 text-sm text-slate-500">
                Add a PDF, TXT, or Markdown file to your selected knowledge
                collection.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-slate-700">
                  Knowledge collection
                </span>
                <select
                  value={selectedCollectionId ?? ""}
                  onChange={(event) =>
                    setSelectedCollectionId(Number(event.target.value))
                  }
                  disabled={isLoading || collections.length === 0 || isUploading}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition-colors focus:border-slate-400 disabled:cursor-not-allowed disabled:bg-slate-50"
                >
                  {collections.length === 0 ? (
                    <option value="">No collections available</option>
                  ) : (
                    collections.map((collection) => (
                      <option key={collection.id} value={collection.id}>
                        {collection.name}
                      </option>
                    ))
                  )}
                </select>
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-slate-700">
                  Document file
                </span>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.md,.markdown,application/pdf,text/plain,text/markdown"
                  onChange={handleFileSelection}
                  disabled={isUploading}
                  className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200 disabled:cursor-not-allowed disabled:bg-slate-50"
                />
              </label>
            </div>

            {selectedCollection?.description && (
              <p className="text-sm text-slate-500">
                {selectedCollection.description}
              </p>
            )}

            {selectedFileName && (
              <p className="text-sm text-slate-600">
                Selected file:{" "}
                <span className="font-medium text-slate-900">
                  {selectedFileName}
                </span>
              </p>
            )}
          </div>

          <button
            type="button"
            onClick={() => void handleUpload()}
            disabled={
              isLoading ||
              isUploading ||
              collections.length === 0 ||
              !selectedCollectionId
            }
            className="inline-flex h-10 items-center justify-center rounded-lg bg-slate-900 px-4 text-sm font-medium text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isUploading ? "Uploading..." : "Upload document"}
          </button>
        </div>

        {uploadStatus !== "idle" && (
          <div className="mt-4 flex items-center gap-3 border-t border-slate-100 pt-4">
            <span className="text-sm font-medium text-slate-700">
              Upload status
            </span>
            <StatusBadge status={uploadStatus} />
          </div>
        )}

        {feedback && (
          <div
            className={`mt-4 rounded-lg px-4 py-3 text-sm ${
              feedback.type === "success"
                ? "border border-emerald-200 bg-emerald-50 text-emerald-800"
                : "border border-red-200 bg-red-50 text-red-700"
            }`}
          >
            {feedback.message}
          </div>
        )}
      </section>

      <DocumentTable
        documents={documents}
        isLoading={isLoading}
        deletingFilename={isDeleting ? deleteTarget?.filename ?? null : null}
        onDeleteRequest={handleDeleteRequest}
      />

      <DeleteConfirmDialog
        filename={deleteTarget?.filename ?? ""}
        isOpen={deleteTarget !== null}
        isDeleting={isDeleting}
        onConfirm={() => void handleDeleteConfirm()}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
}
