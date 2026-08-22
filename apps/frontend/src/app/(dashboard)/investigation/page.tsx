"use client";

import { useMemo, useState } from "react";
import { Ban, Search, Sparkles, Terminal } from "lucide-react";
import { usePagedSource } from "@/components/app-shell";
import { api, runAction } from "@/lib/api";
import { demoAIReply, demoData } from "@/lib/demo-data";
import { Button3D, Card3D, PageHeader, SearchInput, SeverityBadge3D, useToast } from "@/components/ui";
import type { SecurityEvent } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

export default function InvestigationPage() {
  const toast = useToast();
  const events = usePagedSource<SecurityEvent>(
    () => api.events({ page: 1, page_size: 200 }),
    { items: demoData.events, total: demoData.events.length }
  );

  const [query, setQuery] = useState("");
  const [aiQuery, setAiQuery] = useState("");
  const [aiBusy, setAiBusy] = useState(false);
  const [aiReply, setAiReply] = useState<string | null>(null);
  const [history, setHistory] = useState<string[]>([]);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return events.items.filter((e) =>
      [e.event_id, e.action, e.source, e.user_name, e.source_ip, e.destination_ip, e.hostname, e.category, e.application]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q))
    );
  }, [events.items, query]);

  function runQuery(q: string) {
    setQuery(q);
    setHistory((h) => [q, ...h.filter((x) => x !== q)].slice(0, 6));
  }

  async function askAI() {
    if (!aiQuery.trim()) return;
    setAiBusy(true);
    setAiReply(null);
    try {
      const r = await api.aiAnalyze(aiQuery);
      setAiReply(r.response);
    } catch {
      await new Promise((r) => setTimeout(r, 450));
      setAiReply(demoAIReply(aiQuery));
    }
    setAiBusy(false);
  }

  async function blockIp(ip: string) {
    const msg = await runAction(() => api.blockIp(ip, "Blocked from investigation console"), `IP ${ip} blocked at perimeter`);
    toast(msg, "ok");
  }

  return (
    <>
      <PageHeader
        title="Investigation Console"
        subtitle="Query the event lake and ask the AI analyst — every control below is live"
      />

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Query console */}
        <Card3D className="p-5">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-400">
            <Terminal className="h-4 w-4 text-cyan-400" /> Event Query
          </h3>
          <div className="mb-3 flex gap-2">
            <div className="flex-1">
              <SearchInput value={query} onChange={setQuery} placeholder="IP, user, hostname, action…" />
            </div>
            <Button3D variant="primary" onClick={() => runQuery(query)}>
              <Search className="h-4 w-4" /> Hunt
            </Button3D>
          </div>
          {history.length > 0 ? (
            <div className="mb-3 flex flex-wrap gap-1.5">
              {history.map((h) => (
                <button key={h} onClick={() => { setQuery(h); runQuery(h); }} className="chip-3d !text-[10px]">
                  ⟳ {h}
                </button>
              ))}
            </div>
          ) : null}

          <div className="panel-inset max-h-72 space-y-2 overflow-y-auto p-3">
            {query && results.length === 0 ? (
              <p className="py-6 text-center text-sm text-slate-500">No events match “{query}”.</p>
            ) : null}
            {!query ? (
              <p className="py-6 text-center text-sm text-slate-500">Type a query and press Hunt — try “admin”, “10.”, or “login_failed”.</p>
            ) : null}
            {results.slice(0, 40).map((e) => (
              <div key={e.id} className="flex items-center gap-3 rounded-lg border border-slate-800/70 bg-slate-900/50 px-3 py-2">
                <SeverityBadge3D severity={e.severity} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-semibold text-slate-200">
                    {e.action} · {e.user_name ?? "—"} @ {e.hostname ?? "—"}
                  </p>
                  <p className="truncate font-mono text-[11px] text-slate-500">
                    {e.source_ip}:{e.destination_port} → {e.destination_ip} · {formatDateTime(e.timestamp)}
                  </p>
                </div>
                {e.source_ip ? (
                  <Button3D size="sm" variant="danger" onClick={() => blockIp(e.source_ip!)} title={`Block ${e.source_ip}`}>
                    <Ban className="h-3 w-3" />
                  </Button3D>
                ) : null}
              </div>
            ))}
          </div>
          {query && results.length > 0 ? (
            <p className="mt-2 text-xs text-slate-500">{results.length} match{results.length === 1 ? "" : "es"} (showing first 40)</p>
          ) : null}
        </Card3D>

        {/* AI analyst */}
        <Card3D className="p-5">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-400">
            <Sparkles className="h-4 w-4 text-violet-400" /> AI Analyst
          </h3>
          <div className="mb-3 flex gap-2">
            <input
              value={aiQuery}
              onChange={(e) => setAiQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && askAI()}
              placeholder="Ask about brute force, exfiltration, an incident…"
              className="panel-inset flex-1 px-3 py-2 text-sm text-slate-200 placeholder-slate-600 outline-none"
            />
            <Button3D variant="primary" loading={aiBusy} onClick={askAI}>
              Ask
            </Button3D>
          </div>
          <div className="mb-3 flex flex-wrap gap-1.5">
            {["Analyse brute force", "Check exfiltration", "Summarise incidents", "MITRE coverage"].map((s) => (
              <button key={s} onClick={() => { setAiQuery(s); }} className="chip-3d !text-[10px]">
                {s}
              </button>
            ))}
          </div>
          <div className="panel-inset min-h-[220px] p-4 text-sm leading-relaxed text-slate-200">
            {aiBusy ? (
              <p className="animate-pulse text-slate-500">Correlating events…</p>
            ) : aiReply ? (
              <p className="whitespace-pre-wrap">{aiReply}</p>
            ) : (
              <p className="text-slate-500">Ask a question or pick a suggestion above. The analyst correlates the last 24h of events.</p>
            )}
          </div>
        </Card3D>
      </div>
    </>
  );
}
