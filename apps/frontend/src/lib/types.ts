export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type Status = "open" | "investigating" | "resolved" | "closed" | "pending";

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
}

export interface SecurityEvent {
  id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  event_type: string;
  severity: Severity;
  description: string;
  raw_log: string;
  source: string;
  user?: string;
  country?: string;
}

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: Status;
  created_at: string;
  updated_at: string;
  source: string;
  event_ids: string[];
  assigned_to?: string;
  mitre_tactic?: string;
  mitre_technique?: string;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: Status;
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  alert_ids: string[];
  event_ids: string[];
  timeline: TimelineEntry[];
  iocs: IOC[];
  ai_analysis?: string;
}

export interface TimelineEntry {
  id: string;
  timestamp: string;
  action: string;
  user: string;
  details: string;
}

export interface IOC {
  id: string;
  type: "ip" | "domain" | "hash" | "url" | "email";
  value: string;
  confidence: number;
  first_seen: string;
  last_seen: string;
  tags: string[];
}

export interface ThreatIntel {
  id: string;
  title: string;
  description: string;
  type: string;
  severity: Severity;
  source: string;
  published: string;
  tags: string[];
  iocs: IOC[];
  url?: string;
}

export interface MITRETactic {
  id: string;
  name: string;
  description: string;
  techniques: MITRETechnique[];
}

export interface MITRETechnique {
  id: string;
  tactic: string;
  name: string;
  description: string;
  detection: string;
  alert_count: number;
  status: "active" | "mitigated" | "none";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface DashboardStats {
  total_events: number;
  critical_alerts: number;
  open_incidents: number;
  active_threats: number;
  events_trend: number;
  alerts_trend: number;
  incidents_trend: number;
  threats_trend: number;
}

export interface EventsByHour {
  hour: string;
  count: number;
  critical: number;
  high: number;
  medium: number;
}

export interface AlertsBySeverity {
  severity: string;
  count: number;
  fill: string;
}

export interface AttackerIP {
  ip: string;
  country: string;
  attacks: number;
  last_seen: string;
  status: "active" | "blocked" | "monitoring";
}

export interface TargetedUser {
  username: string;
  department: string;
  alerts: number;
  risk_score: number;
}

export interface Settings {
  general: {
    org_name: string;
    timezone: string;
    language: string;
  };
  notifications: {
    email_enabled: boolean;
    slack_enabled: boolean;
    critical_only: boolean;
  };
  retention: {
    events_days: number;
    alerts_days: number;
    incidents_days: number;
  };
}
