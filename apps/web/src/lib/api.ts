const API_URL = process.env.NEXT_PUBLIC_API_URL;

export type HealthResponse = {
  status: string;
  service: string;
};

export async function getApiHealth(): Promise<HealthResponse> {
  if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured.");
  }

  const response = await fetch(`${API_URL}/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to connect to the KnowledgeForge API.");
  }

  return response.json() as Promise<HealthResponse>;
}
