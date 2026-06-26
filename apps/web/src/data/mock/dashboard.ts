import type { DashboardStat, KnowledgeCollection } from "@/types/dashboard";

export const dashboardStats: DashboardStat[] = [
  {
    id: "documents-indexed",
    label: "Documents indexed",
    value: "1,284",
    change: "+42 this week",
    trend: "up",
  },
  {
    id: "questions-answered",
    label: "Questions answered",
    value: "3,917",
    change: "+186 this week",
    trend: "up",
  },
  {
    id: "helpful-response-rate",
    label: "Helpful response rate",
    value: "94.2%",
    change: "+1.3% vs last month",
    trend: "up",
  },
];

export const recentCollections: KnowledgeCollection[] = [
  {
    id: "col-1",
    name: "Engineering Handbook",
    documentCount: 312,
    lastUpdated: "2 hours ago",
    owner: "Platform Team",
  },
  {
    id: "col-2",
    name: "Customer Support Playbooks",
    documentCount: 148,
    lastUpdated: "Yesterday",
    owner: "Support Ops",
  },
  {
    id: "col-3",
    name: "Security & Compliance",
    documentCount: 89,
    lastUpdated: "3 days ago",
    owner: "GRC Team",
  },
  {
    id: "col-4",
    name: "Product Launch Materials",
    documentCount: 56,
    lastUpdated: "5 days ago",
    owner: "Product Marketing",
  },
];
