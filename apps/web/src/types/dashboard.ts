export type DashboardStat = {
  id: string;
  label: string;
  value: string;
  change?: string;
  trend?: "up" | "down" | "neutral";
};

export type KnowledgeCollection = {
  id: string;
  name: string;
  documentCount: number;
  lastUpdated: string;
  owner: string;
};
