import Link from "next/link";

import { PORTFOLIO_SITE_URL } from "@/lib/config";

export function HowItWorksSection() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-slate-900">How it works</h2>
      <ul className="mt-4 space-y-3 text-sm leading-relaxed text-slate-600">
        <li>
          Answers are generated from indexed public portfolio documents only.
        </li>
        <li>
          Source excerpts are shown beneath answers so you can review what
          supported the response.
        </li>
        <li>
          The assistant does not provide private personal information or
          proprietary employer details.
        </li>
      </ul>
      <p className="mt-4 text-sm text-slate-500">
        Learn more on{" "}
        <Link
          href={PORTFOLIO_SITE_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-slate-700 underline decoration-slate-300 underline-offset-2"
        >
          rkbillups.com
        </Link>
        .
      </p>
    </section>
  );
}
