type StatCardProps = {
  label: string;
  value: string;
  change?: string;
  trend?: "up" | "down" | "neutral";
};

export function StatCard({ label, value, change, trend = "neutral" }: StatCardProps) {
  const trendColor =
    trend === "up"
      ? "text-emerald-600"
      : trend === "down"
        ? "text-red-600"
        : "text-slate-500";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
        {value}
      </p>
      {change && (
        <p className={`mt-2 text-sm ${trendColor}`}>{change}</p>
      )}
    </div>
  );
}
