import { Badge } from "@/components/ui/Badge";
import type { DocumentStatus, UploadFlowStatus } from "@/types/documents";
import { mapDocumentStatusForDisplay } from "@/lib/documents";

type StatusVariant = "success" | "warning" | "default" | "error" | "info";

const statusConfig: Record<
  DocumentStatus | UploadFlowStatus,
  { label: string; variant: StatusVariant }
> = {
  idle: { label: "Ready", variant: "default" },
  uploading: { label: "Uploading", variant: "info" },
  processing: { label: "Processing", variant: "warning" },
  indexed: { label: "Indexed", variant: "success" },
  failed: { label: "Failed", variant: "error" },
  uploaded: { label: "Processing", variant: "warning" },
};

type StatusBadgeProps = {
  status: DocumentStatus | UploadFlowStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const displayStatus = mapDocumentStatusForDisplay(status);
  const config = statusConfig[displayStatus];

  return <Badge variant={config.variant}>{config.label}</Badge>;
}
