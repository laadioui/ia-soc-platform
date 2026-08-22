"use client";

import { useState } from "react";
import { Search, Filter, ExternalLink, RefreshCw, Globe, Shield, AlertTriangle, Tag } from "lucide-react";
import { SeverityBadge } from "@/components/severity-badge";
import type { ThreatIntel } from "@/lib/types";

const mockThreats: ThreatIntel[] = [
  {
    id: "TI-001",
    title: "APT-41 Activity Targeting Financial Institutions",
    description: "Chinese APT group APT-41 has been observed conducting spear-phishing campaigns against financial institutions in North America and Europe. The group is using a new backdoor variant dubbed \"ShadowGate\" that evades most EDR solutions.",
    type: "APT Campaign",
    severity: "critical",
    source: "MITRE + CrowdStrike",
    published: "2026-08-18T08:00:00Z",
    tags: ["apt-41", "financial-sector", "spear-phishing", "backdoor"],
    iocs: [
      { id: "IOC-1", type: "ip", value: "185.220.101.34", confidence: 95, first_seen: "2026-08-15", last_seen: "2026-08-18", tags: ["c2"] },
      { id: "IOC-2", type: "hash", value: "a1b2c3d4e5f6...", confidence: 90, first_seen: "2026-08-16", last_seen: "2026-08-18", tags: ["malware"] },
    ],
  },
  {
    id: "TI-002",
    title: "Zero-Day in OpenSSL CVE-2026-38291",
    description: "Critical buffer overflow vulnerability in OpenSSL 3.1.x allows remote code execution. No patch available yet. Exploitation observed in the wild since August 15, 2026.",
    type: "Vulnerability",
    severity: "critical",
    source: "NVD + CISA",
    published: "2026-08-17T14:30:00Z",
    tags: ["zero-day", "openssl", "rce", "cve-2026-38291"],
    iocs: [],
    url: "https://nvd.nist.gov/vuln/detail/CVE-2026-38291",
  },
  {
    id: "TI-003",
    title: "Ransomware Group \"BlackStorm\" New Campaign",
    description: "BlackStorm ransomware group targeting healthcare and critical infrastructure with updated encryption algorithm. Ransom demands averaging $2.3M in cryptocurrency.",
    type: "Ransomware",
    severity: "high",
    source: " Recorded Future",
    published: "2026-08-17T10:00:00Z",
    tags: ["ransomware", "blackstorm", "healthcare", "critical-infrastructure"],
    iocs: [
      { id: "IOC-3", type: "domain", value: "payment-blacksheet.onion", confidence: 88, first_seen: "2026-08-10", last_seen: "2026-08-17", tags: ["ransomware-payment"] },
    ],
  },
  {
    id: "TI-004",
    title: "Credential Stuffing Campaign Using Leaked Databases",
    description: "Large-scale credential stuffing campaign using recently leaked database from social media platform. Over 200 million credentials being tested across major services.",
    type: "Credential Threat",
    severity: "high",
    source: "HaveIBeenPwned",
    published: "2026-08-16T16:00:00Z",
    tags: ["credential-stuffing", "data-leak", "brute-force"],
    iocs: [],
  },
  {
    id: "TI-005",
    title: "New Phishing Kit \"PhishMaster\" Spreading",
    description: "Sophisticated phishing-as-a-service platform targeting banking credentials. Features real-time proxy for MFA bypass and AI-generated phishing content.",
    type: "Phishing",
    severity: "medium",
    source: "PhishTank",
    published: "2026-08-16T09:00:00Z",
    tags: ["phishing", "mfa-bypass", "banking"],
    iocs: [
      { id: "IOC-4", type: "url", value: "https://secure-login-bank.phishmaster.xyz/*", confidence: 85, first_seen: "2026-08-14", last_seen: "2026-08-16", tags: ["phishing-url"] },
    ],
  },
  {
    id: "TI-006",
    title: "Kubernetes API Server Vulnerability",
    description: "Privilege escalation vulnerability in Kubernetes API server allows authenticated users to gain cluster-admin privileges. Affects versions 1.25-1.29.",
    type: "Vulnerability",
    severity: "high",
    source: "Kubernetes Security",
    published: "2026-08-15T12:00:00Z",
    tags: ["kubernetes", "privilege-escalation", "cve-2026-37845"],
    iocs: [],
  },
];

const typeColors: Record<string, string> = {
  "APT Campaign": "bg-cyber-red/10 text-cyber-red border-cyber-red/20",
  "Vulnerability": "bg-cyber-orange/10 text-cyber-orange border-cyber-orange/20",
  "Ransomware": "bg-cyber-purple/10 text-cyber-purple border-cyber-purple/20",
  "Credential Threat": "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  "Phishing": "bg-cyber-blue/10 text-cyber-blue border-cyber-blue/20",
};

export default function ThreatIntelPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");

  const filteredThreats = mockThreats.filter((t) => {
    const matchesSearch =
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.tags.some((tag) => tag.includes(searchQuery.toLowerCase()));
    const matchesType = typeFilter === "all" || t.type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Threat Intelligence</h2>
          <p className="text-sm text-slate-400 mt-1">Latest threat intelligence feeds and indicators</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-soc-border bg-soc-card px-3 py-2 text-sm text-slate-300 hover:bg-soc-surface transition-colors">
          <RefreshCw className="h-4 w-4" />
          Refresh Feeds
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        {[
          { icon: Globe, label: "Active Feeds", value: "12", color: "text-cyber-cyan" },
          { icon: Shield, label: "IOCs Tracked", value: "4,892", color: "text-cyber-blue" },
          { icon: AlertTriangle, label: "Critical Threats", value: "3", color: "text-cyber-red" },
          { icon: Tag, label: "Tags", value: "156", color: "text-cyber-green" },
        ].map((stat) => (
          <div key={stat.label} className="card-glow rounded-xl p-4 flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-soc-surface`}>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </div>
            <div>
              <p className="text-xs text-slate-400">{stat.label}</p>
              <p className="text-lg font-bold text-white">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search threats, IOCs, tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-soc-border bg-soc-card pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyber-cyan/50 focus:ring-1 focus:ring-cyber-cyan/20 transition-colors"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="rounded-lg border border-soc-border bg-soc-card px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyber-cyan/50 transition-colors"
        >
          <option value="all">All Types</option>
          <option value="APT Campaign">APT Campaign</option>
          <option value="Vulnerability">Vulnerability</option>
          <option value="Ransomware">Ransomware</option>
          <option value="Credential Threat">Credential Threat</option>
          <option value="Phishing">Phishing</option>
        </select>
      </div>

      <div className="space-y-4">
        {filteredThreats.map((threat) => (
          <div key={threat.id} className="card-glow rounded-xl p-5 hover-glow">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <SeverityBadge severity={threat.severity} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-white">{threat.title}</h3>
                    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${typeColors[threat.type] || "bg-slate-500/10 text-slate-400"}`}>
                      {threat.type}
                    </span>
                  </div>
                  <p className="mt-1.5 text-sm text-slate-400 max-w-3xl">{threat.description}</p>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    {threat.tags.map((tag) => (
                      <span key={tag} className="inline-flex items-center rounded bg-soc-surface px-2 py-0.5 text-xs text-slate-400">
                        #{tag}
                      </span>
                    ))}
                  </div>
                  <div className="mt-3 flex items-center gap-4 text-xs text-slate-500">
                    <span>Source: <span className="text-slate-300">{threat.source}</span></span>
                    <span>Published: {new Date(threat.published).toLocaleDateString()}</span>
                    {threat.iocs.length > 0 && (
                      <span>IOCs: <span className="text-cyber-cyan">{threat.iocs.length}</span></span>
                    )}
                  </div>
                </div>
              </div>
              <button className="ml-4 shrink-0 rounded p-1.5 text-slate-400 hover:text-cyber-cyan transition-colors">
                <ExternalLink className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
