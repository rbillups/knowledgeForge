export type DashboardRecentDocument = {
  title: string;
  filename: string;
  collection_name: string;
  status: string;
  chunk_count: number;
  updated_at: string;
};

export type DashboardCollectionSummary = {
  id: number;
  slug: string;
  name: string;
  document_count: number;
  indexed_document_count: number;
  chunk_count: number;
};

export type DashboardSummary = {
  total_collections: number;
  total_documents: number;
  total_indexed_documents: number;
  total_processing_documents: number;
  total_failed_documents: number;
  total_chunks: number;
  recent_documents: DashboardRecentDocument[];
  collections: DashboardCollectionSummary[];
  api_status: string;
  database_status: string;
};
