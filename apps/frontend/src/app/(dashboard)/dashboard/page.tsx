"use client";

import { StatsCard } from "@/components/stats-card";
import { AlertChart } from "@/components/alert-chart";
import { SeverityBadge } from "@/components/severity-badge";
import { Activity, AlertTriangle, Shield, Zap, ExternalLink } from "lucide-react";

const stats = [
  { title: "Total Events (24h)", value: 284593, change: 12.5, icon: Activity, iconColor: "text-cyber-cyan" },
  { title: "Critical Alerts", value: 23, change: -8.3, icon: AlertTriangle, iconColor: "text-cyber-red" },
  { title: "Open Incidents", value: 7, change: 16.7, icon: Shield, iconColor: "text-cyber-orange" },
  { title: "Active Threats", value: 4, change: -33.3, icon: Zap, iconColor: "text-cyber-purple" },
];

const eventsByHour = [
  { hour: "00:00", count: 8200, critical: 2, high: 8, medium: 45 },
  { hour: "01:00", count: 6500, critical: 1, high: 5, medium: 32 },
  { hour: "02:00", count: 4800, critical: 0, high: 3, medium: 22 },
  { hour: "03:00", count: 3200, critical: 0, high: 2, medium: 15 },
  { hour: "04:00", count: 2800, critical: 0, high: 1, medium: 12 },
  { hour: "05:00", count: 3500, critical: 1, high: 4, medium: 18 },
  { hour: "06:00", count: 7200, critical: 2, high: 9, medium: 42 },
  { hour: "07:00", count: 12500, critical: 3, high: 15, medium: 68 },
  { hour: "08:00", count: 18900, critical: 5, high: 28, medium: 95 },
  { hour: "09:00", count: 22100, critical: 4, high: 22, medium: 88 },
  { hour: "10:00", count: 24500, critical: 3, high: 18, medium: 76 },
  { hour: "11:00", count: 21800, critical: 2, high: 16, medium: 72 },
  { hour: "12:00", count: 15200, critical: 1, high: 10, medium: 48 },
  { hour: "13:00", count: 19800, critical: 3, high: 20, medium: 82 },
  { hour: "14:00", count: 23400, critical: 4, high: 24, medium: 90 },
  { hour: "15:00", count: 21200, critical: 2, high: 18, medium: 78 },
  { hour: "16:00", count: 18600, critical: 1, high: 14, medium: 65 },
  { hour: "17:00", count: 14200, critical: 1, high: 10, medium: 52 },
  { hour: "18:00", count: 10800, critical: 0, high: 8, medium: 38 },
  { hour: "19:00", count: 8900, critical: 0, high: 6, medium: 30 },
  { hour: "20:00", count: 7200, critical: 1, high: 5, medium: 25 },
  { hour: "21:00", count: 6100, critical: 0, high: 4, medium: 20 },
  { hour: "22:00", count: 5400, critical: 0, high: 3, medium: 18 },
  { hour: "23:00", count: 4800, critical: 1, high: 3, medium: 15 },
];

const alertsBySeverity = [
  { severity: "Critical", count: 23, fill: "#ef4444" },
  { severity: "High", count: 87, fill: "#f59e0b" },
  { severity: "Medium", count: 234, fill: "#3b82f6" },
  { severity: "Low", count: 456, fill: "#10b981" },
  { severity: "Info", count: 892, fill: "#64748b" },
];

const topAttackerIPs = [
  { ip: "185.220.101.34", country: "Russia", attacks: 1247, last_seen: "2 min ago", status: "active" },
  { ip: "103.43.75.120", country: "China", attacks: 892, last_seen: "5 min ago", status: "blocked" },
  { ip: "45.155.205.233", country: "Netherlands", attacks: 634, last_seen: "12 min ago", status: "monitoring" },
  { ip: "194.26.29.123", country: "Ukraine", attacks: 421, last_seen: "18 min ago", status: "blocked" },
  { ip: "91.134.203.58", country: "France", attacks: 287, last_seen: "25 min ago", status: "monitoring" },
];

const topTargetedUsers = [
  { username: "j.martinez", department: "Engineering", alerts: 34, risk_score: 87 },
  { username: "admin", department: "IT Admin", alerts: 28, risk_score: 92 },
  { username: "s.chen", department: "Finance", alerts: 19, risk_score: 65 },
  { username: "r.williams", department: "HR", alerts: 15, risk_score: 54 },
  { username: "backup-svc", department: "Operations", alerts: 12, risk_score: 71 },
];

const recentAlerts = [
  { id: "ALT-7842", title: "Brute Force Attack Detected", severity: "critical" as const, time: "2 min ago", source: "WAF-01" },
  { id: "ALT-7841", title: "Suspicious Outbound Connection", severity: "high" as const, time: "8 min ago", source: "EDR-03" },
  { id: "ALT-7840", title: "Malware Signature Match", severity: "critical" as const, time: "15 min ago", source: "AV-02" },
  { id: "ALT-7839", title: "Anomalous Login Pattern", severity: "medium" as const, time: "22 min ago", source: "IAM-01" },
  { id: "ALT-7838", title: "Data Exfiltration Attempt", severity: "high" as const, time: "35 min ago", source: "DLP-01" },
  { id: "ALT-7837", title: "Privilege Escalation Detected", severity: "critical" as const, time: "41 min ago", source: "SIEM-01" },
  { id: "ALT-7836", title: "Unauthorized USB Device", severity: "low" as const, time: "1 hr ago", source: "EDR-01" },
];

const actorConnections = [
  { name: "SOC Analyst", role: "Incident Lead", status: "online", nodes: ["SIEM", "EDR", "IAM"] },
  { name: "Firewall", role: "Perimeter Gate", status: "online", nodes: ["WAF", "VPN", "Proxy"] },
  { name: "EDR Cluster", role: "Endpoint Defense", status: "degraded", nodes: ["Laptop", "Server", "Workstation"] },
  { name: "IAM", role: "Identity Access", status: "online", nodes: ["AD", "Okta", "VPN"] },
];

export default function DashboardPage() {
  const maxSeverityCount = Math.max(...alertsBySeverity.map((item) => item.count));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <StatsCard key={stat.title} {...stat} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AlertChart data={eventsByHour} />
        </div>
        <div className="card-glow rounded-xl p-5">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Alerts by Severity</h3>
          <div className="flex h-[300px] items-end gap-3 rounded-lg border border-soc-border/60 bg-soc-bg/30 p-4">
            {alertsBySeverity.map((item) => (
              <div key={item.severity} className="group flex h-full flex-1 flex-col justify-end gap-2">
                <div className="relative flex flex-1 items-end">
                  <div
                    className="w-full rounded-t-md transition-all duration-150 group-hover:brightness-125"
                    style={{
                      height: `${Math.max(12, (item.count / maxSeverityCount) * 100)}%`,
                      backgroundColor: item.fill,
                    }}
                  />
                  <div className="pointer-events-none absolute bottom-full left-1/2 mb-2 hidden -translate-x-1/2 rounded-lg border border-soc-border bg-soc-card px-3 py-2 text-xs shadow-xl group-hover:block">
                    <p className="font-medium text-white">{item.severity}</p>
                    <p className="text-slate-400">{item.count.toLocaleString()} alerts</p>
                  </div>
                </div>
                <span className="truncate text-center text-xs text-slate-500">{item.severity}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card-glow rounded-xl p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-400">Threat Map</h3>
            <button type="button" className="flex items-center gap-1 text-xs text-cyber-cyan transition-colors hover:text-cyber-cyan/80">
              View All <ExternalLink className="h-3 w-3" />
            </button>
          </div>
          <div className="relative h-[260px] overflow-hidden rounded-xl border border-soc-border/60 bg-[#081827]/80">
            <div className="absolute inset-0 opacity-50" style={{ background: "radial-gradient(circle at center, rgba(59,130,246,0.14), transparent 55%)" }} />
            <svg viewBox="0 0 600 260" className="relative h-full w-full">
              <path d="M90 120 C160 70, 210 70, 270 115 S380 180, 470 120 S560 90, 580 120" fill="none" stroke="rgba(148,163,184,0.22)" strokeWidth="2" />
              <path d="M120 170 C200 150, 250 170, 320 140 S430 100, 510 145" fill="none" stroke="rgba(148,163,184,0.14)" strokeWidth="2" />
              <circle cx="150" cy="110" r="8" fill="#ef4444" opacity="0.9" />
              <circle cx="310" cy="142" r="9" fill="#f59e0b" opacity="0.9" />
              <circle cx="430" cy="118" r="10" fill="#3b82f6" opacity="0.9" />
              <circle cx="492" cy="150" r="7" fill="#ef4444" opacity="0.9" />
              <circle cx="228" cy="160" r="6" fill="#10b981" opacity="0.9" />
              <g fill="#dbeafe" fontSize="10" fontWeight="600">
                <text x="136" y="92">EU</text>
                <text x="292" y="124">US</text>
                <text x="414" y="100">APAC</text>
                <text x="476" y="170">LATAM</text>
              </g>
            </svg>
            <div className="absolute bottom-4 left-4 rounded-lg border border-soc-border bg-soc-card/90 px-3 py-2 shadow-lg shadow-black/20">
              <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Risk zones</p>
              <p className="mt-1 text-sm font-medium text-white">4 high-risk countries</p>
            </div>
          </div>
        </div>

        <div className="card-glow rounded-xl p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-400">Actor Connections</h3>
            <button type="button" className="flex items-center gap-1 text-xs text-cyber-cyan transition-colors hover:text-cyber-cyan/80">
              View All <ExternalLink className="h-3 w-3" />
            </button>
          </div>
          <div className="space-y-3">
            {actorConnections.map((actor) => (
              <div key={actor.name} className="rounded-xl border border-soc-border/60 bg-soc-surface/20 p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-white">{actor.name}</p>
                    <p className="text-xs text-slate-400">{actor.role}</p>
                  </div>
                  <span className={`rounded-full px-2 py-1 text-[10px] font-medium uppercase tracking-wide ${
                    actor.status === "online" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  }`}>
                    {actor.status}
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {actor.nodes.map((node) => (
                    <span key={node} className="inline-flex rounded-full border border-soc-border bg-soc-card px-2 py-1 text-[10px] text-slate-300">
                      {node}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card-glow rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-400">Top Attacker IPs</h3>
            <button type="button" className="text-xs text-cyber-cyan hover:text-cyber-cyan/80 flex items-center gap-1 transition-colors">
              View All <ExternalLink className="h-3 w-3" />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-soc-border">
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">IP Address</th>
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">Country</th>
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">Attacks</th>
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-soc-border/50">
                {topAttackerIPs.map((ip) => (
                  <tr key={ip.ip} className="hover:bg-soc-surface/30 transition-colors">
                    <td className="py-2.5 text-sm font-mono text-cyber-cyan">{ip.ip}</td>
                    <td className="py-2.5 text-sm text-slate-300">{ip.country}</td>
                    <td className="py-2.5 text-sm font-medium text-white">{ip.attacks.toLocaleString()}</td>
                    <td className="py-2.5">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        ip.status === "active"
                          ? "bg-cyber-red/10 text-cyber-red border border-cyber-red/20"
                          : ip.status === "blocked"
                          ? "bg-slate-500/10 text-slate-400 border border-slate-500/20"
                          : "bg-cyber-orange/10 text-cyber-orange border border-cyber-orange/20"
                      }`}>
                        {ip.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card-glow rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-400">Top Targeted Users</h3>
            <button type="button" className="text-xs text-cyber-cyan hover:text-cyber-cyan/80 flex items-center gap-1 transition-colors">
              View All <ExternalLink className="h-3 w-3" />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-soc-border">
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">User</th>
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">Department</th>
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">Alerts</th>
                  <th className="pb-2 text-left text-xs font-medium text-slate-500">Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-soc-border/50">
                {topTargetedUsers.map((user) => (
                  <tr key={user.username} className="hover:bg-soc-surface/30 transition-colors">
                    <td className="py-2.5 text-sm font-medium text-white">{user.username}</td>
                    <td className="py-2.5 text-sm text-slate-400">{user.department}</td>
                    <td className="py-2.5 text-sm text-slate-300">{user.alerts}</td>
                    <td className="py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 rounded-full bg-soc-surface overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              user.risk_score >= 80 ? "bg-cyber-red" : user.risk_score >= 60 ? "bg-cyber-orange" : "bg-cyber-green"
                            }`}
                            style={{ width: `${user.risk_score}%` }}
                          />
                        </div>
                        <span className={`text-xs font-medium ${
                          user.risk_score >= 80 ? "text-cyber-red" : user.risk_score >= 60 ? "text-cyber-orange" : "text-cyber-green"
                        }`}>
                          {user.risk_score}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="card-glow rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-slate-400">Recent Alerts</h3>
          <button type="button" className="text-xs text-cyber-cyan hover:text-cyber-cyan/80 flex items-center gap-1 transition-colors">
            View All <ExternalLink className="h-3 w-3" />
          </button>
        </div>
        <div className="space-y-2">
          {recentAlerts.map((alert) => (
            <div
              key={alert.id}
              className="flex items-center justify-between rounded-lg border border-soc-border/50 bg-soc-surface/30 px-4 py-3 hover:bg-soc-surface/60 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-4">
                <SeverityBadge severity={alert.severity} />
                <div>
                  <p className="text-sm font-medium text-white">{alert.title}</p>
                  <p className="text-xs text-slate-500">{alert.id} - {alert.source}</p>
                </div>
              </div>
              <span className="text-xs text-slate-500">{alert.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
