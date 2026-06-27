import { AppShell } from "@/components/layout/AppShell";
import { InternalRouteGuard } from "@/components/public/InternalRouteGuard";

export default function PlatformLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <InternalRouteGuard>
      <AppShell>{children}</AppShell>
    </InternalRouteGuard>
  );
}
