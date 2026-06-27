"use client";

import {
  INTERNAL_ROUTES_RESTRICTED_IN_PUBLIC_MODE,
  isPublicPortfolioMode,
} from "@/lib/config";
import { RestrictedAccessScreen } from "@/components/public/RestrictedAccessScreen";
import { usePathname } from "next/navigation";

type InternalRouteGuardProps = {
  children: React.ReactNode;
};

export function InternalRouteGuard({ children }: InternalRouteGuardProps) {
  const pathname = usePathname();

  if (
    isPublicPortfolioMode() &&
    INTERNAL_ROUTES_RESTRICTED_IN_PUBLIC_MODE.some((route) =>
      route === "/"
        ? pathname === "/"
        : pathname === route || pathname.startsWith(`${route}/`),
    )
  ) {
    return <RestrictedAccessScreen />;
  }

  return children;
}
