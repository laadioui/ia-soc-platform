"use client";

import { useState } from "react";
import { Search, Filter, Clock, MapPin, User, Server, ArrowRight, Download } from "lucide-react";
import { SeverityBadge } from "@/components/severity-badge";

function escapePdfText(value: string) {
  return value.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)").replace(/\r?\n/g, " ");
}

function buildPdfReport(report: string) {
  const lines = report.split("\n");
  const content = lines
    .map((line, index) => `BT\n/F1 11 Tf\n50 ${760 - index * 16} Td\n(${escapePdfText(line)}) Tj\nET`)
    .join("\n");

  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    `<< /Length ${content.length} >>\nstream\n${content}\nendstream`,
  ];

  let pdf = "%PDF-1.4\n";
  const offsets: number[] = [0];

  objects.forEach((object, index) => {
    offsets.push(pdf.length);
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });

  const xrefPos = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += `0000000000 65535 f \n`;

  for (let i = 1; i <= objects.length; i += 1) {
    pdf += `${String(offsets[i]).padStart(10, "0")} 00000 n \n`;
  }

  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefPos}\n%%EOF`;

  return new Blob([pdf], { type: "application/pdf" });
}

const timelineEvents = [
  { time: "10:23:45", event: "SSH brute force detected", source: "WAF-01", severity: "critical" as const, details: "500+ failed attempts from 185.220.101.34" },
  { time: "10:25:12", event: "Firewall rule updated", source: "FW-01", severity: "info" as const, details: "Auto-blocked attacker IP at perimeter" },
  { time: "10:28:33", event: "Lateral movement detected", source: "EDR-03", severity: "high" as const, details: "Compromised host 10.0.1.52 scanning internal network" },
  { time: "10:30:01", event: "Suspicious process spawned", source: "EDR-01", severity: "high" as const, details: "Reverse shell connection to 45.33.32.156:4444" },
  { time: "10:32:15", event: "Credential dump attempt", source: "SIEM-01", severity: "critical" as const, details: "LSASS memory access detected on PROD-WEB-01" },
  { time: "10:35:00", event: "Data staging detected", source: "DLP-01", severity: "high" as const, details: "Archived files created in /tmp/.cache/" },
  { time: "10:38:22", event: "Outbound transfer initiated", source: "FW-01", severity: "critical" as const, details: "2.1 GB encrypted transfer to external IP" },
];

const evidence = [
  { id: "EV-001", type: "Log", name: "auth.log extraction", size: "45 MB", timestamp: "10:40:00" },
  { id: "EV-002", type: "Memory", name: "PROD-WEB-01 memory dump", size: "8.2 GB", timestamp: "10:42:00" },
  { id: "EV-003", type: "PCAP", name: "Network capture analysis", size: "1.2 GB", timestamp: "10:45:00" },
  { id: "EV-004", type: "Binary", name: "Malware sample extracted", size: "245 KB", timestamp: "10:48:00" },
];

export default function InvestigationPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"timeline" | "evidence" | "notes">("timeline");

  const exportReport = () => {
    const generatedAt = new Date().toLocaleString();
    const report = [
      "SOC Investigation Report",
      "========================",
      "",
      `Investigation: INC-0042`,
      `Generated: ${generatedAt}`,
      "Analyst: j.martinez",
      "Risk Score: 87",
      "Attack Pattern: Credential Stuffing + Lateral Movement",
      "",
      "Executive Summary",
      "-----------------",
      "A critical intrusion sequence was detected involving brute-force access, lateral movement, credential dumping, data staging, and outbound exfiltration.",
      "",
      "Attack Timeline",
      "---------------",
      ...timelineEvents.map(
        (event) =>
          `${event.time} | ${event.severity.toUpperCase()} | ${event.source} | ${event.event} | ${event.details}`
      ),
      "",
      "Evidence",
      "--------",
      ...evidence.map(
        (item) => `${item.id} | ${item.type} | ${item.name} | ${item.size} | Collected at ${item.timestamp}`
      ),
      "",
      "Recommended Next Steps",
      "----------------------",
      "- Complete forensic imaging of affected systems.",
      "- Rotate credentials and audit privileged accounts.",
      "- Block related IOCs at perimeter and endpoint controls.",
      "- Review outbound transfer logs for data exposure scope.",
    ].join("\n");

    const blob = buildPdfReport(report);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `INC-0042-investigation-report-${new Date().toISOString().slice(0, 10)}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Investigation Workspace</h2>
          <p className="text-sm text-slate-400 mt-1">Deep-dive analysis and forensic investigation tools</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={exportReport}
            className="inline-flex items-center gap-2 rounded-lg border border-soc-border bg-soc-card px-3 py-2 text-sm text-slate-300 hover:bg-soc-surface transition-colors"
          >
            <Download className="h-4 w-4" />
            Export Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div className="card-glow rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyber-red/10">
              <Search className="h-5 w-5 text-cyber-red" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Active Investigation</p>
              <p className="text-lg font-bold text-white">INC-0042</p>
            </div>
          </div>
        </div>
        <div className="card-glow rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyber-orange/10">
              <Clock className="h-5 w-5 text-cyber-orange" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Time Elapsed</p>
              <p className="text-lg font-bold text-white">2h 15m</p>
            </div>
          </div>
        </div>
        <div className="card-glow rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyber-cyan/10">
              <Server className="h-5 w-5 text-cyber-cyan" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Affected Systems</p>
              <p className="text-lg font-bold text-white">5</p>
            </div>
          </div>
        </div>
        <div className="card-glow rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyber-green/10">
              <User className="h-5 w-5 text-cyber-green" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Analyst</p>
              <p className="text-lg font-bold text-white">j.martinez</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1 border-b border-soc-border">
        {(["timeline", "evidence", "notes"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 text-sm font-medium capitalize transition-colors border-b-2 ${
              activeTab === tab
                ? "border-cyber-cyan text-cyber-cyan"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "timeline" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 card-glow rounded-xl p-5">
            <h3 className="text-sm font-medium text-slate-400 mb-4">Attack Timeline</h3>
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-px bg-soc-border" />
              <div className="space-y-4">
                {timelineEvents.map((event, idx) => (
                  <div key={idx} className="relative flex gap-4 pl-10">
                    <div className={`absolute left-2.5 top-1 h-3 w-3 rounded-full border-2 border-soc-card ${
                      event.severity === "critical" ? "bg-cyber-red" :
                      event.severity === "high" ? "bg-cyber-orange" : "bg-cyber-cyan"
                    }`} />
                    <div className="flex-1 rounded-lg border border-soc-border/50 bg-soc-surface/30 p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs text-slate-500">{event.time}</span>
                          <SeverityBadge severity={event.severity} />
                          <span className="text-sm font-medium text-white">{event.event}</span>
                        </div>
                        <span className="text-xs text-slate-500">{event.source}</span>
                      </div>
                      <p className="text-sm text-slate-400 mt-1">{event.details}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="card-glow rounded-xl p-5">
            <h3 className="text-sm font-medium text-slate-400 mb-4">Quick Analysis</h3>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-slate-500 mb-2">Attack Pattern</p>
                <div className="rounded-lg bg-soc-surface p-3">
                  <p className="text-sm text-white font-medium">Credential Stuffing + Lateral Movement</p>
                  <p className="text-xs text-slate-400 mt-1">Matches APT-41 variant TTPs</p>
                </div>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-2">Kill Chain Phase</p>
                <div className="flex flex-wrap gap-2">
                  {["Initial Access", "Execution", "Persistence", "Credential Access", "Lateral Movement", "Exfiltration"].map((phase) => (
                    <span key={phase} className="inline-flex items-center rounded-md bg-cyber-purple/10 px-2 py-1 text-xs text-cyber-purple border border-cyber-purple/20">
                      {phase}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-2">Risk Score</p>
                <div className="flex items-center gap-3">
                  <div className="h-2 flex-1 rounded-full bg-soc-surface overflow-hidden">
                    <div className="h-full rounded-full bg-cyber-red" style={{ width: "87%" }} />
                  </div>
                  <span className="text-lg font-bold text-cyber-red">87</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "evidence" && (
        <div className="card-glow rounded-xl p-5">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Evidence Collection</h3>
          <div className="space-y-3">
            {evidence.map((ev) => (
              <div key={ev.id} className="flex items-center justify-between rounded-lg border border-soc-border/50 bg-soc-surface/30 p-4 hover:bg-soc-surface/60 transition-colors">
                <div className="flex items-center gap-4">
                  <span className="inline-flex items-center rounded-md bg-cyber-blue/10 px-2.5 py-1 text-xs font-medium text-cyber-blue border border-cyber-blue/20">
                    {ev.type}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-white">{ev.name}</p>
                    <p className="text-xs text-slate-500">{ev.size} - Collected at {ev.timestamp}</p>
                  </div>
                </div>
                <button className="text-xs text-cyber-cyan hover:text-cyber-cyan/80 transition-colors">Download</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "notes" && (
        <div className="card-glow rounded-xl p-5">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Investigation Notes</h3>
          <textarea
            className="w-full h-64 rounded-lg border border-soc-border bg-soc-surface p-4 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyber-cyan/50 focus:ring-1 focus:ring-cyber-cyan/20 resize-none transition-colors"
            placeholder="Add investigation notes here..."
            defaultValue={`## Investigation Notes - INC-0042

### Initial Findings (10:45 AM)
- Attacker used Tor exit node 185.220.101.34
- Brute force targeted root, admin, and deploy users
- Successful login on PROD-WEB-01 using deploy:deploy123

### Lateral Movement (11:00 AM)
- From PROD-WEB-01, attacker pivoted to PROD-APP-03
- Used stolen SSH keys for authentication
- Created backdoor user "svc-update" with sudo privileges

### Next Steps
- [ ] Complete forensic image of PROD-WEB-01
- [ ] Analyze memory dump for injection artifacts
- [ ] Check all systems for the "svc-update" account
- [ ] Review VPN logs for any related activity`}
          />
        </div>
      )}
    </div>
  );
}
