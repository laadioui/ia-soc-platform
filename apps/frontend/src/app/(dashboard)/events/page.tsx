"use client";

import { useMemo, useState } from "react";
import { Ban, FileJson } from "lucide-react";
import { usePagedSource } from "@/components/app-shell";
import { DataTable, type Column } from "@/components/data-table";
import { api, runAction } from "@/lib/api";
import { demoData } from "@/lib/demo-data";
import { Button3D, Modal3D, PageHeader, SearchInput, SeverityBadge3D, useToast } from "@/components/ui";
import type { SecurityEvent, Severity } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

const SEVS: Severity[] = ["critical", "high", "medium", "low", "info"];

export default function EventsPage() {
  const toast = useToast();
  const events = usePagedSource<SecurityEvent>(
    () => api.events({ page: 1, page_size: 200 }),
    { items: demoData.events, total: demoData.events.length }
  );

  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState<Severity | "all">("all");
  const [category, setCategory] = useState<string>("all");
  const [selected, setSelected] = useState<SecurityEvent | null>(null);

  const categories = useMemo(
    () => ["all", ...new Set(events.items.map((e) => e.category).filter(Boolean))],
    [events.items]
  );

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return events.items.filter((e) => {
      if (severity !== "all" && e.severity !== severity) return false;
      if (category !== "all" && e.category !== category) return false;
      if (!q) return true;
      return [e.event_id, e.action, e.source, e.user_name, e.source_ip, e.destination_ip, e.hostname]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q));
    });
  }, [events.items, search, severity, category]);

  async function blockIp(e: SecurityEvent) {
    const msg = await runAction(
      () => api.blockIp(e.source_ip ?? "0.0.0.0", `Blocked from events console (${e.event_id})`),
      `IP ${e.source_ip} blocked at perimeter`
    );
    toast(msg, "ok");
  }

  const columns: Column<SecurityEvent>[] = [
    {
      key: "timestamp",
      header: "Timestamp",
      sortValue: (e) => new Date(e.timestamp).getTime(),
      render: (e) => <span className="font-mono text-xs text-slate-400">{formatDateTime(e.timestamp)}</span>,
    },
    { key: "event_id", header: "Event ID", sortValue: (e) => e.event_id, render: (e) => <span className="font-mono text-xs text-cyan-300">{e.event_id}</span> },
    { key: "severity", header: "Severity", sortValue: (e) => SEVS.indexOf(e.severity), render: (e) => <SeverityBadge3D severity={e.severity} /> },
    { key: "action", header: "Activity", sortValue: (e) => e.action, render: (e) => (
      <div>
        <p className="text-xs font-semibold text-slate-200">{e.action}</p>
        <p className="text-[11px] text-slate-500">{e.category} · {e.source}</p>
      </div>
    ) },
    { key: "ip", header: "Src → Dst", sortValue: (e) => e.source_ip ?? "", render: (e) => (
      <span className="font-mono text-xs text-slate-400">{e.source_ip ?? "—"} → {e.destination_ip ?? "—"}:{e.destination_port ?? ""}</span>
    ) },
    { key: "user", header: "User / Host", sortValue: (e) => e.user_name ?? "", render: (e) => (
      <span className="text-xs text-slate-300">{e.user_name ?? "—"} @ {e.hostname ?? "—"}</span>
    ) },
    {
      key: "actions",
      header: "",
      render: (e) => (
        <Button3D size="sm" variant="danger" onClick={() => blockIp(e)} title={`Block ${e.source_ip}`}>
          <Ban className="h-3.5 w-3.5" />
        </Button3D>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Event Stream"
        subtitle={`${events.total.toLocaleString()} events ingested · ${filtered.length} matching current filters`}
      />

      <DataTable
        data={filtered}
        columns={columns}
        rowKey={(e) => e.id}
        onRowClick={setSelected}
        pageSize={12}
        toolbar={
          <div className="flex flex-wrap items-center gap-3">
            <div className="min-w-[220px] flex-1">
              <SearchInput value={search} onChange={setSearch} placeholder="Search IP, user, action, host…" />
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(["all", ...SEVS] as const).map((s) => (
                <button key={s} onClick={() => setSeverity(s)} className={`chip-3d ${severity === s ? "chip-3d-active" : ""}`}>
                  {s}
                </button>
              ))}
            </div>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="panel-inset cursor-pointer px-3 py-2 text-xs font-semibold text-slate-300 outline-none"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-slate-900">
                  {c === "all" ? "All categories" : c}
                </option>
              ))}
            </select>
          </div>
        }
      />

      <Modal3D open={!!selected} onClose={() => setSelected(null)} title={`Event ${selected?.event_id ?? ""}`} wide>
        {selected ? (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <SeverityBadge3D severity={selected.severity} />
              <span className="font-mono text-xs text-slate-400">{formatDateTime(selected.timestamp)}</span>
              <span className="chip-3d !cursor-default">{selected.category}</span>
              <span className="chip-3d !cursor-default">{selected.source}</span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-3">
              {[
                ["Action", selected.action],
                ["User", selected.user_name ?? "—"],
                ["Source IP", selected.source_ip ?? "—"],
                ["Destination", `${selected.destination_ip ?? "—"}:${selected.destination_port ?? ""}`],
                ["Hostname", selected.hostname ?? "—"],
                ["Application", selected.application ?? "—"],
                ["Risk score", String(selected.risk_score ?? "—")],
                ["Source type", selected.source_type],
              ].map(([k, v]) => (
                <div key={k} className="panel-inset px-3 py-2">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">{k}</p>
                  <p className="mt-0.5 font-mono text-xs text-slate-200">{v}</p>
                </div>
              ))}
            </div>
            <div>
              <p className="mb-1.5 flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-400">
                <FileJson className="h-3.5 w-3.5" /> Raw event
              </p>
              <pre className="panel-inset max-h-52 overflow-auto p-3 font-mono text-[11px] leading-relaxed text-cyan-200/80">
                {JSON.stringify(selected.raw_event ?? selected, null, 2)}
              </pre>
            </div>
            <div className="flex justify-end gap-2">
              <Button3D variant="danger" onClick={() => { blockIp(selected); }}>
                <Ban className="h-4 w-4" /> Block source IP
              </Button3D>
            </div>
          </div>
        ) : null}
      </Modal3D>
    </>
  );
}
