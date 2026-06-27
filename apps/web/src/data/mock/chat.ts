type MockCitation = {
  id: string;
  title: string;
  excerpt: string;
  page?: string;
  relevance: number;
};

type MockChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  citations?: MockCitation[];
};

export const mockChatMessages: MockChatMessage[] = [
  {
    id: "msg-1",
    role: "user",
    content:
      "What is our policy for rotating API credentials in production environments?",
    timestamp: "10:24 AM",
  },
  {
    id: "msg-2",
    role: "assistant",
    content:
      "Production API credentials must be rotated every 90 days or immediately after any suspected compromise. Rotation requires approval from the security team, and new credentials must be deployed through the standard secrets management pipeline before old credentials are revoked.",
    timestamp: "10:24 AM",
    citations: [
      {
        id: "cite-1",
        title: "Security Operations Manual — Section 4.2",
        excerpt:
          "All production API keys and service credentials shall be rotated on a 90-day schedule...",
        page: "p. 47",
        relevance: 0.96,
      },
      {
        id: "cite-2",
        title: "Incident Response Playbook",
        excerpt:
          "In the event of credential exposure, initiate emergency rotation within 4 hours...",
        page: "p. 12",
        relevance: 0.88,
      },
    ],
  },
];

export const suggestedPrompts: string[] = [
  "Summarize our onboarding documentation",
  "What are the SLA targets for customer support?",
  "Find compliance requirements for data retention",
];
