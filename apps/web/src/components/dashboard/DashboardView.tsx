"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiStatusCard } from "@/components/dashboard/ApiStatusCard";
import { PortfolioSummaryCard } from "@/components/dashboard/PortfolioSummaryCard";
import { RecentDocuments } from "@/components/dashboard/RecentDocuments";
import { StatCard } from "@/components/ui/StatCard";
import { getDashboardSummary } from "@/lib/api";
import type { DashboardSummary } from "@/types/dashboard";

const PORTFOLIO_SLUG = "portfolio";

function formatCount(value: number): string {
  return value.toLocaleString("en-US");
}

export function DashboardView() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadSummary = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const nextSummary = await getDashboardSummary();
      setSummary(nextSummary);
    } catch (err) {
      setSummary(null);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load dashboard summary.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  const portfolioCollection =
    summary?.collections.find(
      (collection) => collection.slug === PORTFOLIO_SLUG,
    ) ?? null;

  const documentsNeedingAttention = summary
    ? summary.total_processing_documents + summary.total_failed_documents
    : 0;

  return (
    <div className="px-6 py-8 lg:px-10">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          System overview and knowledge base metrics
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Loading dashboard summary...</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[0, 1, 2].map((index) => (
              <div
                key={index}
                className="h-28 animate-pulse rounded-xl border border-slate-200 bg-slate-50"
              />
            ))}
          </div>
        </div>
      ) : (
        <>
          <div className="mb-6">
            <ApiStatusCard summary={summary} error={error} />
          </div>

          {error ? (
            <div className="mb-8 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error} Make sure the KnowledgeForge API is running, then refresh
              this page.
            </div>
          ) : (
            summary && (
              <>
                <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  <StatCard
                    label="Knowledge Collections"
                    value={formatCount(summary.total_collections)}
                  />
                  <StatCard
                    label="Indexed Documents"
                    value={formatCount(summary.total_indexed_documents)}
                  />
                  <StatCard
                    label="Indexed Chunks"
                    value={formatCount(summary.total_chunks)}
                  />
                  {documentsNeedingAttention > 0 && (
                    <StatCard
                      label="Documents Needing Attention"
                      value={formatCount(documentsNeedingAttention)}
                    />
                  )}
                </div>

                <div className="mb-8">
                  <PortfolioSummaryCard collection={portfolioCollection} />
                </div>

                <RecentDocuments documents={summary.recent_documents} />
              </>
            )
          )}
        </>
      )}
    </div>
  );
}
