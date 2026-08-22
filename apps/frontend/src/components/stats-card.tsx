import { cn } from "@/lib/utils";
import { type LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: LucideIcon;
  iconColor?: string;
}

export function StatsCard({ title, value, change, icon: Icon, iconColor = "text-cyber-cyan" }: StatsCardProps) {
  return (
    <div className="card-glow group rounded-xl p-5 hover-glow">
      <div className="flex items-start justify-between">
        <div className="relative z-10">
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <p className="mt-2 text-3xl font-bold text-white">{typeof value === "number" ? value.toLocaleString() : value}</p>
          {change !== undefined && (
            <p className={cn("mt-1 text-xs font-medium", change >= 0 ? "text-cyber-green" : "text-cyber-red")}>
              {change >= 0 ? "+" : ""}{change}% from last hour
            </p>
          )}
        </div>
        <div className={cn("relative z-10 flex h-12 w-12 items-center justify-center rounded-lg bg-opacity-10 transition-transform duration-200 group-hover:scale-110", iconColor.replace("text-", "bg-") + "/10")}>
          <Icon className={cn("h-6 w-6", iconColor)} />
        </div>
      </div>
    </div>
  );
}
