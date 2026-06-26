import { ApiStatusCard } from "@/components/dashboard/ApiStatusCard";
import { RecentCollections } from "@/components/dashboard/RecentCollections";
import { StatCard } from "@/components/ui/StatCard";
import { dashboardStats, recentCollections } from "@/data/mock/dashboard";
import { getApiHealth } from "@/lib/api";

export default async function DashboardPage() {
  let health = null;
  let error: string | null = null;

  try {
    health = await getApiHealth();
  } catch (err) {
    error =
      err instanceof Error ? err.message : "Failed to connect to the API.";
  }

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

      <div className="mb-6">
        <ApiStatusCard health={health} error={error} />
      </div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {dashboardStats.map((stat) => (
          <StatCard
            key={stat.id}
            label={stat.label}
            value={stat.value}
            change={stat.change}
            trend={stat.trend}
          />
        ))}
      </div>

      <RecentCollections collections={recentCollections} />
    </div>
  );
}
