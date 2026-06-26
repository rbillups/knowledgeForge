import { Badge } from "@/components/ui/Badge";
import type { HealthResponse } from "@/lib/api";

type ApiStatusCardProps = {
  health: HealthResponse | null;
  error: string | null;
};

export function ApiStatusCard({ health, error }: ApiStatusCardProps) {
  const isConnected = health !== null && !error;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">API connection</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {isConnected ? "Connected" : "Disconnected"}
          </p>
          {isConnected && health && (
            <p className="mt-1 text-sm text-slate-500">
              Service: {health.service} · Status: {health.status}
            </p>
          )}
          {error && (
            <p className="mt-1 text-sm text-red-600">{error}</p>
          )}
        </div>
        <Badge variant={isConnected ? "success" : "error"}>
          {isConnected ? "Online" : "Offline"}
        </Badge>
      </div>
      <div className="mt-4 flex items-center gap-2">
        <span
          className={`h-2 w-2 rounded-full ${
            isConnected ? "bg-emerald-500" : "bg-red-500"
          }`}
        />
        <span className="text-xs text-slate-400">
          {isConnected
            ? "Backend health check passed"
            : "Unable to reach GET /health"}
        </span>
      </div>
    </div>
  );
}
