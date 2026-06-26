import type { ChatMessage } from "@/types/chat";

export const mockChatMessages: ChatMessage[] = [
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
  {
    id: "msg-3",
    role: "user",
    content: "Who needs to approve the rotation?",
    timestamp: "10:25 AM",
  },
  {
    id: "msg-4",
    role: "assistant",
    content:
      "Approval is required from a member of the Security Engineering team. For emergency rotations triggered by an incident, the on-call security lead can approve immediately and document the exception within 24 hours.",
    timestamp: "10:25 AM",
    citations: [
      {
        id: "cite-3",
        title: "Security Operations Manual — Section 4.2.1",
        excerpt:
          "Routine rotations require Security Engineering approval. Emergency rotations may be authorized by the on-call security lead...",
        page: "p. 48",
        relevance: 0.94,
      },
    ],
  },
];

export const suggestedPrompts: string[] = [
  "Summarize our onboarding documentation",
  "What are the SLA targets for customer support?",
  "Find compliance requirements for data retention",
];
