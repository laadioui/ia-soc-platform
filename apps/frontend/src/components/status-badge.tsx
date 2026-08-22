import { cn } from "@/lib/utils";
import type { Status } from "@/lib/types";

const statusConfig: Record<Status, { label: string; className: string }> = {
  open: {
    label: "Open",
    className: "bg-cyber-red/10 text-cyber-red border-cyber-red/20",
  },
  investigating: {
    label: "Investigating",
    className: "bg-cyber-orange/10 text-cyber-orange border-cyber-orange/20",
  },
  pending: {
    label: "Pending",
    className: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  },
  resolved: {
    label: "Resolved",
    className: "bg-cyber-green/10 text-cyber-green border-cyber-green/20",
  },
  closed: {
    label: "Closed",
    className: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  },
};

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  );
}
