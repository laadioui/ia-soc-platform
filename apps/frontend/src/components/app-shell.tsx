"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  Bot,
  Globe,
  LayoutDashboard,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Search,
  Settings as SettingsIcon,
  Shield,
  ShieldAlert,
  Target,
  Wifi,
  WifiOff,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { api, defaultSettings, loadSettings, type SocSettings } from "@/lib/api";

const defaultShellSettings: SocSettings = { apiUrl: "", refreshSeconds: 30, demoMode: false };
import { demoData } from "@/lib/demo-data";
import { ToastProvider, useToast } from "./ui";

/* ─────────────────────────── Global app state ─────────────────────────── */
interface AppState {
  source: "live" | "demo";
  settings: SocSettings;
  counts: { events: number; alerts: number; incidents: number; criticalAlerts: number; openIncidents: number };
  refreshKey: number;
  refresh: () => void;
  setSettings: (s: SocSettings) => void;
}

const AppCtx = createContext<AppState | null>(null);

const fallbackAppState: AppState = {
  source: "demo",
  settings: { apiUrl: "", refreshSeconds: 30, demoMode: false },
  counts: { events: 0, alerts: 0, incidents: 0, criticalAlerts: 0, openIncidents: 0 },
  refreshKey: 0,
  refresh: () => {},
  setSettings: () => {},
};

export function useApp(): AppState {
  const ctx = useContext(AppCtx);
  // Null during static prerendering (page rendered outside the shell) — degrade gracefully
  return ctx ?? fallbackAppState;
}

function AppShellInner({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const toast = useToast();
  const [collapsed, setCollapsed] = useState(false);
  const [source, setSource] = useState<"live" | "demo">("demo");
  const [settings, setSettingsState] = useState<SocSettings>(defaultShellSettings);
  const [refreshKey, setRefreshKey] = useState(0);
  const [counts, setCounts] = useState<AppState["counts"]>({
    events: demoData.events.length,
    alerts: demoData.alerts.length,
    incidents: demoData.incidents.length,
    criticalAlerts: 12,
    openIncidents: 5,
  });
  const [clock, setClock] = useState("");

  useEffect(() => {
    const loaded = loadSettings();
    defaultShellSettings.apiUrl = loaded.apiUrl;
    setSettingsState(loaded);
  }, []);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const setSettings = useCallback((s: SocSettings) => {
    setSettingsState(s);
    window.localStorage.setItem("soc-settings", JSON.stringify(s));
  }, []);

  // Live counts + backend reachability, refreshed periodically
  useEffect(() => {
    let cancelled = false;
    async function probe() {
      if (settings.demoMode) {
        if (!cancelled) {
          setSource("demo");
          setCounts({
            events: demoData.events.length,
            alerts: demoData.alerts.length,
            incidents: demoData.incidents.length,
            criticalAlerts: demoData.alerts.filter((a) => a.severity === "critical").length,
            openIncidents: demoData.incidents.filter((i) => i.status === "open" || i.status === "investigating").length,
          });
        }
        return;
      }
      try {
        const [ev, al, inc] = await Promise.all([
          api.events({ page: 1, page_size: 1 }),
          api.alerts({ page: 1, page_size: 100 }),
          api.incidents({ page: 1, page_size: 100 }),
        ]);
        if (cancelled) return;
        setSource("live");
        setCounts({
          events: ev.total,
          alerts: al.total,
          incidents: inc.total,
          criticalAlerts: al.items.filter((a) => a.severity === "critical").length,
          openIncidents: inc.items.filter((i) => i.status === "open" || i.status === "investigating").length,
        });
      } catch {
        if (!cancelled) {
          setSource("demo");
          setCounts({
            events: demoData.events.length,
            alerts: demoData.alerts.length,
            incidents: demoData.incidents.length,
            criticalAlerts: demoData.alerts.filter((a) => a.severity === "critical").length,
            openIncidents: demoData.incidents.filter((i) => i.status === "open" || i.status === "investigating").length,
          });
        }
      }
    }
    probe();
    const id = setInterval(probe, Math.max(10, settings.refreshSeconds) * 1000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [settings.demoMode, settings.refreshSeconds, settings.apiUrl, refreshKey]);

  useEffect(() => {
    const tick = () =>
      setClock(
        new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" })
      );
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const navItems = useMemo(
    () => [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, badge: 0 },
      { href: "/events", label: "Events", icon: Activity, badge: counts.events },
      { href: "/alerts", label: "Alerts", icon: AlertTriangle, badge: counts.alerts },
      { href: "/incidents", label: "Incidents", icon: ShieldAlert, badge: counts.openIncidents },
      { href: "/investigation", label: "Investigation", icon: Search, badge: 0 },
      { href: "/threat-intelligence", label: "Threat Intel", icon: Globe, badge: 0 },
      { href: "/mitre", label: "MITRE ATT&CK", icon: Target, badge: 0 },
      { href: "/ai-assistant", label: "AI Assistant", icon: Bot, badge: 0 },
      { href: "/settings", label: "Settings", icon: SettingsIcon, badge: 0 },
    ],
    [counts]
  );

  const appState = useMemo<AppState>(
    () => ({ source, settings, counts, refreshKey, refresh, setSettings }),
    [source, settings, counts, refreshKey, refresh, setSettings]
  );

  return (
    <AppCtx.Provider value={appState}>
    <div className="relative z-10 flex min-h-screen">
      {/* ─── Sidebar ─── */}
      <aside
        className={cn(
          "sticky top-0 flex h-screen shrink-0 flex-col border-r border-slate-800/80 bg-gradient-to-b from-[#0c1322]/95 to-[#080d18]/95 backdrop-blur-md transition-[width] duration-300",
          collapsed ? "w-[68px]" : "w-[232px]"
        )}
        style={{ perspective: 1200 }}
      >
        <div className="flex items-center gap-3 px-4 py-5">
          <div className="plate-3d float-3d h-10 w-10 shrink-0 border-cyan-500/40 shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_8px_18px_rgba(0,212,255,0.25)]">
            <Shield className="h-5 w-5 text-cyan-300" />
          </div>
          {!collapsed ? (
            <div className="min-w-0">
              <p className="text-3d truncate text-[15px] font-black tracking-tight text-white">SOC Platform</p>
              <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-cyan-400/80">AI Defense</p>
            </div>
          ) : null}
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-2">
          {navItems.map((item) => {
            const active = pathname === item.href || pathname?.startsWith(item.href + "/");
            return (
              <Link key={item.href} href={item.href} className={cn("nav-pill", active && "nav-pill-active")} title={item.label}>
                <item.icon className="h-[18px] w-[18px] shrink-0" />
                {!collapsed ? <span className="truncate">{item.label}</span> : null}
                {!collapsed && item.badge > 0 ? (
                  <span
                    className={cn(
                      "ml-auto rounded-full border px-1.5 py-px text-[10px] font-bold",
                      active
                        ? "border-cyan-900/40 bg-cyan-950/40 text-cyan-100"
                        : "border-slate-600/40 bg-slate-800/80 text-slate-400"
                    )}
                  >
                    {item.badge > 999 ? "999+" : item.badge}
                  </span>
                ) : null}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-slate-800/80 p-3">
          <button
            onClick={() => setCollapsed((c) => !c)}
            className={cn("nav-pill w-full justify-center", !collapsed && "justify-start")}
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <PanelLeftOpen className="h-[18px] w-[18px]" /> : <PanelLeftClose className="h-[18px] w-[18px]" />}
            {!collapsed ? <span>Collapse</span> : null}
          </button>
        </div>
      </aside>

      {/* ─── Main column ─── */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Topbar */}
        <header className="sticky top-0 z-30 border-b border-slate-800/80 bg-[#0a0f1c]/85 backdrop-blur-md">
          <div className="flex flex-wrap items-center gap-3 px-5 py-3">
            <div className="panel-inset flex items-center gap-2 px-3 py-1.5">
              {source === "live" ? (
                <>
                  <Wifi className="h-4 w-4 text-emerald-400" />
                  <span className="text-xs font-bold text-emerald-300">LIVE API</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-4 w-4 text-amber-400" />
                  <span className="text-xs font-bold text-amber-300">DEMO DATA</span>
                </>
              )}
              <span className={cn("h-2 w-2 rounded-full", source === "live" ? "bg-emerald-400 pulse-ring !shadow-none" : "bg-amber-400")} />
            </div>

            <span className="panel-inset px-3 py-1.5 font-mono text-xs tracking-widest text-cyan-300">{clock} UTC{new Date().getTimezoneOffset() <= 0 ? "+" : ""}{-new Date().getTimezoneOffset() / 60}</span>

            <div className="ml-auto flex items-center gap-2">
              <button
                onClick={() => {
                  refresh();
                  toast("Data refreshed", "info");
                }}
                className="btn-3d btn-3d-sm"
                title="Refresh all data"
              >
                <RefreshCw className="h-3.5 w-3.5" /> Refresh
              </button>
              <div className="plate-3d h-8 w-8 rounded-full border-cyan-500/30">
                <span className="text-[11px] font-black text-cyan-300">SA</span>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 px-5 py-6 lg:px-7">
          <div key={refreshKey} className="animate-rise mx-auto max-w-[1500px] space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
    </AppCtx.Provider>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <ToastProvider>
      <AppShellInner>{children}</AppShellInner>
    </ToastProvider>
  );
}

/** Convenience hook for pages: resolves live data with demo fallback on refreshKey changes. */
export function usePagedSource<T>(
  fetcher: () => Promise<{ items: T[]; total: number }>,
  fallback: { items: T[]; total: number }
) {
  const { settings, refreshKey } = useApp();
  const [state, setState] = useState({ items: fallback.items, total: fallback.total, source: "demo" as "live" | "demo", loading: true });

  useEffect(() => {
    let cancelled = false;
    if (settings.demoMode) {
      setState({ ...fallback, source: "demo", loading: false });
      return;
    }
    setState((s) => ({ ...s, loading: true }));
    fetcher()
      .then((r) => !cancelled && setState({ items: r.items, total: r.total, source: "live", loading: false }))
      .catch(() => !cancelled && setState({ ...fallback, source: "demo", loading: false }));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey, settings.demoMode, settings.apiUrl]);

  return state;
}
