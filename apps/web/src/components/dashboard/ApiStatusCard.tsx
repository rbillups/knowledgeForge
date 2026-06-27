import { Badge } from "@/components/ui/Badge";
import type { DashboardSummary } from "@/types/dashboard";

type ApiStatusCardProps = {
  summary: DashboardSummary | null;
  error: string | null;
};

export function ApiStatusCard({ summary, error }: ApiStatusCardProps) {
  const isConnected = summary !== null && !error;
  const databaseOnline = summary?.database_status === "ok";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">Platform health</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {isConnected ? "Operational" : "Unavailable"}
          </p>
          {isConnected && summary && (
            <p className="mt-1 text-sm text-slate-500">
              API: {summary.api_status} · Database: {summary.database_status}
            </p>
          )}
          {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        </div>
        <Badge variant={isConnected && databaseOnline ? "success" : "error"}>
          {isConnected && databaseOnline ? "Healthy" : "Needs attention"}
        </Badge>
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <span
            className={`h-2 w-2 rounded-full ${
              isConnected ? "bg-emerald-500" : "bg-red-500"
            }`}
          />
          <span className="text-xs text-slate-400">
            {isConnected
              ? "Dashboard summary loaded from the API"
              : "Unable to reach GET /api/v1/dashboard/summary"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`h-2 w-2 rounded-full ${
              databaseOnline ? "bg-emerald-500" : "bg-amber-500"
            }`}
          />
          <span className="text-xs text-slate-400">
            {databaseOnline
              ? "Database connectivity check passed"
              : "Database connectivity check failed"}
          </span>
        </div>
      </div>
    </div>
  );
}
