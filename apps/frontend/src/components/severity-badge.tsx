import { cn } from "@/lib/utils";
import type { Severity } from "@/lib/types";

const severityConfig: Record<Severity, { label: string; className: string }> = {
  critical: {
    label: "Critical",
    className: "bg-cyber-red/10 text-cyber-red border-cyber-red/20",
  },
  high: {
    label: "High",
    className: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  },
  medium: {
    label: "Medium",
    className: "bg-cyber-orange/10 text-cyber-orange border-cyber-orange/20",
  },
  low: {
    label: "Low",
    className: "bg-cyber-blue/10 text-cyber-blue border-cyber-blue/20",
  },
  info: {
    label: "Info",
    className: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  },
};

interface SeverityBadgeProps {
  severity: Severity;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const config = severityConfig[severity];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className
      )}
    >
      <span className={cn("mr-1.5 h-1.5 w-1.5 rounded-full", {
        "bg-cyber-red": severity === "critical",
        "bg-orange-400": severity === "high",
        "bg-cyber-orange": severity === "medium",
        "bg-cyber-blue": severity === "low",
        "bg-slate-400": severity === "info",
      })} />
      {config.label}
    </span>
  );
}
