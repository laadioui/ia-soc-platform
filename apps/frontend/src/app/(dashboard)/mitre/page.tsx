"use client";

import { useState } from "react";
import { Search, ShieldCheck, Target, Activity, CheckCircle2 } from "lucide-react";

const tactics = [
  {
    id: "TA0001",
    name: "Initial Access",
    description: "Entry points used to gain a foothold in the environment.",
    techniques: [
      { id: "T1110", name: "Brute Force", detections: 14, status: "active" },
      { id: "T1566", name: "Phishing", detections: 8, status: "active" },
    ],
  },
  {
    id: "TA0006",
    name: "Credential Access",
    description: "Attempts to steal account names, passwords, hashes, and tokens.",
    techniques: [
      { id: "T1003", name: "OS Credential Dumping", detections: 6, status: "active" },
      { id: "T1555", name: "Credentials from Password Stores", detections: 3, status: "mitigated" },
    ],
  },
  {
    id: "TA0008",
    name: "Lateral Movement",
    description: "Movement through the network to reach high-value systems.",
    techniques: [
      { id: "T1021", name: "Remote Services", detections: 11, status: "active" },
      { id: "T1570", name: "Lateral Tool Transfer", detections: 4, status: "mitigated" },
    ],
  },
  {
    id: "TA0010",
    name: "Exfiltration",
    description: "Techniques used to steal data from protected systems.",
    techniques: [
      { id: "T1041", name: "Exfiltration Over C2 Channel", detections: 5, status: "active" },
      { id: "T1567", name: "Exfiltration Over Web Service", detections: 2, status: "none" },
    ],
  },
];

export default function MitrePage() {
  const [query, setQuery] = useState("");
  const filteredTactics = tactics
    .map((tactic) => ({
      ...tactic,
      techniques: tactic.techniques.filter(
        (technique) =>
          technique.name.toLowerCase().includes(query.toLowerCase()) ||
          technique.id.toLowerCase().includes(query.toLowerCase()) ||
          tactic.name.toLowerCase().includes(query.toLowerCase())
      ),
    }))
    .filter((tactic) => tactic.techniques.length > 0 || tactic.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">MITRE ATT&CK</h2>
          <p className="mt-1 text-sm text-slate-400">Mapped tactics, techniques, and detection coverage</p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-lg border border-cyber-green/20 bg-cyber-green/10 px-3 py-2 text-sm text-cyber-green">
          <ShieldCheck className="h-4 w-4" />
          Coverage Active
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: "Mapped Tactics", value: tactics.length, icon: Target, color: "text-cyber-cyan" },
          { label: "Active Detections", value: 36, icon: Activity, color: "text-cyber-orange" },
          { label: "Mitigated Techniques", value: 2, icon: CheckCircle2, color: "text-cyber-green" },
        ].map((stat) => (
          <div key={stat.label} className="card-glow flex items-center gap-3 rounded-xl p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-soc-surface">
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </div>
            <div>
              <p className="text-xs text-slate-400">{stat.label}</p>
              <p className="text-lg font-bold text-white">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search tactic or technique..."
          className="w-full rounded-lg border border-soc-border bg-soc-card py-2.5 pl-10 pr-4 text-sm text-slate-200 placeholder:text-slate-500 focus:border-cyber-cyan/50 focus:outline-none"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {filteredTactics.map((tactic) => (
          <section key={tactic.id} className="card-glow rounded-xl p-5">
            <div className="mb-4">
              <p className="font-mono text-xs text-cyber-cyan">{tactic.id}</p>
              <h3 className="text-lg font-semibold text-white">{tactic.name}</h3>
              <p className="mt-1 text-sm text-slate-400">{tactic.description}</p>
            </div>
            <div className="space-y-3">
              {tactic.techniques.map((technique) => (
                <div key={technique.id} className="rounded-lg border border-soc-border/50 bg-soc-surface/40 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-mono text-xs text-slate-500">{technique.id}</p>
                      <p className="text-sm font-medium text-white">{technique.name}</p>
                    </div>
                    <span className="rounded-full border border-cyber-cyan/20 bg-cyber-cyan/10 px-2.5 py-0.5 text-xs text-cyber-cyan">
                      {technique.detections} detections
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
