import type { Document } from "@/types/documents";
import { formatFileType, formatUploadedDate } from "@/lib/documents";
import { StatusBadge } from "@/components/documents/StatusBadge";

type DocumentTableProps = {
  documents: Document[];
  isLoading: boolean;
};

export function DocumentTable({ documents, isLoading }: DocumentTableProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-base font-semibold text-slate-900">
          Document library
        </h2>
        <p className="mt-0.5 text-sm text-slate-500">
          Uploaded knowledge sources and their indexing status
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-xs font-medium uppercase tracking-wide text-slate-500">
              <th className="px-5 py-3">Name</th>
              <th className="px-5 py-3">Type</th>
              <th className="px-5 py-3">Chunks</th>
              <th className="px-5 py-3">Collection</th>
              <th className="px-5 py-3">Uploaded</th>
              <th className="px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              <tr>
                <td
                  className="px-5 py-8 text-center text-sm text-slate-500"
                  colSpan={6}
                >
                  Loading documents...
                </td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td
                  className="px-5 py-8 text-center text-sm text-slate-500"
                  colSpan={6}
                >
                  No documents yet. Upload your first PDF, TXT, or Markdown file
                  above.
                </td>
              </tr>
            ) : (
              documents.map((document) => (
                <tr
                  key={document.id}
                  className="transition-colors hover:bg-slate-50"
                >
                  <td className="px-5 py-3.5 font-medium text-slate-900">
                    {document.filename}
                  </td>
                  <td className="px-5 py-3.5 text-slate-500">
                    {formatFileType(document.file_type)}
                  </td>
                  <td className="px-5 py-3.5 text-slate-500">
                    {document.chunk_count}
                  </td>
                  <td className="px-5 py-3.5 text-slate-500">
                    {document.collection_name}
                  </td>
                  <td className="px-5 py-3.5 text-slate-500">
                    {formatUploadedDate(document.created_at)}
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={document.status} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
