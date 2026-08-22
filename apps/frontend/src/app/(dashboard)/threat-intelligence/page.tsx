"use client";

import { useEffect, useMemo, useState } from "react";
import { Crosshair, Database, ShieldQuestion } from "lucide-react";
import { useApp } from "@/components/app-shell";
import { DataTable, type Column } from "@/components/data-table";
import { api } from "@/lib/api";
import { demoData } from "@/lib/demo-data";
import { Button3D, Card3D, Modal3D, PageHeader, SearchInput, SeverityBadge3D, useToast } from "@/components/ui";
import type { ThreatIntelEntry } from "@/lib/types";
import { timeAgo } from "@/lib/utils";

export default function ThreatIntelligencePage() {
  const toast = useToast();
  const { settings, refreshKey } = useApp();

  const [entries, setEntries] = useState<ThreatIntelEntry[]>(demoData.threatIntel);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [lookupValue, setLookupValue] = useState("");
  const [lookupBusy, setLookupBusy] = useState(false);
  const [lookupResult, setLookupResult] = useState<ThreatIntelEntry | "not-found" | null>(null);

  useEffect(() => {
    if (settings.demoMode) {
      setEntries(demoData.threatIntel);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    api
      .threatIntel({ page_size: 200 })
      .then((r) => !cancelled && setEntries(r.length ? r : demoData.threatIntel))
      .catch(() => !cancelled && setEntries(demoData.threatIntel))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [settings.demoMode, settings.apiUrl, refreshKey]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    if (!q) return entries;
    return entries.filter((t) =>
      [t.indicator_value, t.threat_type, t.source, t.description, t.indicator_type]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q))
    );
  }, [entries, search]);

  async function runLookup() {
    if (!lookupValue.trim()) {
      toast("Enter an indicator to look up", "err");
      return;
    }
    setLookupBusy(true);
    setLookupResult(null);
    try {
      const r = await api.tiLookup(lookupValue.trim());
      setLookupResult(r as ThreatIntelEntry);
      toast("Indicator found in threat feeds", "ok");
    } catch {
      await new Promise((r) => setTimeout(r, 400));
      const local = entries.find((t) => t.indicator_value === lookupValue.trim());
      if (local) {
        setLookupResult(local);
        toast("Indicator found in local dataset", "info");
      } else {
        setLookupResult("not-found");
        toast("No match in any feed", "info");
      }
    }
    setLookupBusy(false);
  }

  const columns: Column<ThreatIntelEntry>[] = [
    { key: "value", header: "Indicator", sortValue: (t) => t.indicator_value, render: (t) => (
      <span className="font-mono text-xs text-cyan-300">{t.indicator_value}</span>
    ) },
    { key: "type", header: "Type", sortValue: (t) => t.indicator_type ?? "", render: (t) => <span className="chip-3d !cursor-default !py-0.5 !text-[10px]">{t.indicator_type ?? "—"}</span> },
    { key: "threat", header: "Threat", sortValue: (t) => t.threat_type ?? "", render: (t) => <span className="text-xs font-semibold text-slate-200">{t.threat_type ?? "—"}</span> },
    { key: "severity", header: "Severity", sortValue: (t) => t.severity ?? "info", render: (t) => t.severity ? <SeverityBadge3D severity={t.severity} /> : <span className="text-xs text-slate-500">—</span> },
    { key: "confidence", header: "Confidence", sortValue: (t) => t.confidence ?? 0, render: (t) => (
      <div className="flex items-center gap-2">
        <div className="panel-inset h-1.5 w-14 overflow-hidden rounded-full">
          <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-400" style={{ width: `${t.confidence ?? 0}%` }} />
        </div>
        <span className="font-mono text-xs text-slate-400">{t.confidence ?? 0}%</span>
      </div>
    ) },
    { key: "source", header: "Feed", sortValue: (t) => t.source ?? "", render: (t) => <span className="text-xs text-slate-400">{t.source ?? "—"}</span> },
    { key: "seen", header: "First seen", sortValue: (t) => (t.created_at ? new Date(t.created_at).getTime() : 0), render: (t) => (
      <span className="text-xs text-slate-500">{t.created_at ? timeAgo(t.created_at) : "—"}</span>
    ) },
    {
      key: "actions",
      header: "",
      render: (t) => (
        <Button3D
          size="sm"
          onClick={() => { setLookupValue(t.indicator_value); runLookup(); }}
          title="Enrich this indicator"
        >
          <Crosshair className="h-3.5 w-3.5" />
        </Button3D>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Threat Intelligence"
        subtitle={`${entries.length} indicators loaded${loading ? " (refreshing…)" : ""} · lookup across all connected feeds`}
      />

      <Card3D className="p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-400">
          <ShieldQuestion className="h-4 w-4 text-amber-400" /> Indicator Lookup
        </h3>
        <div className="flex flex-wrap gap-2">
          <input
            value={lookupValue}
            onChange={(e) => setLookupValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runLookup()}
            placeholder="IP, domain or hash — try 185.220.101.34"
            className="panel-inset min-w-[240px] flex-1 px-3 py-2 font-mono text-sm text-slate-200 placeholder-slate-600 outline-none"
          />
          <Button3D variant="primary" loading={lookupBusy} onClick={runLookup}>
            <Database className="h-4 w-4" /> Lookup
          </Button3D>
        </div>
      </Card3D>

      <DataTable
        data={filtered}
        columns={columns}
        rowKey={(t) => t.id}
        pageSize={10}
        toolbar={
          <div className="flex flex-wrap items-center gap-3">
            <div className="min-w-[220px] flex-1">
              <SearchInput value={search} onChange={setSearch} placeholder="Search indicators, threats, feeds…" />
            </div>
          </div>
        }
      />

      <Modal3D open={!!lookupResult} onClose={() => setLookupResult(null)} title="Lookup Result">
        {lookupResult === "not-found" ? (
          <div className="space-y-3">
            <SeverityBadge3D severity="info" />
            <p className="text-sm text-slate-300">
              <span className="font-mono text-cyan-300">{lookupValue}</span> was not found in any connected feed. No
              known association — treat as unknown and monitor.
            </p>
          </div>
        ) : lookupResult ? (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <SeverityBadge3D severity={lookupResult.severity ?? "info"} />
              <span className="chip-3d !cursor-default">{lookupResult.indicator_type ?? "indicator"}</span>
            </div>
            <p className="font-mono text-sm text-cyan-300">{lookupResult.indicator_value}</p>
            <p className="text-sm text-slate-300">{lookupResult.description ?? lookupResult.threat_type}</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                ["Threat type", lookupResult.threat_type ?? "—"],
                ["Confidence", `${lookupResult.confidence ?? "—"}%`],
                ["Feed", lookupResult.source ?? "—"],
                ["Active", lookupResult.is_active === false ? "retired" : "active"],
              ].map(([k, v]) => (
                <div key={k} className="panel-inset px-3 py-2">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">{k}</p>
                  <p className="mt-0.5 font-mono text-xs text-slate-200">{v}</p>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </Modal3D>
    </>
  );
}
