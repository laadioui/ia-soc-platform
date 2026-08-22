"use client";

import { useState } from "react";
import { SeverityBadge } from "@/components/severity-badge";
import { StatusBadge } from "@/components/status-badge";
import { Search, Filter, Bell, BellOff, CheckCircle, XCircle, Eye } from "lucide-react";
import type { Alert, Severity, Status } from "@/lib/types";

const mockAlerts: Alert[] = [
  { id: "ALT-7842", title: "Brute Force Attack Detected", description: "Over 500 failed SSH login attempts from 185.220.101.34 targeting multiple servers. Attack pattern indicates automated credential stuffing.", severity: "critical", status: "open", created_at: "2026-08-18T10:23:45Z", updated_at: "2026-08-18T10:23:45Z", source: "WAF-01", event_ids: ["EVT-001"], assigned_to: undefined, mitre_tactic: "Credential Access", mitre_technique: "T1110 - Brute Force" },
  { id: "ALT-7841", title: "Suspicious Outbound Connection", description: "Internal host 10.0.1.52 established connection to known C2 server at 45.33.32.156. Connection lasted 45 seconds before being terminated.", severity: "high", status: "investigating", created_at: "2026-08-18T10:21:12Z", updated_at: "2026-08-18T10:25:00Z", source: "EDR-03", event_ids: ["EVT-002"], assigned_to: "j.martinez", mitre_tactic: "Command and Control", mitre_technique: "T1071 - Application Layer Protocol" },
  { id: "ALT-7840", title: "Malware Signature Match", description: "Trojan.GenericKD.47823912 detected in downloaded file. File quarantined automatically. User action required for full remediation.", severity: "critical", status: "open", created_at: "2026-08-18T10:18:33Z", updated_at: "2026-08-18T10:18:33Z", source: "AV-02", event_ids: ["EVT-003"], assigned_to: undefined, mitre_tactic: "Execution", mitre_technique: "T1204 - User Execution" },
  { id: "ALT-7839", title: "Anomalous Login Pattern", description: "User r.williams logged in from unusual location (10.0.3.88) at non-business hours. Previous logins recorded from corporate office only.", severity: "medium", status: "pending", created_at: "2026-08-18T10:15:07Z", updated_at: "2026-08-18T10:20:00Z", source: "IAM-01", event_ids: ["EVT-004"], assigned_to: "admin", mitre_tactic: "Initial Access", mitre_technique: "T1078 - Valid Accounts" },
  { id: "ALT-7838", title: "Data Exfiltration Attempt", description: "Large data transfer (2.3 GB) detected from finance server to external IP. Transfer encrypted with non-standard protocol.", severity: "high", status: "open", created_at: "2026-08-18T10:08:19Z", updated_at: "2026-08-18T10:12:00Z", source: "DLP-01", event_ids: ["EVT-006"], assigned_to: undefined, mitre_tactic: "Exfiltration", mitre_technique: "T1041 - Exfiltration Over C2 Channel" },
  { id: "ALT-7837", title: "Privilege Escalation Detected", description: "User s.chen attempted to modify sudoers file. Action blocked by EDR policy. Potential lateral movement attempt.", severity: "critical", status: "investigating", created_at: "2026-08-18T10:05:56Z", updated_at: "2026-08-18T10:10:00Z", source: "SIEM-01", event_ids: ["EVT-007"], assigned_to: "j.martinez", mitre_tactic: "Privilege Escalation", mitre_technique: "T1548 - Abuse Elevation Control Mechanism" },
  { id: "ALT-7836", title: "Unauthorized USB Device", description: "USB mass storage device connected to workstation WS-042. Device not in approved hardware inventory.", severity: "low", status: "resolved", created_at: "2026-08-18T09:58:00Z", updated_at: "2026-08-18T10:15:00Z", source: "EDR-01", event_ids: ["EVT-008"], assigned_to: "admin", mitre_tactic: "Initial Access", mitre_technique: "T1091 - Replication Through Removable Media" },
  { id: "ALT-7835", title: "Failed MFA Challenge", description: "Multiple failed MFA verification attempts for admin account. Possible social engineering attack targeting IT administrators.", severity: "high", status: "open", created_at: "2026-08-18T09:52:00Z", updated_at: "2026-08-18T09:55:00Z", source: "IAM-01", event_ids: [], assigned_to: undefined, mitre_tactic: "Credential Access", mitre_technique: "T1621 - Multi-Factor Authentication Request Generation" },
];

export default function AlertsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
  const [statusFilter, setStatusFilter] = useState<Status | "all">("all");

  const filteredAlerts = mockAlerts.filter((alert) => {
    const matchesSearch =
      alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      alert.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      alert.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = severityFilter === "all" || alert.severity === severityFilter;
    const matchesStatus = statusFilter === "all" || alert.status === statusFilter;
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const severityCounts = {
    critical: mockAlerts.filter((a) => a.severity === "critical").length,
    high: mockAlerts.filter((a) => a.severity === "high").length,
    medium: mockAlerts.filter((a) => a.severity === "medium").length,
    low: mockAlerts.filter((a) => a.severity === "low").length,
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Alerts</h2>
        <p className="text-sm text-slate-400 mt-1">Manage and respond to security alerts</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        {[
          { label: "Critical", count: severityCounts.critical, color: "text-cyber-red", bg: "bg-cyber-red/10 border-cyber-red/20" },
          { label: "High", count: severityCounts.high, color: "text-orange-400", bg: "bg-orange-500/10 border-orange-500/20" },
          { label: "Medium", count: severityCounts.medium, color: "text-cyber-orange", bg: "bg-cyber-orange/10 border-cyber-orange/20" },
          { label: "Low", count: severityCounts.low, color: "text-cyber-blue", bg: "bg-cyber-blue/10 border-cyber-blue/20" },
        ].map((item) => (
          <div key={item.label} className={`card-glow rounded-xl p-4 border ${item.bg}`}>
            <p className="text-sm text-slate-400">{item.label} Alerts</p>
            <p className={`text-3xl font-bold mt-1 ${item.color}`}>{item.count}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search alerts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-soc-border bg-soc-card pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyber-cyan/50 focus:ring-1 focus:ring-cyber-cyan/20 transition-colors"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-500" />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value as Severity | "all")}
            className="rounded-lg border border-soc-border bg-soc-card px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyber-cyan/50 transition-colors"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as Status | "all")}
            className="rounded-lg border border-soc-border bg-soc-card px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyber-cyan/50 transition-colors"
          >
            <option value="all">All Statuses</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="pending">Pending</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {filteredAlerts.map((alert) => (
          <div key={alert.id} className="card-glow rounded-xl p-5 hover-glow cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <SeverityBadge severity={alert.severity} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-white">{alert.title}</h3>
                    <span className="text-xs text-slate-500 font-mono">{alert.id}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-400 max-w-2xl">{alert.description}</p>
                  <div className="mt-3 flex items-center gap-4">
                    {alert.mitre_tactic && (
                      <span className="inline-flex items-center gap-1 rounded-md bg-cyber-purple/10 px-2 py-0.5 text-xs text-cyber-purple border border-cyber-purple/20">
                        {alert.mitre_tactic}
                      </span>
                    )}
                    <span className="text-xs text-slate-500">Source: {alert.source}</span>
                    {alert.assigned_to && (
                      <span className="text-xs text-slate-500">Assigned: {alert.assigned_to}</span>
                    )}
                    <span className="text-xs text-slate-500">
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0 ml-4">
                <StatusBadge status={alert.status} />
                <div className="flex items-center gap-1 ml-2">
                  <button className="rounded-lg p-1.5 text-slate-400 hover:bg-soc-surface hover:text-cyber-cyan transition-colors" title="View Details">
                    <Eye className="h-4 w-4" />
                  </button>
                  <button className="rounded-lg p-1.5 text-slate-400 hover:bg-soc-surface hover:text-cyber-green transition-colors" title="Acknowledge">
                    <CheckCircle className="h-4 w-4" />
                  </button>
                  <button className="rounded-lg p-1.5 text-slate-400 hover:bg-soc-surface hover:text-cyber-red transition-colors" title="Dismiss">
                    <XCircle className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
