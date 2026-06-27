import { PortfolioAskInterface } from "@/components/public/PortfolioAskInterface";
import { PublicTopNav } from "@/components/public/PublicTopNav";

export default function AskPage() {
  return (
    <div className="flex h-screen flex-col bg-slate-50">
      <PublicTopNav />
      <main className="min-h-0 flex-1">
        <PortfolioAskInterface />
      </main>
    </div>
  );
}
