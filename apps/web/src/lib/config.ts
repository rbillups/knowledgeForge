export function isPublicPortfolioMode(): boolean {
  return process.env.NEXT_PUBLIC_PUBLIC_PORTFOLIO_MODE === "true";
}

export const PORTFOLIO_SITE_URL = "https://rkbillups.com";

export const INTERNAL_ROUTES_RESTRICTED_IN_PUBLIC_MODE = [
  "/",
  "/dashboard",
  "/documents",
  "/chat",
] as const;
