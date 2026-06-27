"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiStatusCard } from "@/components/dashboard/ApiStatusCard";
import { FeedbackSummaryCard } from "@/components/dashboard/FeedbackSummaryCard";
import { PortfolioSummaryCard } from "@/components/dashboard/PortfolioSummaryCard";
import { RecentDocuments } from "@/components/dashboard/RecentDocuments";
import { StatCard } from "@/components/ui/StatCard";
import { getDashboardSummary, getFeedbackSummary } from "@/lib/api";
import type { DashboardSummary } from "@/types/dashboard";
import type { FeedbackSummary } from "@/types/feedback";

const PORTFOLIO_SLUG = "portfolio";

function formatCount(value: number): string {
  return value.toLocaleString("en-US");
}

export function DashboardView() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [feedbackSummary, setFeedbackSummary] = useState<FeedbackSummary | null>(
    null,
  );
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [isFeedbackLoading, setIsFeedbackLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadSummary = useCallback(async () => {
    setIsLoading(true);
    setIsFeedbackLoading(true);
    setError(null);
    setFeedbackError(null);

    const [dashboardResult, feedbackResult] = await Promise.allSettled([
      getDashboardSummary(),
      getFeedbackSummary(),
    ]);

    if (dashboardResult.status === "fulfilled") {
      setSummary(dashboardResult.value);
    } else {
      setSummary(null);
      setError(
        dashboardResult.reason instanceof Error
          ? dashboardResult.reason.message
          : "Failed to load dashboard summary.",
      );
    }

    if (feedbackResult.status === "fulfilled") {
      setFeedbackSummary(feedbackResult.value);
    } else {
      setFeedbackSummary(null);
      setFeedbackError("Unable to load feedback summary.");
    }

    setIsLoading(false);
    setIsFeedbackLoading(false);
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

                <div className="mb-8">
                  <FeedbackSummaryCard
                    summary={feedbackSummary}
                    isLoading={isFeedbackLoading}
                    error={feedbackError}
                  />
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
