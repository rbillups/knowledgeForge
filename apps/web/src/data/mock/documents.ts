type MockDocumentRecord = {
  id: string;
  name: string;
  type: string;
  size: string;
  collection: string;
  uploadedAt: string;
  status: "indexed" | "processing" | "queued" | "failed";
};

export const mockDocuments: MockDocumentRecord[] = [
  {
    id: "doc-1",
    name: "Security Operations Manual.pdf",
    type: "PDF",
    size: "4.2 MB",
    collection: "Security & Compliance",
    uploadedAt: "Jun 24, 2026",
    status: "indexed",
  },
  {
    id: "doc-2",
    name: "Engineering Onboarding Guide.docx",
    type: "DOCX",
    size: "1.8 MB",
    collection: "Engineering Handbook",
    uploadedAt: "Jun 23, 2026",
    status: "indexed",
  },
  {
    id: "doc-3",
    name: "Q2 Product Roadmap.pptx",
    type: "PPTX",
    size: "6.1 MB",
    collection: "Product Launch Materials",
    uploadedAt: "Jun 22, 2026",
    status: "processing",
  },
  {
    id: "doc-4",
    name: "Support Escalation Matrix.xlsx",
    type: "XLSX",
    size: "892 KB",
    collection: "Customer Support Playbooks",
    uploadedAt: "Jun 21, 2026",
    status: "indexed",
  },
  {
    id: "doc-5",
    name: "Vendor Risk Assessment Template.pdf",
    type: "PDF",
    size: "2.3 MB",
    collection: "Security & Compliance",
    uploadedAt: "Jun 20, 2026",
    status: "queued",
  },
  {
    id: "doc-6",
    name: "Legacy API Documentation.html",
    type: "HTML",
    size: "540 KB",
    collection: "Engineering Handbook",
    uploadedAt: "Jun 18, 2026",
    status: "failed",
  },
];
