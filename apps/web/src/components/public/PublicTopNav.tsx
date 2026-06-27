import Link from "next/link";

import { PORTFOLIO_SITE_URL } from "@/lib/config";

export function PublicTopNav() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6">
      <div>
        <p className="text-sm font-semibold text-slate-900">Ask About My Work</p>
        <p className="text-xs text-slate-500">Public portfolio assistant</p>
      </div>

      <Link
        href={PORTFOLIO_SITE_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex h-9 items-center rounded-lg border border-slate-200 px-4 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
      >
        Visit rkbillups.com
      </Link>
    </header>
  );
}
