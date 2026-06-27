import { StatusBadge } from "@/components/documents/StatusBadge";
import type { DashboardRecentDocument } from "@/types/dashboard";
import { formatUploadedDate } from "@/lib/documents";
import type { DocumentStatus } from "@/types/documents";

type RecentDocumentsProps = {
  documents: DashboardRecentDocument[];
};

function displayDocumentName(document: DashboardRecentDocument): string {
  return document.title.trim() || document.filename;
}

export function RecentDocuments({ documents }: RecentDocumentsProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-base font-semibold text-slate-900">
          Recent documents
        </h2>
        <p className="mt-0.5 text-sm text-slate-500">
          Latest documents added or updated across your knowledge collections
        </p>
      </div>

      {documents.length === 0 ? (
        <div className="px-5 py-8 text-center text-sm text-slate-500">
          No documents indexed yet. Upload a document or import the portfolio
          source pack to populate your knowledge base.
        </div>
      ) : (
        <ul className="divide-y divide-slate-100">
          {documents.map((document) => (
            <li
              key={`${document.filename}-${document.updated_at}`}
              className="flex flex-col gap-3 px-5 py-4 transition-colors hover:bg-slate-50 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="text-sm font-medium text-slate-900">
                  {displayDocumentName(document)}
                </p>
                <p className="mt-0.5 text-sm text-slate-500">
                  {document.collection_name} · {document.filename} ·{" "}
                  {document.chunk_count} chunks
                </p>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={document.status as DocumentStatus} />
                <span className="text-xs text-slate-400">
                  {formatUploadedDate(document.updated_at)}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
