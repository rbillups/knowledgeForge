import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ask About My Work | KnowledgeForge",
  description:
    "Ask questions about Key'Shawn Billups' public portfolio projects, skills, and experience.",
};

export default function AskLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
