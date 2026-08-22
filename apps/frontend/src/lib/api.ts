"use client";

import type {
  AIAnalyzeResult,
  AISummaryResult,
  Alert,
  AlertStatus,
  Incident,
  IncidentStatus,
  MITRETechniqueEntry,
  Paged,
  SecurityEvent,
  ThreatIntelEntry,
} from "./types";

const SETTINGS_KEY = "soc-settings";

export interface SocSettings {
  apiUrl: string;
  refreshSeconds: number;
  demoMode: boolean;
}

export const defaultSettings: SocSettings = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  refreshSeconds: 30,
  demoMode: false,
};

export function loadSettings(): SocSettings {
  if (typeof window === "undefined") return defaultSettings;
  try {
    const stored = JSON.parse(window.localStorage.getItem(SETTINGS_KEY) || "{}");
    const merged = { ...defaultSettings, ...stored };
    if (!merged.apiUrl || !merged.apiUrl.trim()) merged.apiUrl = defaultSettings.apiUrl;
    return merged;
  } catch {
    return defaultSettings;
  }
}

export function saveSettings(s: SocSettings) {
  window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const base = (loadSettings().apiUrl || defaultSettings.apiUrl).replace(/\/$/, "");
  const res = await fetch(`${base}${endpoint}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export type DataSource = "live" | "demo";
export interface FetchResult<T> {
  data: T;
  source: DataSource;
}

function pagedParams(params?: Record<string, string | number | undefined>): string {
  if (!params) return "";
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") q.set(k, String(v));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

export const api = {
  async events(params?: Record<string, string | number | undefined>): Promise<Paged<SecurityEvent>> {
    const d = await fetchAPI<{ events: SecurityEvent[]; total: number; page: number; page_size: number }>(
      `/events/${pagedParams(params)}`
    );
    return { items: d.events ?? [], total: d.total, page: d.page, page_size: d.page_size };
  },
  async alerts(params?: Record<string, string | number | undefined>): Promise<Paged<Alert>> {
    const d = await fetchAPI<{ alerts: Alert[]; total: number; page: number; page_size: number }>(
      `/alerts/${pagedParams(params)}`
    );
    return { items: d.alerts ?? [], total: d.total, page: d.page, page_size: d.page_size };
  },
  async updateAlert(id: string, data: { status?: AlertStatus; severity?: string }): Promise<Alert> {
    return fetchAPI<Alert>(`/alerts/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },
  async incidents(params?: Record<string, string | number | undefined>): Promise<Paged<Incident>> {
    const d = await fetchAPI<{ incidents: Incident[]; total: number; page: number; page_size: number }>(
      `/incidents/${pagedParams(params)}`
    );
    return { items: d.incidents ?? [], total: d.total, page: d.page, page_size: d.page_size };
  },
  incidentTimeline: (id: string) =>
    fetchAPI<Record<string, unknown[]>>(`/incidents/${id}/timeline`),
  async updateIncident(id: string, data: { status?: IncidentStatus; severity?: string }): Promise<Incident> {
    return fetchAPI<Incident>(`/incidents/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },
  async createIncident(data: { title: string; description?: string; severity: string }): Promise<Incident> {
    return fetchAPI<Incident>(`/incidents/`, { method: "POST", body: JSON.stringify(data) });
  },
  async threatIntel(params?: Record<string, string | number | undefined>): Promise<ThreatIntelEntry[]> {
    return fetchAPI<ThreatIntelEntry[]>(`/threat-intelligence/${pagedParams(params)}`);
  },
  tiLookup: (value: string) =>
    fetchAPI<ThreatIntelEntry | { indicator_value: string }>(`/threat-intelligence/lookup/${encodeURIComponent(value)}`),
  mitre: () => fetchAPI<MITRETechniqueEntry[]>("/mitre/"),
  aiAnalyze: (query: string) =>
    fetchAPI<AIAnalyzeResult>("/ai/analyze", { method: "POST", body: JSON.stringify({ query }) }),
  aiSummarize: (incidentId: string) =>
    fetchAPI<AISummaryResult>("/ai/summarize", { method: "POST", body: JSON.stringify({ incident_id: incidentId }) }),
  blockIp: (ip: string, reason = "Blocked from SOC UI") =>
    fetchAPI<unknown>("/response/block-ip", { method: "POST", body: JSON.stringify({ ip_address: ip, reason }) }),
  health: () => fetchAPI<{ status: string }>("/../health".replace("/api/v1", "")),
};

/** Runs fetcher(); on failure or forced demo mode, returns fallback with source flag. */
export async function withFallback<T>(
  fetcher: () => Promise<T>,
  fallback: T,
  forceDemo = false
): Promise<FetchResult<T>> {
  if (forceDemo) return { data: fallback, source: "demo" };
  try {
    return { data: await fetcher(), source: "live" };
  } catch {
    return { data: fallback, source: "demo" };
  }
}

/** Mutating action with demo-mode simulation. Returns a human-readable outcome. */
export async function runAction(
  live: () => Promise<unknown>,
  demoMessage: string,
  forceDemo = false,
  demoEntity = false
): Promise<string> {
  if (forceDemo || demoEntity) {
    await new Promise((r) => setTimeout(r, 350));
    return `Simulated — ${demoMessage.toLowerCase()}`;
  }
  try {
    await live();
    return "Action executed on the live API";
  } catch {
    return `Live API unreachable — simulated: ${demoMessage.toLowerCase()}`;
  }
}
