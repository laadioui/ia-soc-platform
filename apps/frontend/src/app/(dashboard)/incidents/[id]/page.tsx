"use client";

import { use } from "react";
import { SeverityBadge } from "@/components/severity-badge";
import { StatusBadge } from "@/components/status-badge";
import { ArrowLeft, Clock, User, Shield, Brain, AlertTriangle, ExternalLink, Plus } from "lucide-react";
import Link from "next/link";
import type { TimelineEntry, IOC } from "@/lib/types";

const incident = {
  id: "INC-0042",
  title: "Active SSH Brute Force Campaign",
  description: "Coordinated brute force attack targeting multiple production servers. Attacker using Tor exit nodes. 5 servers potentially compromised. Initial access vector appears to be via exposed SSH ports on legacy systems that were not included in the recent hardening sprint.",
  severity: "critical" as const,
  status: "investigating" as const,
  created_at: "2026-08-18T10:23:45Z",
  updated_at: "2026-08-18T10:30:00Z",
  assigned_to: "j.martinez",
  alert_ids: ["ALT-7842", "ALT-7837"],
  event_ids: ["EVT-001", "EVT-007", "EVT-009", "EVT-012"],
  timeline: [
    { id: "TL-1", timestamp: "2026-08-18T10:23:45Z", action: "Alert Triggered", user: "System", details: "WAF detected 500+ failed SSH login attempts from 185.220.101.34" },
    { id: "TL-2", timestamp: "2026-08-18T10:25:00Z", action: "Alert Created", user: "System", details: "Alert ALT-7842 created and assigned to on-call analyst" },
    { id: "TL-3", timestamp: "2026-08-18T10:28:12Z", action: "Investigation Started", user: "j.martinez", details: "Analyst acknowledged alert and began investigation" },
    { id: "TL-4", timestamp: "2026-08-18T10:30:00Z", action: "Incident Created", user: "j.martinez", details: "Incident INC-0042 created. Multiple alerts correlated." },
    { id: "TL-5", timestamp: "2026-08-18T10:32:45Z", action: "IP Blocked", user: "j.martinez", details: "Attacker IP 185.220.101.34 blocked at perimeter firewall" },
    { id: "TL-6", timestamp: "2026-08-18T10:35:00Z", action: "AI Analysis Complete", user: "AI Assistant", details: "AI identified attack pattern as part of known APT group campaign. Recommended credential rotation for all SSH users." },
  ],
  iocs: [
    { id: "IOC-1", type: "ip" as const, value: "185.220.101.34", confidence: 95, first_seen: "2026-08-18T10:20:00Z", last_seen: "2026-08-18T10:23:45Z", tags: ["tor-exit-node", "brute-force"] },
    { id: "IOC-2", type: "ip" as const, value: "103.43.75.120", confidence: 88, first_seen: "2026-08-18T09:50:00Z", last_seen: "2026-08-18T10:05:56Z", tags: ["c2-server", "sql-injection"] },
    { id: "IOC-3", type: "hash" as const, value: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", confidence: 100, first_seen: "2026-08-18T10:18:33Z", last_seen: "2026-08-18T10:18:33Z", tags: ["malware", "trojan"] },
    { id: "IOC-4", type: "domain" as const, value: "malware-distribution.example.com", confidence: 82, first_seen: "2026-08-18T10:15:00Z", last_seen: "2026-08-18T10:18:33Z", tags: ["malware-hosting"] },
  ],
  ai_analysis: `## AI Analysis Summary

### Threat Assessment
This incident represents a **high-confidence active attack** targeting our SSH infrastructure. The attack pattern matches known TTPs of APT group "Sandstorm" (tracked as APT-41 variant).

### Attack Chain
1. **Reconnaissance**: Attacker scanned for exposed SSH ports (T1046)
2. **Credential Access**: Automated brute force using common credential lists (T1110)
3. **Lateral Movement**: Successfully authenticated on 2 of 5 targeted servers
4. **Persistence**: Created backdoor user account on compromised hosts (T1136)

### Affected Systems
- PROD-WEB-01: Compromised (root access achieved)
- PROD-APP-03: Compromised (backdoor user created)
- PROD-DB-01: Attack blocked, no compromise
- PROD-WEB-02: Attack blocked, no compromise
- PROD-APP-01: Attack blocked, no compromise

### Recommendations
1. **Immediate**: Rotate all SSH credentials across production environment
2. **Immediate**: Remove backdoor accounts from compromised hosts
3. **Short-term**: Implement IP allowlisting for SSH access
4. **Long-term**: Migrate to key-only SSH authentication, implement network segmentation

### MITRE ATT&CK Mapping
- T1110.001 - Brute Force: Password Guessing
- T1078.002 - Valid Accounts: Domain Accounts
- T1136.001 - Create Account: Local Account
- T1059.004 - Command and Scripting Interpreter: Unix Shell`,
};

const iocTypeColors: Record<string, string> = {
  ip: "bg-cyber-cyan/10 text-cyber-cyan border-cyber-cyan/20",
  domain: "bg-cyber-purple/10 text-cyber-purple border-cyber-purple/20",
  hash: "bg-cyber-orange/10 text-cyber-orange border-cyber-orange/20",
  url: "bg-cyber-blue/10 text-cyber-blue border-cyber-blue/20",
  email: "bg-cyber-green/10 text-cyber-green border-cyber-green/20",
};

export default function IncidentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/incidents" className="rounded-lg border border-soc-border bg-soc-card p-2 text-slate-400 hover:text-white hover:bg-soc-surface transition-colors">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <SeverityBadge severity={incident.severity} />
            <StatusBadge status={incident.status} />
            <span className="text-sm text-slate-500 font-mono">{incident.id}</span>
          </div>
          <h2 className="text-2xl font-bold text-white mt-2">{incident.title}</h2>
          <p className="text-sm text-slate-400 mt-1">{incident.description}</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="rounded-lg border border-soc-border bg-soc-card px-4 py-2 text-sm text-slate-300 hover:bg-soc-surface transition-colors">
            Edit
          </button>
          <button className="rounded-lg bg-gradient-to-r from-cyber-cyan to-cyber-blue px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity">
            Escalate
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card-glow rounded-xl p-5">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Details</h3>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-sm text-slate-500">Assigned To</dt>
              <dd className="text-sm text-white">{incident.assigned_to || "Unassigned"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-slate-500">Created</dt>
              <dd className="text-sm text-white">{new Date(incident.created_at).toLocaleString()}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-slate-500">Last Updated</dt>
              <dd className="text-sm text-white">{new Date(incident.updated_at).toLocaleString()}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-slate-500">Related Alerts</dt>
              <dd className="text-sm text-cyber-cyan">{incident.alert_ids.length}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-slate-500">Related Events</dt>
              <dd className="text-sm text-cyber-cyan">{incident.event_ids.length}</dd>
            </div>
          </dl>
        </div>

        <div className="lg:col-span-2 card-glow rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-400">AI Analysis</h3>
            <span className="inline-flex items-center gap-1 rounded-md bg-cyber-purple/10 px-2 py-0.5 text-xs text-cyber-purple border border-cyber-purple/20">
              <Brain className="h-3 w-3" />
              AI Generated
            </span>
          </div>
          <div className="prose prose-invert prose-sm max-w-none">
            {incident.ai_analysis?.split("\n").map((line, i) => {
              if (line.startsWith("## ")) return <h2 key={i} className="text-lg font-bold text-white mt-4 mb-2">{line.replace("## ", "")}</h2>;
              if (line.startsWith("### ")) return <h3 key={i} className="text-md font-semibold text-white mt-3 mb-1">{line.replace("### ", "")}</h3>;
              if (line.startsWith("- **")) {
                const match = line.match(/^- \*\*(.+?)\*\*:?\s*(.*)$/);
                if (match) return <div key={i} className="flex gap-2 ml-4 mb-1"><span className="text-cyber-cyan font-medium">{match[1]}:</span><span className="text-slate-300">{match[2]}</span></div>;
              }
              if (line.match(/^\d+\.\s*\*\*/)) {
                const match = line.match(/^\d+\.\s*\*\*(.+?)\*\*:?\s*(.*)$/);
                if (match) return <div key={i} className="flex gap-2 ml-4 mb-1"><span className="text-cyber-orange font-medium">{match[1]}:</span><span className="text-slate-300">{match[2]}</span></div>;
              }
              if (line.startsWith("- ")) return <div key={i} className="ml-4 mb-1 text-slate-300">{line}</div>;
              if (line.match(/^\d+\.\s/)) return <div key={i} className="ml-4 mb-1 text-slate-300">{line}</div>;
              if (line.trim() === "") return <br key={i} />;
              return <p key={i} className="text-sm text-slate-300 mb-1">{line}</p>;
            })}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card-glow rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-400">Timeline</h3>
            <button className="inline-flex items-center gap-1 text-xs text-cyber-cyan hover:text-cyber-cyan/80 transition-colors">
              <Plus className="h-3 w-3" /> Add Entry
            </button>
          </div>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-px bg-soc-border" />
            <div className="space-y-4">
              {incident.timeline.map((entry: TimelineEntry) => (
                <div key={entry.id} className="relative flex gap-4 pl-10">
                  <div className="absolute left-2.5 top-1 h-3 w-3 rounded-full border-2 border-soc-card bg-cyber-cyan" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white">{entry.action}</span>
                      <span className="text-xs text-slate-500">by {entry.user}</span>
                    </div>
                    <p className="text-sm text-slate-400 mt-0.5">{entry.details}</p>
                    <span className="text-xs text-slate-500 mt-1 block">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card-glow rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-400">Indicators of Compromise</h3>
            <button className="inline-flex items-center gap-1 text-xs text-cyber-cyan hover:text-cyber-cyan/80 transition-colors">
              <Plus className="h-3 w-3" /> Add IOC
            </button>
          </div>
          <div className="space-y-3">
            {incident.iocs.map((ioc: IOC) => (
              <div key={ioc.id} className="rounded-lg border border-soc-border/50 bg-soc-surface/30 p-3">
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${iocTypeColors[ioc.type]}`}>
                        {ioc.type.toUpperCase()}
                      </span>
                      <span className="text-xs text-slate-500">Confidence: {ioc.confidence}%</span>
                    </div>
                    <p className="mt-1.5 text-sm font-mono text-white break-all">{ioc.value}</p>
                    <div className="mt-2 flex items-center gap-2">
                      {ioc.tags.map((tag) => (
                        <span key={tag} className="inline-flex items-center rounded bg-soc-surface px-1.5 py-0.5 text-xs text-slate-400">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button className="ml-2 rounded p-1 text-slate-400 hover:text-cyber-cyan transition-colors">
                    <ExternalLink className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
