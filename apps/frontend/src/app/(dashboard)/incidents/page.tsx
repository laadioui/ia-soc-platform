"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SeverityBadge } from "@/components/severity-badge";
import { StatusBadge } from "@/components/status-badge";
import { Search, Plus, ExternalLink, X } from "lucide-react";
import type { Incident, Severity, Status } from "@/lib/types";

const mockIncidentsSeed: Incident[] = [
  { id: "INC-0042", title: "Active SSH Brute Force Campaign", description: "Coordinated brute force attack targeting multiple production servers. Attacker using Tor exit nodes. 5 servers potentially compromised.", severity: "critical", status: "investigating", created_at: "2026-08-18T10:23:45Z", updated_at: "2026-08-18T10:30:00Z", assigned_to: "j.martinez", alert_ids: ["ALT-7842", "ALT-7837"], event_ids: ["EVT-001", "EVT-007"], timeline: [], iocs: [], ai_analysis: "High-confidence automated attack pattern. Recommend immediate isolation of affected servers and credential rotation." },
  { id: "INC-0041", title: "Potential Data Breach - Finance Dept", description: "Large encrypted data transfer detected from finance database server to external IP. DLP policy triggered. No authorized data transfer scheduled.", severity: "high", status: "open", created_at: "2026-08-18T10:08:19Z", updated_at: "2026-08-18T10:15:00Z", assigned_to: undefined, alert_ids: ["ALT-7838"], event_ids: ["EVT-006"], timeline: [], iocs: [] },
  { id: "INC-0040", title: "Malware Outbreak - Engineering Wing", description: "Multiple workstations in engineering detected with same malware variant. Patient zero likely workstation WS-042.", severity: "critical", status: "investigating", created_at: "2026-08-18T09:45:00Z", updated_at: "2026-08-18T10:20:00Z", assigned_to: "admin", alert_ids: ["ALT-7840"], event_ids: ["EVT-003"], timeline: [], iocs: [] },
  { id: "INC-0039", title: "Suspicious VPN Access Pattern", description: "VPN account 'backup-svc' accessing resources from multiple countries within short timeframe. Possible credential compromise.", severity: "medium", status: "pending", created_at: "2026-08-17T22:30:00Z", updated_at: "2026-08-18T08:00:00Z", assigned_to: "s.chen", alert_ids: [], event_ids: [], timeline: [], iocs: [] },
  { id: "INC-0038", title: "Phishing Campaign - HR Department", description: "Spear-phishing emails targeting HR with malicious PDF attachments. 3 employees clicked malicious links.", severity: "high", status: "investigating", created_at: "2026-08-17T14:00:00Z", updated_at: "2026-08-18T09:30:00Z", assigned_to: "r.williams", alert_ids: [], event_ids: [], timeline: [], iocs: [] },
  { id: "INC-0037", title: "Unauthorized Cloud Resource Provisioning", description: "AWS account used to spin up 5 high-performance GPU instances. Billing spike detected. Possible cryptomining.", severity: "medium", status: "resolved", created_at: "2026-08-16T08:00:00Z", updated_at: "2026-08-17T16:00:00Z", assigned_to: "admin", alert_ids: [], event_ids: [], timeline: [], iocs: [] },
  { id: "INC-0036", title: "DNS Tunneling Detected", description: "Unusual DNS query patterns indicating potential data exfiltration via DNS tunneling from internal server.", severity: "high", status: "closed", created_at: "2026-08-15T11:00:00Z", updated_at: "2026-08-16T14:00:00Z", assigned_to: "j.martinez", alert_ids: [], event_ids: [], timeline: [], iocs: [] },
];

export default function IncidentsPage() {
  const router = useRouter();
  const [incidents, setIncidents] = useState<Incident[]>(mockIncidentsSeed);
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
  const [statusFilter, setStatusFilter] = useState<Status | "all">("all");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newIncident, setNewIncident] = useState({
    title: "",
    description: "",
    severity: "medium" as Severity,
    status: "open" as Status,
  });

  const filteredIncidents = incidents.filter((inc) => {
    const matchesSearch =
      inc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = severityFilter === "all" || inc.severity === severityFilter;
    const matchesStatus = statusFilter === "all" || inc.status === statusFilter;
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const handleCreateIncident = (event: React.FormEvent) => {
    event.preventDefault();

    if (!newIncident.title.trim() || !newIncident.description.trim()) {
      return;
    }

    const id = `INC-${String(incidents.length + 1).padStart(4, "0")}`;
    const createdAt = new Date().toISOString();
    const incident: Incident = {
      id,
      title: newIncident.title.trim(),
      description: newIncident.description.trim(),
      severity: newIncident.severity,
      status: newIncident.status,
      created_at: createdAt,
      updated_at: createdAt,
      assigned_to: "analyst",
      alert_ids: [],
      event_ids: [],
      timeline: [],
      iocs: [],
      ai_analysis: "New incident created from the dashboard workflow.",
    };

    setIncidents((current) => [incident, ...current]);
    setNewIncident({ title: "", description: "", severity: "medium", status: "open" });
    setShowCreateModal(false);
    router.push(`/incidents/${incident.id}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Incidents</h2>
          <p className="text-sm text-slate-400 mt-1">Track and manage security incidents</p>
        </div>
        <button
          type="button"
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyber-cyan to-cyber-blue px-4 py-2.5 text-sm font-medium text-white hover:opacity-90 transition-opacity"
        >
          <Plus className="h-4 w-4" />
          Create Incident
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-5">
        {[
          { label: "Open", count: incidents.filter((i) => i.status === "open").length, color: "text-cyber-red" },
          { label: "Investigating", count: incidents.filter((i) => i.status === "investigating").length, color: "text-cyber-orange" },
          { label: "Pending", count: incidents.filter((i) => i.status === "pending").length, color: "text-yellow-400" },
          { label: "Resolved", count: incidents.filter((i) => i.status === "resolved").length, color: "text-cyber-green" },
          { label: "Closed", count: incidents.filter((i) => i.status === "closed").length, color: "text-slate-400" },
        ].map((item) => (
          <div key={item.label} className="card-glow rounded-xl p-4 text-center">
            <p className="text-sm text-slate-400">{item.label}</p>
            <p className={`text-2xl font-bold mt-1 ${item.color}`}>{item.count}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search incidents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-soc-border bg-soc-card pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyber-cyan/50 focus:ring-1 focus:ring-cyber-cyan/20 transition-colors"
          />
        </div>
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
          <option value="closed">Closed</option>
        </select>
      </div>

      <div className="space-y-3">
        {filteredIncidents.map((incident) => (
          <div
            key={incident.id}
            className="card-glow rounded-xl p-5 hover-glow cursor-pointer"
            onClick={() => router.push(`/incidents/${incident.id}`)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <SeverityBadge severity={incident.severity} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-white">{incident.title}</h3>
                    <span className="text-xs text-slate-500 font-mono">{incident.id}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-400 max-w-2xl">{incident.description}</p>
                  <div className="mt-3 flex items-center gap-4">
                    {incident.assigned_to && (
                      <span className="text-xs text-slate-500">
                        Assigned: <span className="text-slate-300">{incident.assigned_to}</span>
                      </span>
                    )}
                    <span className="text-xs text-slate-500">
                      Alerts: <span className="text-slate-300">{incident.alert_ids.length}</span>
                    </span>
                    <span className="text-xs text-slate-500">
                      Events: <span className="text-slate-300">{incident.event_ids.length}</span>
                    </span>
                    <span className="text-xs text-slate-500">
                      Updated: {new Date(incident.updated_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0 ml-4">
                <StatusBadge status={incident.status} />
                <ExternalLink className="h-4 w-4 text-slate-500" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-xl rounded-2xl border border-soc-border bg-[#0f172a] p-6 shadow-2xl shadow-black/30">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">New incident</p>
                <h3 className="text-xl font-semibold text-white">Create Incident</h3>
              </div>
              <button type="button" onClick={() => setShowCreateModal(false)} className="rounded-lg p-2 text-slate-300 hover:bg-slate-800">
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCreateIncident} className="space-y-4">
              <div>
                <label className="mb-2 block text-sm text-slate-300">Title</label>
                <input
                  value={newIncident.title}
                  onChange={(e) => setNewIncident((current) => ({ ...current, title: e.target.value }))}
                  className="w-full rounded-lg border border-soc-border bg-soc-card px-3 py-2.5 text-sm text-white outline-none focus:border-cyber-cyan/60"
                  placeholder="Suspicious lateral movement"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-slate-300">Description</label>
                <textarea
                  value={newIncident.description}
                  onChange={(e) => setNewIncident((current) => ({ ...current, description: e.target.value }))}
                  className="h-28 w-full resize-none rounded-lg border border-soc-border bg-soc-card px-3 py-2.5 text-sm text-white outline-none focus:border-cyber-cyan/60"
                  placeholder="Describe the suspicious activity, scope, and impacted systems."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-2 block text-sm text-slate-300">Severity</label>
                  <select
                    value={newIncident.severity}
                    onChange={(e) => setNewIncident((current) => ({ ...current, severity: e.target.value as Severity }))}
                    className="w-full rounded-lg border border-soc-border bg-soc-card px-3 py-2.5 text-sm text-white focus:outline-none"
                  >
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm text-slate-300">Status</label>
                  <select
                    value={newIncident.status}
                    onChange={(e) => setNewIncident((current) => ({ ...current, status: e.target.value as Status }))}
                    className="w-full rounded-lg border border-soc-border bg-soc-card px-3 py-2.5 text-sm text-white focus:outline-none"
                  >
                    <option value="open">Open</option>
                    <option value="investigating">Investigating</option>
                    <option value="pending">Pending</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreateModal(false)} className="rounded-lg border border-soc-border bg-soc-card px-4 py-2 text-sm text-slate-300 hover:bg-soc-surface">
                  Cancel
                </button>
                <button type="submit" className="rounded-lg bg-gradient-to-r from-cyber-cyan to-cyber-blue px-4 py-2 text-sm font-medium text-white hover:opacity-90">
                  Save incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
