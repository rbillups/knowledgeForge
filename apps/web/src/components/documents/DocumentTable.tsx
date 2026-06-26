import { Badge } from "@/components/ui/Badge";
import type { DocumentRecord, DocumentUploadStatus } from "@/types/documents";

const statusConfig: Record<
  DocumentUploadStatus,
  { label: string; variant: "success" | "warning" | "default" | "error" }
> = {
  indexed: { label: "Indexed", variant: "success" },
  processing: { label: "Processing", variant: "warning" },
  queued: { label: "Queued", variant: "default" },
  failed: { label: "Failed", variant: "error" },
};

type StatusBadgeProps = {
  status: DocumentUploadStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

type DocumentTableProps = {
  documents: DocumentRecord[];
};

export function DocumentTable({ documents }: DocumentTableProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">
            Document library
          </h2>
          <p className="mt-0.5 text-sm text-slate-500">
            Manage uploaded knowledge sources and indexing status
          </p>
        </div>
        <button
          type="button"
          disabled
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white opacity-50"
        >
          Upload document
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-xs font-medium uppercase tracking-wide text-slate-500">
              <th className="px-5 py-3">Name</th>
              <th className="px-5 py-3">Type</th>
              <th className="px-5 py-3">Size</th>
              <th className="px-5 py-3">Collection</th>
              <th className="px-5 py-3">Uploaded</th>
              <th className="px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {documents.map((doc) => (
              <tr key={doc.id} className="transition-colors hover:bg-slate-50">
                <td className="px-5 py-3.5 font-medium text-slate-900">
                  {doc.name}
                </td>
                <td className="px-5 py-3.5 text-slate-500">{doc.type}</td>
                <td className="px-5 py-3.5 text-slate-500">{doc.size}</td>
                <td className="px-5 py-3.5 text-slate-500">{doc.collection}</td>
                <td className="px-5 py-3.5 text-slate-500">{doc.uploadedAt}</td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={doc.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
