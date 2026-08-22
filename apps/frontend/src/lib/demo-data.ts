/**
 * Offline fallback datasets.
 * Every page renders live API data when the backend is reachable and
 * transparently falls back to these when it is not (DEMO badge in the topbar).
 */
import type {
  Alert,
  Incident,
  MITRETechniqueEntry,
  SecurityEvent,
  Severity,
  ThreatIntelEntry,
} from "./types";

const SEVERITIES: Severity[] = ["critical", "high", "medium", "low", "info"];
const SOURCES = ["linux-syslog", "firewall", "windows-event", "edr-agent", "dns-server", "proxy", "waf", "vpn-gateway"];
const CATEGORIES = ["authentication", "network", "malware", "data_access", "privilege", "web", "email"];
const ACTIONS = [
  "login_failed", "login_success", "port_scan", "sudo", "file_encryption", "dns_query",
  "outbound_connection", "process_injection", "privilege_escalation", "policy_violation",
  "malware_detected", "data_exfiltration", "usb_connected", "firewall_block",
];
const USERS = ["admin", "analyst1", "j.martinez", "s.chen", "backup-svc", "root", "webapp", "svc-monitoring"];
const HOSTS = ["webserver-01", "db-primary", "dc-01", "wkstn-114", "fileserver-02", "k8s-node-3", "mail-relay"];
const APPS = ["ssh", "bash", "powershell.exe", "chrome.exe", "sqlplus", "curl", "scp", "rdp"];

let seed = 42;
function rand(): number {
  seed = (seed * 1103515245 + 12345) % 2147483648;
  return seed / 2147483648;
}
function pick<T>(arr: T[]): T {
  return arr[Math.floor(rand() * arr.length)];
}
function ip(): string {
  return `10.${Math.floor(rand() * 4)}.${Math.floor(rand() * 255)}.${Math.floor(rand() * 255)}`;
}
function minutesAgo(m: number): string {
  return new Date(Date.now() - m * 60_000).toISOString();
}

function buildEvents(count: number): SecurityEvent[] {
  return Array.from({ length: count }, (_, i) => {
    const sev = SEVERITIES[Math.min(4, Math.floor(rand() * 5.6))];
    return {
      id: `demo-evt-${i}`,
      event_id: `EVT-${(900000 + i).toString()}`,
      timestamp: minutesAgo(Math.floor(rand() * 7200)),
      source: pick(SOURCES),
      source_type: rand() > 0.5 ? "server" : "workstation",
      category: pick(CATEGORIES),
      action: pick(ACTIONS),
      user_name: rand() > 0.2 ? pick(USERS) : null,
      source_ip: ip(),
      destination_ip: ip(),
      destination_port: pick([22, 53, 80, 443, 445, 3389, 8080, 8443]),
      hostname: pick(HOSTS),
      application: rand() > 0.3 ? pick(APPS) : null,
      severity: sev,
      risk_score: Math.floor(rand() * 100),
      is_alert: sev === "critical" || sev === "high",
      raw_event: { demo: true, generator: "offline-mode" },
      tags: rand() > 0.7 ? ["auto-flagged"] : [],
    } satisfies SecurityEvent;
  });
}

const RULES = [
  { rule: "BRUTE-FORCE-001", title: "Brute Force Login Attempt", tactic: "Credential Access", technique: "T1110" },
  { rule: "PORT-SCAN-001", title: "Port Scan Detected", tactic: "Discovery", technique: "T1046" },
  { rule: "PRIV-ESC-001", title: "Privilege Escalation via Sudo", tactic: "Privilege Escalation", technique: "T1548" },
  { rule: "MAL-C2-001", title: "Malware C2 Beacon", tactic: "Command and Control", technique: "T1071" },
  { rule: "EXFIL-001", title: "Data Exfiltration Attempt", tactic: "Exfiltration", technique: "T1048" },
  { rule: "UNUSUAL-HOURS-001", title: "Unusual Hours Login", tactic: "Initial Access", technique: "T1078" },
  { rule: "POWERSHELL-001", title: "Suspicious PowerShell", tactic: "Execution", technique: "T1059" },
];

function buildAlerts(count: number): Alert[] {
  return Array.from({ length: count }, (_, i) => {
    const r = RULES[i % RULES.length];
    const sev = SEVERITIES[Math.min(4, Math.floor(rand() * 5.4))];
    return {
      id: `demo-alt-${i}`,
      alert_id: `ALT-${7850 - i}`,
      title: r.title,
      description: `${r.title} detected on ${pick(HOSTS)} — threshold exceeded in the configured window.`,
      rule_id: r.rule,
      severity: sev,
      status: (["new", "new", "acknowledged", "investigating", "resolved"] as const)[Math.floor(rand() * 5)],
      source: pick(SOURCES),
      rule_name: r.title,
      event_count: 3 + Math.floor(rand() * 40),
      first_seen: minutesAgo(Math.floor(rand() * 2880) + 30),
      last_seen: minutesAgo(Math.floor(rand() * 60)),
      source_ip: ip(),
      hostname: pick(HOSTS),
      user_name: pick(USERS),
      category: pick(CATEGORIES),
      risk_score: Math.floor(rand() * 100),
      mitre_tactic: r.tactic,
      mitre_technique: r.technique,
      created_at: minutesAgo(Math.floor(rand() * 2880)),
      updated_at: minutesAgo(Math.floor(rand() * 60)),
    } satisfies Alert;
  });
}

function buildIncidents(count: number): Incident[] {
  const titles = [
    "Coordinated Brute Force Campaign",
    "Ransomware Precursor Behaviour",
    "Credential Dumping Suspected",
    "Data Staging on File Server",
    "C2 Channel Confirmation",
    "Lateral Movement via RDP",
    "Privileged Account Abuse",
    "Suspicious DNS Tunnelling",
  ];
  return Array.from({ length: count }, (_, i) => ({
    id: `demo-inc-${i}`,
    incident_id: `INC-${2026}-${(101 + i).toString().padStart(4, "0")}`,
    title: titles[i % titles.length],
    description: "Multiple correlated alerts escalated automatically by the correlation engine.",
    severity: SEVERITIES[Math.min(4, Math.floor(rand() * 4.4))],
    status: (["open", "investigating", "contained", "resolved", "closed"] as const)[Math.floor(rand() * 5)],
    source: pick(["detection-engine", "analyst", "ti-feed", "soc-auto"]),
    risk_score: Math.floor(rand() * 100),
    assigned_to: null,
    tags: ["auto-generated"],
    created_at: minutesAgo(Math.floor(rand() * 8640)),
    updated_at: minutesAgo(Math.floor(rand() * 240)),
  })) satisfies Incident[];
}

function buildThreatIntel(): ThreatIntelEntry[] {
  const rows: Array<[string, string, string, string]> = [
    ["185.220.101.34", "ip", "Tor Exit Node", "Scanning / Brute force origin"],
    ["103.43.75.120", "ip", "Botnet C2", "Emotet C2 infrastructure"],
    ["d3fc0de1.example.ru", "domain", "Phishing", "Credential harvesting kit"],
    ["e05b1e2a7f3c9d8b", "hash", "Ransomware", "LockBit 3.0 sample SHA-256"],
    ["45.155.205.233", "ip", "Proxy Abuse", "Anonymisation service"],
    ["update-svc.example.top", "domain", "Malware Distribution", "Fake update portal"],
    ["194.26.29.123", "ip", "Bulletproof Hosting", "DDoS and scan origin"],
    ["7f3a9c8b2d1e4f5a", "hash", "Trojan", "RAT dropper (Quakbot)"],
  ];
  return rows.map(([value, type, threat, description], i) => ({
    id: `demo-ti-${i}`,
    indicator_type: type,
    indicator_value: value,
    threat_type: threat,
    severity: SEVERITIES[Math.min(4, i % 4)],
    confidence: 55 + Math.floor(rand() * 45),
    source: pick(["misp", "abuse.ch", "otx", "internal"],
    ),
    description,
    is_active: true,
    created_at: minutesAgo(Math.floor(rand() * 10000)),
  })) satisfies ThreatIntelEntry[];
}

function buildMitre(): MITRETechniqueEntry[] {
  const data: Array<[string, string, string]> = [
    ["T1566", "Phishing", "Initial Access"],
    ["T1078", "Valid Accounts", "Initial Access"],
    ["T1110", "Brute Force", "Credential Access"],
    ["T1003", "OS Credential Dumping", "Credential Access"],
    ["T1059", "Command and Scripting Interpreter", "Execution"],
    ["T1204", "User Execution", "Execution"],
    ["T1053", "Scheduled Task/Job", "Execution"],
    ["T1548", "Abuse Elevation Control Mechanism", "Privilege Escalation"],
    ["T1068", "Exploitation for Privilege Escalation", "Privilege Escalation"],
    ["T1046", "Network Service Discovery", "Discovery"],
    ["T1087", "Account Discovery", "Discovery"],
    ["T1021", "Remote Services", "Lateral Movement"],
    ["T1550", "Use of Alternate Authentication Material", "Lateral Movement"],
    ["T1005", "Data from Local System", "Collection"],
    ["T1074", "Data Staged", "Collection"],
    ["T1560", "Archive Collected Data", "Collection"],
    ["T1048", "Exfiltration Over Alternative Protocol", "Exfiltration"],
    ["T1041", "Exfiltration Over C2 Channel", "Exfiltration"],
    ["T1071", "Application Layer Protocol", "Command and Control"],
    ["T1573", "Encrypted Channel", "Command and Control"],
    ["T1486", "Data Encrypted for Impact", "Impact"],
    ["T1490", "Inhibit System Recovery", "Impact"],
  ];
  return data.map(([id, name, tactic], i) => ({
    id: `demo-mitre-${i}`,
    technique_id: id,
    name,
    tactic,
    description: `MITRE ATT&CK technique ${id} (${name}) under the ${tactic} tactic.`,
    platform: ["Windows", "Linux", "macOS"],
  }));
}

export const demoData = {
  events: buildEvents(120),
  alerts: buildAlerts(36),
  incidents: buildIncidents(9),
  threatIntel: buildThreatIntel(),
  mitre: buildMitre(),
};

export function demoAIReply(message: string): string {
  const m = message.toLowerCase();
  if (m.includes("brute")) {
    return "Brute-force analysis: 23 failed logins from 185.220.101.34 in 8 minutes against sshd on webserver-01. Pattern matches T1110 (Password Guessing). Recommended: block source IP at perimeter, rotate targeted credentials, review successful logins from the same ASN in the last 24h.";
  }
  if (m.includes("exfil") || m.includes("data")) {
    return "Exfiltration check: outbound volume from fileserver-02 is 4.7x baseline (2.3 GB over port 443 to a newly registered domain). Behaviour aligns with T1048. Recommended: isolate host, capture PCAP, verify DLP alerts and check for archive staging (T1074/T1560).";
  }
  if (m.includes("incident") || m.includes("summar")) {
    return "Incident summary: the correlation engine grouped 14 alerts (brute force + privilege escalation + C2 beacon) into INC-2026-0104. Confidence 0.87. The kill chain suggests initial access via valid accounts followed by discovery and staging. Recommended actions: contain db-primary, reset svc-backup credentials, hunt for T1021 lateral movement.";
  }
  if (m.includes("mitre")) {
    return "MITRE view: current activity clusters around Credential Access (T1110), Privilege Escalation (T1548) and Command and Control (T1071). Coverage gaps detected for T1550 (pass-the-hash) — consider adding a detection rule.";
  }
  return "Analysis complete. I correlated your request against the last 24h of events: no additional anomalies beyond the currently open incidents. Ask me about 'brute force', 'exfiltration', 'incident summary' or 'MITRE' for a deep-dive.";
}
