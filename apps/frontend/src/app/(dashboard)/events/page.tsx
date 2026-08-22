"use client";

import { useState } from "react";
import { DataTable } from "@/components/data-table";
import { SeverityBadge } from "@/components/severity-badge";
import { Search, Filter, Download, RefreshCw } from "lucide-react";
import type { SecurityEvent, Severity } from "@/lib/types";

const mockEvents: SecurityEvent[] = [
  { id: "EVT-001", timestamp: "2026-08-18T10:23:45Z", source_ip: "185.220.101.34", destination_ip: "10.0.1.52", source_port: 44231, destination_port: 22, event_type: "SSH Brute Force", severity: "critical", description: "Multiple failed SSH login attempts detected from external IP", raw_log: "", source: "WAF-01", user: "root", country: "Russia" },
  { id: "EVT-002", timestamp: "2026-08-18T10:21:12Z", source_ip: "10.0.1.52", destination_ip: "185.220.101.34", source_port: 22, destination_port: 44231, event_type: "Outbound Connection", severity: "high", description: "Suspicious outbound connection to known C2 server", raw_log: "", source: "EDR-03", user: "j.martinez", country: "Netherlands" },
  { id: "EVT-003", timestamp: "2026-08-18T10:18:33Z", source_ip: "10.0.2.15", destination_ip: "45.33.32.156", source_port: 52341, destination_port: 443, event_type: "Malware Download", severity: "critical", description: "Executable downloaded from known malware distribution site", raw_log: "", source: "AV-02", user: "s.chen", country: "US" },
  { id: "EVT-004", timestamp: "2026-08-18T10:15:07Z", source_ip: "10.0.3.88", destination_ip: "10.0.0.1", source_port: 38921, destination_port: 53, event_type: "DNS Query", severity: "medium", description: "DNS query to recently registered domain", raw_log: "", source: "DNS-01", user: "r.williams", country: "" },
  { id: "EVT-005", timestamp: "2026-08-18T10:12:44Z", source_ip: "10.0.1.120", destination_ip: "10.0.0.50", source_port: 445, destination_port: 445, event_type: "SMB Access", severity: "low", description: "Normal SMB file share access detected", raw_log: "", source: "FW-01", user: "admin", country: "" },
  { id: "EVT-006", timestamp: "2026-08-18T10:08:19Z", source_ip: "10.0.2.45", destination_ip: "52.96.123.45", source_port: 51234, destination_port: 587, event_type: "Email Outbound", severity: "info", description: "Email sent to external recipient via SMTP", raw_log: "", source: "EMAIL-01", user: "s.chen", country: "US" },
  { id: "EVT-007", timestamp: "2026-08-18T10:05:56Z", source_ip: "103.43.75.120", destination_ip: "10.0.1.52", source_port: 8080, destination_port: 8443, event_type: "Web Attack", severity: "critical", description: "SQL injection attempt detected in web application request", raw_log: "", source: "WAF-01", user: "", country: "China" },
  { id: "EVT-008", timestamp: "2026-08-18T10:02:11Z", source_ip: "10.0.1.33", destination_ip: "10.0.0.10", source_port: 5432, destination_port: 5432, event_type: "Database Query", severity: "info", description: "Large database query executed - potential data export", raw_log: "", source: "DB-01", user: "backup-svc", country: "" },
];

export default function EventsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
  const [page, setPage] = useState(1);

  const filteredEvents = mockEvents.filter((event) => {
    const matchesSearch =
      event.source_ip.includes(searchQuery) ||
      event.destination_ip.includes(searchQuery) ||
      event.event_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = severityFilter === "all" || event.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  const columns: Array<{
    key: string;
    header: string;
    render?: (item: SecurityEvent) => React.ReactNode;
  }> = [
    {
      key: "timestamp",
      header: "Time",
      render: (item: SecurityEvent) => (
        <span className="font-mono text-xs text-slate-400">
          {new Date(item.timestamp).toLocaleTimeString()}
        </span>
      ),
    },
    {
      key: "severity",
      header: "Severity",
      render: (item: SecurityEvent) => <SeverityBadge severity={item.severity} />,
    },
    {
      key: "event_type",
      header: "Type",
      render: (item: SecurityEvent) => (
        <span className="font-medium text-white">{item.event_type}</span>
      ),
    },
    {
      key: "source_ip",
      header: "Source IP",
      render: (item: SecurityEvent) => (
        <span className="font-mono text-xs text-cyber-cyan">{item.source_ip}:{item.source_port}</span>
      ),
    },
    {
      key: "destination_ip",
      header: "Destination",
      render: (item: SecurityEvent) => (
        <span className="font-mono text-xs text-slate-300">{item.destination_ip}:{item.destination_port}</span>
      ),
    },
    {
      key: "user",
      header: "User",
      render: (item: SecurityEvent) => (
        <span className="text-slate-300">{item.user || "-"}</span>
      ),
    },
    {
      key: "source",
      header: "Source",
      render: (item: SecurityEvent) => (
        <span className="text-xs text-slate-400 bg-soc-surface px-2 py-0.5 rounded">{item.source}</span>
      ),
    },
    {
      key: "description",
      header: "Description",
      render: (item: SecurityEvent) => (
        <span className="text-xs text-slate-400 max-w-xs truncate block">{item.description}</span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Security Events</h2>
          <p className="text-sm text-slate-400 mt-1">Monitor and analyze security events in real-time</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="inline-flex items-center gap-2 rounded-lg border border-soc-border bg-soc-card px-3 py-2 text-sm text-slate-300 hover:bg-soc-surface transition-colors">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button className="inline-flex items-center gap-2 rounded-lg border border-soc-border bg-soc-card px-3 py-2 text-sm text-slate-300 hover:bg-soc-surface transition-colors">
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search events by IP, type, or description..."
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
            <option value="info">Info</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns as any}
        data={filteredEvents}
        currentPage={page}
        totalPages={3}
        onPageChange={setPage}
      />
    </div>
  );
}
