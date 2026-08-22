"use client";

import { useMemo, useState } from "react";
import { Ban, Check, Eye, SearchCode } from "lucide-react";
import { useApp, usePagedSource } from "@/components/app-shell";
import { DataTable, type Column } from "@/components/data-table";
import { api, runAction } from "@/lib/api";
import { demoData } from "@/lib/demo-data";
import { Button3D, Modal3D, PageHeader, SearchInput, SeverityBadge3D, StatusBadge3D, useToast } from "@/components/ui";
import { extractIp, type Alert, type AlertStatus, type Severity } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

const SEVS: Severity[] = ["critical", "high", "medium", "low", "info"];
const STATUSES: AlertStatus[] = ["new", "acknowledged", "investigating", "resolved", "closed"];

export default function AlertsPage() {
  const toast = useToast();
  const { refresh, settings } = useApp();
  const alerts = usePagedSource<Alert>(
    () => api.alerts({ page: 1, page_size: 200 }),
    { items: demoData.alerts, total: demoData.alerts.length }
  );

  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState<Severity | "all">("all");
  const [status, setStatus] = useState<AlertStatus | "all">("all");
  const [selected, setSelected] = useState<Alert | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  // Local optimistic overlay so status changes reflect instantly even in demo mode
  const [overrides, setOverrides] = useState<Record<string, AlertStatus>>({});
  const items = useMemo(
    () => alerts.items.map((a) => (overrides[a.id] ? { ...a, status: overrides[a.id] } : a)),
    [alerts.items, overrides]
  );

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return items.filter((a) => {
      if (severity !== "all" && a.severity !== severity) return false;
      if (status !== "all" && a.status !== status) return false;
      if (!q) return true;
      return [a.alert_id, a.title, a.rule_id, a.source_ip, a.hostname, a.user_name, a.mitre_technique]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q));
    });
  }, [items, search, severity, status]);

  async function changeStatus(a: Alert, next: AlertStatus) {
    setBusyId(a.id);
    const msg = await runAction(
      () => api.updateAlert(a.id, { status: next }),
      `Alert ${a.alert_id} → ${next}`,
      settings.demoMode || false,
      a.id.startsWith("demo-")
    );
    setBusyId(null);
    setOverrides((o) => ({ ...o, [a.id]: next }));
    toast(msg, "ok");
  }

  function alertIp(a: Alert): string | null {
    return a.source_ip ?? extractIp(a.description);
  }

  async function blockIp(a: Alert) {
    const target = alertIp(a);
    if (!target) {
      toast("No source IP recorded on this alert", "err");
      return;
    }
    const msg = await runAction(
      () => api.blockIp(target, `Blocked for ${a.alert_id}`),
      `IP ${target} blocked at perimeter`
    );
    toast(msg, "ok");
  }

  const columns: Column<Alert>[] = [
    { key: "alert_id", header: "Alert", sortValue: (a) => a.alert_id, render: (a) => <span className="font-mono text-xs text-cyan-300">{a.alert_id}</span> },
    { key: "title", header: "Detection", sortValue: (a) => a.title ?? "", render: (a) => (
      <div>
        <p className="text-sm font-semibold text-slate-200">{a.title ?? a.rule_id}</p>
        <p className="text-[11px] text-slate-500">{a.rule_id} · {a.source ?? "—"} · {a.event_count ?? 1} events</p>
      </div>
    ) },
    { key: "severity", header: "Severity", sortValue: (a) => SEVS.indexOf(a.severity), render: (a) => <SeverityBadge3D severity={a.severity} /> },
    { key: "status", header: "Status", sortValue: (a) => a.status, render: (a) => <StatusBadge3D status={a.status} /> },
    { key: "created", header: "Detected", sortValue: (a) => new Date(a.last_seen ?? a.created_at).getTime(), render: (a) => (
      <span className="font-mono text-xs text-slate-400">{formatDateTime(a.last_seen ?? a.created_at)}</span>
    ) },
    {
      key: "actions",
      header: "Response",
      render: (a) => (
        <div className="flex items-center gap-1.5">
          <Button3D size="sm" variant="success" loading={busyId === a.id} onClick={() => changeStatus(a, "acknowledged")} title="Acknowledge">
            <Check className="h-3.5 w-3.5" />
          </Button3D>
          <Button3D size="sm" onClick={() => changeStatus(a, "investigating")} title="Mark investigating">
            <SearchCode className="h-3.5 w-3.5" />
          </Button3D>
          <Button3D size="sm" variant="danger" onClick={() => blockIp(a)} title={`Block ${alertIp(a) ?? "IP"}`}>
            <Ban className="h-3.5 w-3.5" />
          </Button3D>
          <Button3D size="sm" onClick={() => setSelected(a)} title="Details">
            <Eye className="h-3.5 w-3.5" />
          </Button3D>
        </div>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Alert Console"
        subtitle={`${alerts.total.toLocaleString()} alerts · ${filtered.length} matching filters · acknowledge, investigate, block`}
      />

      <DataTable
        data={filtered}
        columns={columns}
        rowKey={(a) => a.id}
        onRowClick={setSelected}
        pageSize={12}
        toolbar={
          <div className="flex flex-wrap items-center gap-3">
            <div className="min-w-[220px] flex-1">
              <SearchInput value={search} onChange={setSearch} placeholder="Search alert, rule, IP, technique…" />
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(["all", ...SEVS] as const).map((s) => (
                <button key={s} onClick={() => setSeverity(s)} className={`chip-3d ${severity === s ? "chip-3d-active" : ""}`}>
                  {s}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(["all", ...STATUSES] as const).map((s) => (
                <button key={s} onClick={() => setStatus(s)} className={`chip-3d ${status === s ? "chip-3d-active" : ""}`}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        }
      />

      <Modal3D open={!!selected} onClose={() => setSelected(null)} title={`Alert ${selected?.alert_id ?? ""}`}>
        {selected ? (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <SeverityBadge3D severity={selected.severity} />
              <StatusBadge3D status={selected.status} />
              <span className="font-mono text-xs text-slate-400">{formatDateTime(selected.created_at)}</span>
            </div>
            <p className="text-sm text-slate-300">{selected.description ?? "No description recorded."}</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                ["Rule", `${selected.rule_id ?? "—"}${selected.rule_name && selected.rule_name !== selected.title ? " · " + selected.rule_name : ""}`],
                ["MITRE", `${selected.mitre_technique ?? "—"} (${selected.mitre_tactic ?? "—"})`],
                ["Source IP", alertIp(selected) ?? "—"],
                ["Feed source", selected.source ?? "—"],
                ["Event count", String(selected.event_count ?? 1)],
                ["Risk score", String(selected.risk_score ?? "—")],
              ].map(([k, v]) => (
                <div key={k} className="panel-inset px-3 py-2">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">{k}</p>
                  <p className="mt-0.5 font-mono text-xs text-slate-200">{v}</p>
                </div>
              ))}
            </div>
            <div className="flex flex-wrap justify-end gap-2">
              <Button3D variant="success" onClick={() => changeStatus(selected, "resolved")}>Resolve</Button3D>
              <Button3D onClick={() => changeStatus(selected, "closed")}>Close</Button3D>
              <Button3D variant="danger" onClick={() => blockIp(selected)}>Block IP</Button3D>
            </div>
          </div>
        ) : null}
      </Modal3D>
    </>
  );
}
