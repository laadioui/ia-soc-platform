"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Activity,
  AlertTriangle,
  Shield,
  Search,
  Globe,
  Target,
  Settings,
  Bot,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/events", label: "Events", icon: Activity },
  { href: "/alerts", label: "Alerts", icon: AlertTriangle },
  { href: "/incidents", label: "Incidents", icon: Shield },
  { href: "/investigation", label: "Investigation", icon: Search },
  { href: "/threat-intelligence", label: "Threat Intel", icon: Globe },
  { href: "/mitre", label: "MITRE ATT&CK", icon: Target },
  { href: "/ai-assistant", label: "AI Assistant", icon: Bot },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "border-b border-soc-border/80 bg-[#0a0d17] px-4 py-3 transition-all duration-300",
        collapsed ? "" : ""
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-500/70 bg-slate-800/80">
            <Shield className="h-5 w-5 text-slate-100" />
          </div>
          <span className="text-2xl font-medium tracking-tight text-slate-900 dark:text-white">SOC Platform</span>
        </div>
      </div>

      <nav className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 p-0 text-[16px]">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 rounded-md px-1 py-1 transition-all duration-200",
                isActive
                  ? "text-blue-600"
                  : "text-slate-700 hover:text-slate-900"
              )}
              title={item.label}
            >
              <item.icon className={cn("h-5 w-5 shrink-0", isActive ? "text-blue-600" : "text-slate-700")} />
              <span className={cn("font-medium", isActive ? "text-blue-600" : "text-slate-700")}>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-6 space-y-3 border-t border-soc-border/80 pt-4">
        <div className="text-lg font-medium text-slate-900 dark:text-white">SOC Analyst</div>
        <div className="text-lg text-blue-600">analyst@soc.io</div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-base text-slate-700 hover:text-slate-900 transition-colors"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          <span>Collapse</span>
        </button>
      </div>
    </aside>
  );
}
