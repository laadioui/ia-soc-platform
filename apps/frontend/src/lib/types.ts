export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type AlertStatus = "new" | "acknowledged" | "investigating" | "resolved" | "closed" | "pending";
export type IncidentStatus = "open" | "investigating" | "contained" | "resolved" | "closed" | "pending";

export interface SecurityEvent {
  id: string;
  event_id: string;
  timestamp: string;
  source: string;
  source_type: string;
  category: string;
  action: string;
  user_name?: string | null;
  source_ip?: string | null;
  destination_ip?: string | null;
  destination_port?: number | null;
  hostname?: string | null;
  application?: string | null;
  severity: Severity;
  risk_score?: number | null;
  is_alert?: boolean;
  raw_event?: Record<string, unknown> | null;
  tags?: string[] | null;
}

export interface Alert {
  id: string;
  alert_id: string;
  title?: string | null;
  description?: string | null;
  rule_id?: string | null;
  severity: Severity;
  status: AlertStatus;
  source?: string | null;
  rule_name?: string | null;
  event_count?: number;
  first_seen?: string;
  last_seen?: string;
  source_ip?: string | null;
  hostname?: string | null;
  user_name?: string | null;
  category?: string | null;
  risk_score?: number | null;
  mitre_tactic?: string | null;
  mitre_technique?: string | null;
  created_at: string;
  updated_at?: string;
}

export function extractIp(text?: string | null): string | null {
  if (!text) return null;
  return text.match(/\b(\d{1,3}(?:\.\d{1,3}){3})\b/)?.[0] ?? null;
}

export interface Incident {
  id: string;
  incident_id: string;
  title: string;
  description?: string | null;
  severity: Severity;
  status: IncidentStatus;
  source?: string | null;
  risk_score?: number | null;
  assigned_to?: string | null;
  tags?: string[] | null;
  created_at: string;
  updated_at?: string;
}

export interface ThreatIntelEntry {
  id: string;
  indicator_type?: string;
  indicator_value: string;
  threat_type?: string | null;
  severity?: Severity | null;
  confidence?: number | null;
  source?: string | null;
  description?: string | null;
  is_active?: boolean;
  created_at?: string;
}

export interface MITRETechniqueEntry {
  id: string;
  technique_id: string;
  name: string;
  tactic: string;
  description?: string | null;
  platform?: string[] | null;
}

export interface Paged<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface AIAnalyzeResult {
  response: string;
  confidence?: number | null;
  model_used?: string | null;
  context_sources?: string[];
}

export interface AISummaryResult {
  summary: string;
  key_findings: string[];
  risk_assessment: string;
  recommended_actions: string[];
  mitre_techniques: string[];
  confidence: number;
}
