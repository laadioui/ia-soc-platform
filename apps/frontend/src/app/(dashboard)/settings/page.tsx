"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Database, PlugZap, RotateCcw, Save, XCircle } from "lucide-react";
import { useApp } from "@/components/app-shell";
import { api } from "@/lib/api";
import { Button3D, Card3D, PageHeader, useToast } from "@/components/ui";
import { defaultSettings, type SocSettings } from "@/lib/api";

export default function SettingsPage() {
  const toast = useToast();
  const { settings: liveSettings, setSettings } = useApp();
  const [draft, setDraft] = useState<SocSettings>(liveSettings);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<null | { ok: boolean; message: string }>(null);
  const [savedFlash, setSavedFlash] = useState(false);

  useEffect(() => setDraft(liveSettings), [liveSettings]);

  async function testConnection() {
    setTesting(true);
    setTestResult(null);
    try {
      const saved = { ...draft, apiUrl: draft.apiUrl.trim() || defaultSettings.apiUrl };
      window.localStorage.setItem("soc-settings", JSON.stringify(saved));
      const r = await api.events({ page: 1, page_size: 1 });
      setTestResult({ ok: true, message: `Connected — ${r.total.toLocaleString()} events available on the API.` });
    } catch {
      setTestResult({ ok: false, message: "Unreachable — the UI will keep running in DEMO mode." });
    }
    setTesting(false);
  }

  function save() {
    setSettings(draft);
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 1500);
    toast("Settings saved and applied", "ok");
  }

  return (
    <>
      <PageHeader
        title="Settings"
        subtitle="Every option here is applied immediately across the whole console"
        actions={
          <>
            <Button3D onClick={() => setDraft(liveSettings)}>
              <RotateCcw className="h-4 w-4" /> Reset
            </Button3D>
            <Button3D variant="primary" onClick={save}>
              <Save className="h-4 w-4" /> {savedFlash ? "Saved ✓" : "Save settings"}
            </Button3D>
          </>
        }
      />

      <div className="grid gap-4 lg:grid-cols-2">
        {/* API connection */}
        <Card3D className="p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-400">
            <PlugZap className="h-4 w-4 text-cyan-400" /> API Connection
          </h3>

          <label className="mb-1 block text-xs font-bold uppercase tracking-widest text-slate-500">Backend URL</label>
          <input
            value={draft.apiUrl}
            onChange={(e) => setDraft({ ...draft, apiUrl: e.target.value })}
            placeholder="http://localhost:8000/api/v1"
            className="panel-inset mb-4 w-full px-3 py-2 font-mono text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-cyan-500/40"
          />

          <label className="mb-1 block text-xs font-bold uppercase tracking-widest text-slate-500">Data mode</label>
          <div className="mb-2 flex gap-2">
            <button
              onClick={() => setDraft({ ...draft, demoMode: false })}
              className={`chip-3d ${!draft.demoMode ? "chip-3d-active" : ""}`}
            >
              Live API (auto-fallback)
            </button>
            <button
              onClick={() => setDraft({ ...draft, demoMode: true })}
              className={`chip-3d ${draft.demoMode ? "chip-3d-active" : ""}`}
            >
              Force demo data
            </button>
          </div>
          <p className="mb-4 text-[11px] leading-relaxed text-slate-500">
            In live mode the console calls the backend and falls back to built-in demo data whenever the API is
            unreachable. Forcing demo always uses the offline dataset.
          </p>

          <div className="flex items-center gap-2">
            <Button3D loading={testing} onClick={testConnection}>
              <Database className="h-4 w-4" /> Test connection
            </Button3D>
          </div>
          {testResult ? (
            <div
              className={`animate-pop mt-3 flex items-center gap-2 rounded-lg border px-3 py-2 text-xs ${
                testResult.ok
                  ? "border-emerald-500/40 bg-emerald-950/30 text-emerald-300"
                  : "border-amber-500/40 bg-amber-950/30 text-amber-300"
              }`}
            >
              {testResult.ok ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
              {testResult.message}
            </div>
          ) : null}
        </Card3D>

        {/* Console behaviour */}
        <Card3D className="p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-400">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Console Behaviour
          </h3>

          <label className="mb-1 block text-xs font-bold uppercase tracking-widest text-slate-500">
            Auto-refresh interval — {draft.refreshSeconds}s
          </label>
          <input
            type="range"
            min={10}
            max={120}
            step={5}
            value={draft.refreshSeconds}
            onChange={(e) => setDraft({ ...draft, refreshSeconds: Number(e.target.value) })}
            className="mb-4 w-full accent-cyan-400"
          />
          <p className="text-[11px] leading-relaxed text-slate-500">
            How often the topbar probe re-checks the backend and refreshes counters (10–120s). Applies on save.
          </p>

          <div className="panel-inset mt-4 space-y-2 p-3.5 text-xs text-slate-400">
            <p className="flex justify-between"><span>Current mode</span><span className={draft.demoMode ? "text-amber-300" : "text-emerald-300"}>{draft.demoMode ? "DEMO DATA" : "LIVE API"}</span></p>
            <p className="flex justify-between"><span>Backend</span><span className="font-mono text-slate-300">{draft.apiUrl.replace(/^https?:\/\//, "")}</span></p>
            <p className="flex justify-between"><span>Settings storage</span><span className="text-slate-300">browser localStorage</span></p>
          </div>
        </Card3D>
      </div>

      <Card3D className="p-5">
        <h3 className="mb-3 text-sm font-bold uppercase tracking-widest text-slate-400">About</h3>
        <p className="text-sm leading-relaxed text-slate-400">
          AI SOC Platform console — Next.js 15, Tailwind CSS, Recharts. Data services: FastAPI collector
          (events, alerts, incidents, MITRE, threat intel, SOAR response actions) with graceful offline demo mode.
        </p>
      </Card3D>
    </>
  );
}
