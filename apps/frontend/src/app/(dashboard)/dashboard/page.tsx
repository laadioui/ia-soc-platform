"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, AlertTriangle, ArrowRight, Ban, Play, Plus, ShieldAlert, Zap } from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useApp, usePagedSource } from "@/components/app-shell";
import { api, runAction } from "@/lib/api";
import { demoData } from "@/lib/demo-data";
import { Button3D, Card3D, KpiCard3D, PageHeader, SeverityBadge3D, useToast } from "@/components/ui";
import { extractIp, type Alert, type Incident, type SecurityEvent, Severity } from "@/lib/types";
import { timeAgo } from "@/lib/utils";

const SEV_COLORS: Record<Severity, string> = {
  critical: "#f43f5e",
  high: "#fb923c",
  medium: "#fbbf24",
  low: "#38bdf8",
  info: "#64748b",
};

export default function DashboardPage() {
  const router = useRouter();
  const toast = useToast();
  const { counts, refresh } = useApp();

  const events = usePagedSource<SecurityEvent>(
    () => api.events({ page: 1, page_size: 200 }),
    { items: demoData.events, total: demoData.events.length }
  );
  const alerts = usePagedSource<Alert>(
    () => api.alerts({ page: 1, page_size: 200 }),
    { items: demoData.alerts, total: demoData.alerts.length }
  );
  const incidents = usePagedSource<Incident>(
    () => api.incidents({ page: 1, page_size: 200 }),
    { items: demoData.incidents, total: demoData.incidents.length }
  );

  const [feedPaused, setFeedPaused] = useState(false);
  const [creatingIncident, setCreatingIncident] = useState(false);

  // Live incident creation form state
  const [newTitle, setNewTitle] = useState("");
  const [newSeverity, setNewSeverity] = useState<Severity>("high");
  const [formOpen, setFormOpen] = useState(false);

  const byHour = useMemo(() => {
    const buckets = new Map<string, number>();
    const now = new Date();
    for (let h = 11; h >= 0; h--) {
      const d = new Date(now.getTime() - h * 3600_000);
      buckets.set(`${String(d.getHours()).padStart(2, "0")}:00`, 0);
    }
    for (const e of events.items) {
      const key = `${String(new Date(e.timestamp).getHours()).padStart(2, "0")}:00`;
      if (buckets.has(key)) buckets.set(key, (buckets.get(key) ?? 0) + 1);
    }
    return [...buckets.entries()].map(([hour, count]) => ({ hour, count }));
  }, [events.items]);

  const bySeverity = useMemo(() => {
    const order: Severity[] = ["critical", "high", "medium", "low", "info"];
    return order
      .map((sev) => ({
        name: sev,
        value: alerts.items.filter((a) => a.severity === sev).length,
        color: SEV_COLORS[sev],
      }))
      .filter((d) => d.value > 0);
  }, [alerts.items]);

  const recentAlerts = useMemo(
    () =>
      [...alerts.items]
        .sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at))
        .slice(0, feedPaused ? 0 : 6),
    [alerts.items, feedPaused]
  );

  // Demo feed simulation
  const [demoTick, setDemoTick] = useState(0);
  useEffect(() => {
    if (feedPaused) return;
    const id = setInterval(() => setDemoTick((t) => t + 1), 4000);
    return () => clearInterval(id);
  }, [feedPaused]);

  async function handleBlockIp(alert: Alert) {
    const ip = alert.source_ip ?? extractIp(alert.description);
    if (!ip) {
      toast("No source IP recorded on this alert", "err");
      return;
    }
    const msg = await runAction(
      () => api.blockIp(ip, `Blocked for alert ${alert.alert_id}`),
      `IP ${ip} blocked (firewall rule queued)`,
      false
    );
    toast(msg, "ok");
  }

  async function handleCreateIncident() {
    if (!newTitle.trim()) {
      toast("Give the incident a title first", "err");
      return;
    }
    setCreatingIncident(true);
    const msg = await runAction(
      () => api.createIncident({ title: newTitle, severity: newSeverity, description: "Created from SOC dashboard" }),
      `Incident "${newTitle}" created`,
      false
    );
    setCreatingIncident(false);
    setFormOpen(false);
    setNewTitle("");
    toast(msg, "ok");
    refresh();
  }

  return (
    <>
      <PageHeader
        title="Security Operations Center"
        subtitle={`Real-time posture · ${counts.events.toLocaleString()} events · ${counts.alerts.toLocaleString()} alerts · ${counts.openIncidents} open incidents`}
        actions={
          <>
            <Button3D variant="primary" onClick={() => setFormOpen(true)}>
              <Plus className="h-4 w-4" /> New Incident
            </Button3D>
            <Button3D onClick={() => setFeedPaused((p) => !p)}>
              {feedPaused ? <Play className="h-4 w-4" /> : null}
              {feedPaused ? "Resume Feed" : "Pause Feed"}
            </Button3D>
          </>
        }
      />

      {/* KPI row */}
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <KpiCard3D
          label="Events (24h)"
          value={events.total}
          tone="cyan"
          icon={<Activity className="h-6 w-6" />}
          hint="ingested security events"
          onClick={() => router.push("/events")}
        />
        <KpiCard3D
          label="Critical Alerts"
          value={counts.criticalAlerts}
          tone="red"
          icon={<AlertTriangle className="h-6 w-6" />}
          hint="requiring triage"
          onClick={() => router.push("/alerts")}
        />
        <KpiCard3D
          label="Open Incidents"
          value={counts.openIncidents}
          tone="orange"
          icon={<ShieldAlert className="h-6 w-6" />}
          hint="active investigations"
          onClick={() => router.push("/incidents")}
        />
        <KpiCard3D
          label="Threat Actors Seen"
          value={new Set(events.items.map((e) => e.source_ip).filter(Boolean)).size}
          tone="violet"
          icon={<Zap className="h-6 w-6" />}
          hint="distinct source IPs"
        />
      </div>

      {/* Charts row */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card3D className="p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Event Flow (12h)</h3>
            <span className="chip-3d chip-3d-active">Hourly</span>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={byHour}>
                <defs>
                  <linearGradient id="evgrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00d4ff" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="#00d4ff" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="hour" stroke="#475569" fontSize={11} />
                <YAxis stroke="#475569" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #334155",
                    borderRadius: 10,
                    boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
                  }}
                />
                <Area type="monotone" dataKey="count" stroke="#00d4ff" strokeWidth={2} fill="url(#evgrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card3D>

        <Card3D className="p-5">
          <h3 className="mb-4 text-sm font-bold uppercase tracking-widest text-slate-400">Alerts by Severity</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={bySeverity}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={52}
                  outerRadius={80}
                  paddingAngle={4}
                  stroke="#0b1120"
                  strokeWidth={3}
                >
                  {bySeverity.map((d) => (
                    <Cell key={d.name} fill={d.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #334155",
                    borderRadius: 10,
                    boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex flex-wrap justify-center gap-2">
            {bySeverity.map((d) => (
              <span key={d.name} className="chip-3d !cursor-default !px-2.5 !py-0.5 !text-[10px]">
                <span className="h-2 w-2 rounded-full" style={{ background: d.color, boxShadow: `0 0 8px ${d.color}` }} />
                {d.name} · {d.value}
              </span>
            ))}
          </div>
        </Card3D>
      </div>

      {/* Live feed + recent incidents */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card3D className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-400">
              <span className={`${feedPaused ? "" : "pulse-ring"} h-2.5 w-2.5 rounded-full bg-rose-500`} />
              Live Alert Feed
            </h3>
            <Button3D size="sm" onClick={() => router.push("/alerts")}>
              All alerts <ArrowRight className="h-3.5 w-3.5" />
            </Button3D>
          </div>
          <div className="space-y-2.5" key={demoTick}>
            {recentAlerts.map((a) => (
              <div
                key={a.id}
                className="panel-inset animate-pop flex items-center gap-3 px-3.5 py-2.5"
              >
                <SeverityBadge3D severity={a.severity} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-slate-200">{a.title ?? a.rule_id}</p>
                  <p className="truncate text-xs text-slate-500">
                    {a.alert_id} · {extractIp(a.description) ?? a.source_ip ?? "—"} · {a.hostname ?? a.source ?? "—"}
                  </p>
                </div>
                <span className="shrink-0 text-xs text-slate-500">{timeAgo(a.created_at)}</span>
                <Button3D size="sm" variant="danger" onClick={() => handleBlockIp(a)} title={`Block ${extractIp(a.description) ?? a.source_ip ?? "IP"}`}>
                  <Ban className="h-3.5 w-3.5" />
                </Button3D>
              </div>
            ))}
            {feedPaused ? <p className="py-8 text-center text-sm text-slate-500">Feed paused — press Resume.</p> : null}
          </div>
        </Card3D>

        <Card3D className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Recent Incidents</h3>
            <Button3D size="sm" onClick={() => router.push("/incidents")}>
              Open console <ArrowRight className="h-3.5 w-3.5" />
            </Button3D>
          </div>
          <div className="space-y-2.5">
            {[...incidents.items]
              .sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at))
              .slice(0, 5)
              .map((i) => (
                <button
                  key={i.id}
                  onClick={() => router.push(`/incidents`)}
                  className="panel-inset flex w-full items-center gap-3 px-3.5 py-2.5 text-left transition-all hover:translate-x-1 hover:border-cyan-500/40"
                >
                  <SeverityBadge3D severity={i.severity} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-slate-200">{i.title}</p>
                    <p className="truncate text-xs text-slate-500">
                      {i.incident_id} · {i.status}
                    </p>
                  </div>
                  <span className="shrink-0 text-xs text-slate-500">{timeAgo(i.created_at)}</span>
                </button>
              ))}
          </div>
        </Card3D>
      </div>

      {/* New incident modal */}
      {formOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" onClick={() => setFormOpen(false)}>
          <div className="card-3d animate-pop w-full max-w-md p-5" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-3d mb-4 text-lg font-bold text-white">Declare Incident</h3>
            <label className="mb-1 block text-xs font-bold uppercase tracking-widest text-slate-400">Title</label>
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Suspicious lateral movement"
              className="panel-inset mb-4 w-full px-3 py-2 text-sm text-slate-200 placeholder-slate-600 outline-none"
            />
            <label className="mb-1 block text-xs font-bold uppercase tracking-widest text-slate-400">Severity</label>
            <div className="mb-5 flex flex-wrap gap-2">
              {(["critical", "high", "medium", "low"] as Severity[]).map((s) => (
                <button
                  key={s}
                  onClick={() => setNewSeverity(s)}
                  className={`chip-3d ${newSeverity === s ? "chip-3d-active" : ""}`}
                >
                  {s}
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-2">
              <Button3D onClick={() => setFormOpen(false)}>Cancel</Button3D>
              <Button3D variant="primary" loading={creatingIncident} onClick={handleCreateIncident}>
                Create
              </Button3D>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
