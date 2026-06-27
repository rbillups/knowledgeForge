import Link from "next/link";

export function RestrictedAccessScreen() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-6 py-12">
      <div className="max-w-lg rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">
          Internal area unavailable
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-slate-600">
          This KnowledgeForge workspace route is reserved for internal use. The
          public portfolio assistant is available separately and does not expose
          document management or multi-collection controls.
        </p>
        <p className="mt-3 text-xs text-slate-500">
          This launch boundary is not authentication. Internal routes remain in
          the codebase for development and future secured access.
        </p>
        <Link
          href="/ask"
          className="mt-6 inline-flex h-10 items-center rounded-lg bg-slate-900 px-4 text-sm font-medium text-white transition-colors hover:bg-slate-800"
        >
          Open Ask About My Work
        </Link>
      </div>
    </div>
  );
}
