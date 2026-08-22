"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, Eye, Play, Plus, ShieldCheck, Sparkles } from "lucide-react";
import { useApp, usePagedSource } from "@/components/app-shell";
import { DataTable, type Column } from "@/components/data-table";
import { api, runAction } from "@/lib/api";
import { demoData } from "@/lib/demo-data";
import { Button3D, Modal3D, PageHeader, SearchInput, SeverityBadge3D, StatusBadge3D, useToast } from "@/components/ui";
import type { AISummaryResult, Incident, IncidentStatus, Severity } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

const SEVS: Severity[] = ["critical", "high", "medium", "low", "info"];
const STATUSES: IncidentStatus[] = ["open", "investigating", "contained", "resolved", "closed"];

export default function IncidentsPage() {
  const toast = useToast();
  const { refresh, settings } = useApp();
  const incidents = usePagedSource<Incident>(
    () => api.incidents({ page: 1, page_size: 200 }),
    { items: demoData.incidents, total: demoData.incidents.length }
  );

  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState<Severity | "all">("all");
  const [status, setStatus] = useState<IncidentStatus | "all">("all");
  const [selected, setSelected] = useState<Incident | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newSeverity, setNewSeverity] = useState<Severity>("high");
  const [creating, setCreating] = useState(false);

  const [overrides, setOverrides] = useState<Record<string, IncidentStatus>>({});
  const items = useMemo(
    () => incidents.items.map((i) => (overrides[i.id] ? { ...i, status: overrides[i.id] } : i)),
    [incidents.items, overrides]
  );

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return items.filter((i) => {
      if (severity !== "all" && i.severity !== severity) return false;
      if (status !== "all" && i.status !== status) return false;
      if (!q) return true;
      return [i.incident_id, i.title, i.source, i.description].filter(Boolean).some((v) =>
        String(v).toLowerCase().includes(q)
      );
    });
  }, [items, search, severity, status]);

  async function changeStatus(i: Incident, next: IncidentStatus) {
    setBusyId(i.id);
    const msg = await runAction(
      () => api.updateIncident(i.id, { status: next }),
      `Incident ${i.incident_id} → ${next}`,
      settings.demoMode || false,
      i.id.startsWith("demo-")
    );
    setBusyId(null);
    setOverrides((o) => ({ ...o, [i.id]: next }));
    toast(msg, "ok");
  }

  async function handleCreate() {
    if (!newTitle.trim()) {
      toast("Give the incident a title", "err");
      return;
    }
    setCreating(true);
    const msg = await runAction(
      () => api.createIncident({ title: newTitle, severity: newSeverity, description: "Declared from incidents console" }),
      `Incident "${newTitle}" created`
    );
    setCreating(false);
    setCreateOpen(false);
    setNewTitle("");
    toast(msg, "ok");
    refresh();
  }

  // AI summary inside detail modal
  const [aiBusy, setAiBusy] = useState(false);
  const [aiSummary, setAiSummary] = useState<AISummaryResult | null>(null);

  async function askAI(i: Incident) {
    setAiBusy(true);
    try {
      const r = await api.aiSummarize(i.id);
      setAiSummary(r);
    } catch {
      setAiSummary({
        summary: `Simulated analysis of ${i.title}: the correlation engine linked multiple detections into this incident. The kill chain suggests initial access followed by discovery and staging on affected hosts.`,
        key_findings: [
          "Multiple failed authentications precede privileged activity",
          "Outbound volume on the affected host is 4.7x baseline",
          "New scheduled task created minutes before staging",
        ],
        risk_assessment: "High — containment recommended within the hour.",
        recommended_actions: ["Isolate affected hosts", "Rotate compromised credentials", "Hunt for lateral movement (T1021)"],
        mitre_techniques: ["T1110", "T1048", "T1074"],
        confidence: 0.83,
      });
    }
    setAiBusy(false);
  }

  const columns: Column<Incident>[] = [
    { key: "id", header: "Incident", sortValue: (i) => i.incident_id, render: (i) => <span className="font-mono text-xs text-cyan-300">{i.incident_id}</span> },
    { key: "title", header: "Title", sortValue: (i) => i.title, render: (i) => <span className="text-sm font-semibold text-slate-200">{i.title}</span> },
    { key: "severity", header: "Severity", sortValue: (i) => SEVS.indexOf(i.severity), render: (i) => <SeverityBadge3D severity={i.severity} /> },
    { key: "status", header: "Status", sortValue: (i) => i.status, render: (i) => <StatusBadge3D status={i.status} /> },
    { key: "risk", header: "Risk", sortValue: (i) => i.risk_score ?? 0, render: (i) => (
      <div className="flex items-center gap-2">
        <div className="panel-inset h-1.5 w-14 overflow-hidden rounded-full">
          <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-rose-500" style={{ width: `${i.risk_score ?? 0}%` }} />
        </div>
        <span className="font-mono text-xs text-slate-400">{i.risk_score ?? 0}</span>
      </div>
    ) },
    { key: "created", header: "Opened", sortValue: (i) => new Date(i.created_at).getTime(), render: (i) => (
      <span className="font-mono text-xs text-slate-400">{formatDateTime(i.created_at)}</span>
    ) },
    {
      key: "actions",
      header: "Response",
      render: (i) => (
        <div className="flex items-center gap-1.5">
          <Button3D size="sm" loading={busyId === i.id} onClick={() => changeStatus(i, "investigating")} title="Start investigating">
            <Play className="h-3.5 w-3.5" />
          </Button3D>
          <Button3D size="sm" variant="success" onClick={() => changeStatus(i, "contained")} title="Mark contained">
            <ShieldCheck className="h-3.5 w-3.5" />
          </Button3D>
          <Button3D size="sm" variant="primary" onClick={() => changeStatus(i, "resolved")} title="Resolve">
            <CheckCircle2 className="h-3.5 w-3.5" />
          </Button3D>
          <Button3D size="sm" onClick={() => { setSelected(i); setAiSummary(null); }} title="Details & AI">
            <Eye className="h-3.5 w-3.5" />
          </Button3D>
        </div>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Incident Response"
        subtitle={`${incidents.total.toLocaleString()} incidents · ${filtered.length} matching filters`}
        actions={
          <Button3D variant="primary" onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" /> Declare Incident
          </Button3D>
        }
      />

      <DataTable
        data={filtered}
        columns={columns}
        rowKey={(i) => i.id}
        pageSize={10}
        toolbar={
          <div className="flex flex-wrap items-center gap-3">
            <div className="min-w-[220px] flex-1">
              <SearchInput value={search} onChange={setSearch} placeholder="Search incident, title, source…" />
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

      {/* Detail modal with AI summary */}
      <Modal3D open={!!selected} onClose={() => setSelected(null)} title={selected ? `${selected.incident_id} — ${selected.title}` : ""} wide>
        {selected ? (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <SeverityBadge3D severity={selected.severity} />
              <StatusBadge3D status={selected.status} />
              <span className="font-mono text-xs text-slate-400">opened {formatDateTime(selected.created_at)}</span>
            </div>
            <p className="text-sm text-slate-300">{selected.description ?? "No description recorded."}</p>

            <Button3D variant="primary" loading={aiBusy} onClick={() => askAI(selected)}>
              <Sparkles className="h-4 w-4" /> AI Incident Summary
            </Button3D>

            {aiSummary ? (
              <div className="panel-inset animate-pop space-y-3 p-4 text-sm">
                <p className="text-slate-200">{aiSummary.summary}</p>
                <div>
                  <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-slate-500">Key findings</p>
                  <ul className="list-disc space-y-1 pl-5 text-slate-300">
                    {aiSummary.key_findings.map((f) => <li key={f}>{f}</li>)}
                  </ul>
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <div>
                    <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-slate-500">Risk assessment</p>
                    <p className="text-amber-200">{aiSummary.risk_assessment}</p>
                  </div>
                  <div>
                    <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-slate-500">MITRE techniques</p>
                    <div className="flex flex-wrap gap-1.5">
                      {aiSummary.mitre_techniques.map((t) => <span key={t} className="chip-3d !cursor-default !py-0.5 !text-[10px]">{t}</span>)}
                    </div>
                  </div>
                </div>
                <div>
                  <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-slate-500">Recommended actions</p>
                  <ul className="list-disc space-y-1 pl-5 text-emerald-300">
                    {aiSummary.recommended_actions.map((a) => <li key={a}>{a}</li>)}
                  </ul>
                </div>
                <p className="text-xs text-slate-500">AI confidence: {(aiSummary.confidence * 100).toFixed(0)}%</p>
              </div>
            ) : null}

            <div className="flex flex-wrap justify-end gap-2">
              <Button3D onClick={() => changeStatus(selected, "contained")}>Contain</Button3D>
              <Button3D variant="success" onClick={() => changeStatus(selected, "resolved")}>Resolve</Button3D>
              <Button3D onClick={() => changeStatus(selected, "closed")}>Close</Button3D>
            </div>
          </div>
        ) : null}
      </Modal3D>

      {/* Create modal */}
      {createOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" onClick={() => setCreateOpen(false)}>
          <div className="card-3d animate-pop w-full max-w-md p-5" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-3d mb-4 text-lg font-bold text-white">Declare Incident</h3>
            <label className="mb-1 block text-xs font-bold uppercase tracking-widest text-slate-400">Title</label>
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Ransomware staging detected"
              className="panel-inset mb-4 w-full px-3 py-2 text-sm text-slate-200 placeholder-slate-600 outline-none"
            />
            <label className="mb-1 block text-xs font-bold uppercase tracking-widest text-slate-400">Severity</label>
            <div className="mb-5 flex flex-wrap gap-2">
              {(["critical", "high", "medium", "low"] as Severity[]).map((s) => (
                <button key={s} onClick={() => setNewSeverity(s)} className={`chip-3d ${newSeverity === s ? "chip-3d-active" : ""}`}>
                  {s}
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-2">
              <Button3D onClick={() => setCreateOpen(false)}>Cancel</Button3D>
              <Button3D variant="primary" loading={creating} onClick={handleCreate}>Create</Button3D>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
