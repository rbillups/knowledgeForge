import { DocumentTable } from "@/components/documents/DocumentTable";
import { mockDocuments } from "@/data/mock/documents";

export default function DocumentsPage() {
  return (
    <div className="px-6 py-8 lg:px-10">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Documents
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Upload and manage knowledge sources for indexing
        </p>
      </div>

      <DocumentTable documents={mockDocuments} />
    </div>
  );
}
