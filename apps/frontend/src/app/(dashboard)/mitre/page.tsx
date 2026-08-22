"use client";

import { useEffect, useMemo, useState } from "react";
import { Target } from "lucide-react";
import { useApp } from "@/components/app-shell";
import { api } from "@/lib/api";
import { demoData } from "@/lib/demo-data";
import { Button3D, Card3D, Modal3D, PageHeader, SearchInput, useToast } from "@/components/ui";
import type { MITRETechniqueEntry } from "@/lib/types";

const TACTIC_ORDER = [
  "Initial Access",
  "Execution",
  "Persistence",
  "Privilege Escalation",
  "Defense Evasion",
  "Credential Access",
  "Discovery",
  "Lateral Movement",
  "Collection",
  "Command and Control",
  "Exfiltration",
  "Impact",
];

export default function MitrePage() {
  const toast = useToast();
  const { settings, refreshKey } = useApp();
  const [techniques, setTechniques] = useState<MITRETechniqueEntry[]>(demoData.mitre);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<MITRETechniqueEntry | null>(null);

  useEffect(() => {
    if (settings.demoMode) {
      setTechniques(demoData.mitre);
      return;
    }
    let cancelled = false;
    api
      .mitre()
      .then((r) => !cancelled && setTechniques(r.length ? r : demoData.mitre))
      .catch(() => !cancelled && setTechniques(demoData.mitre));
    return () => {
      cancelled = true;
    };
  }, [settings.demoMode, settings.apiUrl, refreshKey]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    if (!q) return techniques;
    return techniques.filter((t) =>
      [t.technique_id, t.name, t.tactic, t.description].filter(Boolean).some((v) =>
        String(v).toLowerCase().includes(q)
      )
    );
  }, [techniques, search]);

  const tactics = useMemo(() => {
    const groups = new Map<string, MITRETechniqueEntry[]>();
    for (const t of filtered) {
      const key = t.tactic || "Other";
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(t);
    }
    return [...groups.entries()].sort(
      (a, b) =>
        (TACTIC_ORDER.indexOf(a[0]) + 100) % 1000 - ((TACTIC_ORDER.indexOf(b[0]) + 100) % 1000) ||
        TACTIC_ORDER.indexOf(a[0]) - TACTIC_ORDER.indexOf(b[0])
    );
  }, [filtered]);

  return (
    <>
      <PageHeader
        title="MITRE ATT&CK Matrix"
        subtitle={`${techniques.length} techniques mapped · ${tactics.length} tactics · click any cell for details`}
        actions={
          <Button3D
            onClick={() => {
              toast(`Export queued: ${filtered.length} techniques`, "info");
            }}
          >
            Export view
          </Button3D>
        }
      />

      <div className="max-w-md">
        <SearchInput value={search} onChange={setSearch} placeholder="Search technique, ID or tactic…" />
      </div>

      <div className="overflow-x-auto pb-2">
        <div className="flex gap-3" style={{ minWidth: Math.max(900, tactics.length * 170) }}>
          {tactics.map(([tactic, techs]) => (
            <div key={tactic} className="w-[168px] shrink-0">
              <div className="card-3d mb-2 px-3 py-2.5 text-center">
                <p className="text-[10px] font-black uppercase leading-tight tracking-widest text-cyan-300">{tactic}</p>
                <p className="mt-0.5 text-[10px] text-slate-500">{techs.length} technique{techs.length === 1 ? "" : "s"}</p>
              </div>
              <div className="space-y-2">
                {techs.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setSelected(t)}
                    className="card-3d card-3d-hover w-full px-3 py-2.5 text-left"
                  >
                    <p className="font-mono text-[11px] font-bold text-orange-300">{t.technique_id}</p>
                    <p className="mt-0.5 text-xs font-medium leading-snug text-slate-300">{t.name}</p>
                  </button>
                ))}
              </div>
            </div>
          ))}
          {tactics.length === 0 ? (
            <Card3D className="w-full p-8 text-center text-sm text-slate-500">
              No techniques match “{search}”.
            </Card3D>
          ) : null}
        </div>
      </div>

      <Modal3D open={!!selected} onClose={() => setSelected(null)} title={selected ? `${selected.technique_id} — ${selected.name}` : ""}>
        {selected ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="plate-3d h-11 w-11">
                <Target className="h-5 w-5 text-orange-300" />
              </div>
              <div>
                <p className="font-mono text-sm font-bold text-orange-300">{selected.technique_id}</p>
                <p className="text-xs uppercase tracking-widest text-slate-500">{selected.tactic}</p>
              </div>
            </div>
            <p className="text-sm leading-relaxed text-slate-300">{selected.description}</p>
            {selected.platform ? (
              <div>
                <p className="mb-1.5 text-[10px] font-bold uppercase tracking-widest text-slate-500">Platforms</p>
                <div className="flex flex-wrap gap-1.5">
                  {selected.platform.map((p) => (
                    <span key={p} className="chip-3d !cursor-default !py-0.5 !text-[10px]">{p}</span>
                  ))}
                </div>
              </div>
            ) : null}
            <div className="flex justify-end">
              <Button3D
                variant="primary"
                onClick={() => {
                  toast(`Detection-rule scan queued for ${selected!.technique_id}`, "ok");
                  setSelected(null);
                }}
              >
                Scan coverage for this technique
              </Button3D>
            </div>
          </div>
        ) : null}
      </Modal3D>
    </>
  );
}
