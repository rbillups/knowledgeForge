import Link from "next/link";

import type { DashboardCollectionSummary } from "@/types/dashboard";

type PortfolioSummaryCardProps = {
  collection: DashboardCollectionSummary | null;
};

export function PortfolioSummaryCard({ collection }: PortfolioSummaryCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">
            Portfolio Knowledge Base
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-900">
            {collection?.name ?? "Portfolio Knowledge Base"}
          </h2>
          {collection ? (
            <dl className="mt-4 grid gap-3 sm:grid-cols-3">
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Documents
                </dt>
                <dd className="mt-1 text-2xl font-semibold text-slate-900">
                  {collection.document_count}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Indexed
                </dt>
                <dd className="mt-1 text-2xl font-semibold text-slate-900">
                  {collection.indexed_document_count}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Chunks
                </dt>
                <dd className="mt-1 text-2xl font-semibold text-slate-900">
                  {collection.chunk_count}
                </dd>
              </div>
            </dl>
          ) : (
            <p className="mt-4 text-sm text-slate-500">
              The portfolio collection has not been created yet. Import the
              portfolio source pack to get started.
            </p>
          )}
        </div>

        <Link
          href="/documents"
          className="inline-flex h-10 items-center justify-center rounded-lg bg-slate-900 px-4 text-sm font-medium text-white transition-colors hover:bg-slate-800"
        >
          Open documents
        </Link>
      </div>

      {collection && collection.document_count === 0 && (
        <div className="mt-5 rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
          This collection is empty. Import the portfolio source pack or upload
          your first document to begin indexing.
        </div>
      )}
    </div>
  );
}
