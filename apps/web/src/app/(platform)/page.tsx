import Link from "next/link";

const quickActions = [
  {
    title: "Dashboard",
    description: "View system metrics, API status, and recent collections.",
    href: "/dashboard",
  },
  {
    title: "Chat",
    description: "Ask questions and get answers grounded in your documents.",
    href: "/chat",
  },
  {
    title: "Documents",
    description: "Upload, organize, and monitor your knowledge sources.",
    href: "/documents",
  },
];

export default function HomePage() {
  return (
    <div className="px-6 py-8 lg:px-10 lg:py-12">
      <div className="mx-auto max-w-4xl">
        <div className="mb-10">
          <p className="text-sm font-medium text-slate-500">
            Citation-grounded AI knowledge assistant
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900 lg:text-4xl">
            Welcome to KnowledgeForge
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-600">
            Turn your organization&apos;s documents into a trusted, searchable
            knowledge base. Every answer is backed by source citations so your
            team can verify and act with confidence.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          {quickActions.map((action) => (
            <Link
              key={action.href}
              href={action.href}
              className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-slate-300 hover:shadow-md"
            >
              <h2 className="text-base font-semibold text-slate-900 group-hover:text-slate-700">
                {action.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-500">
                {action.description}
              </p>
              <span className="mt-4 inline-flex items-center text-sm font-medium text-slate-900">
                Open
                <svg
                  className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
                  />
                </svg>
              </span>
            </Link>
          ))}
        </div>

        <div className="mt-10 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900">
            Platform capabilities
          </h2>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {[
              "Document ingestion and indexing",
              "Semantic search across collections",
              "Citation-grounded chat responses",
              "Enterprise access controls (coming soon)",
            ].map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-slate-600">
                <svg
                  className="mt-0.5 h-4 w-4 shrink-0 text-slate-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="m4.5 12.75 6 6 9-13.5"
                  />
                </svg>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
