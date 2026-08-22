import type {
  SecurityEvent,
  Alert,
  Incident,
  ThreatIntel,
  DashboardStats,
  EventsByHour,
  AlertsBySeverity,
  AttackerIP,
  TargetedUser,
  ChatMessage,
  Settings,
  MITRETactic,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export const api = {
  dashboard: {
    getStats: () => fetchAPI<DashboardStats>("/dashboard/stats"),
    getEventsByHour: () => fetchAPI<EventsByHour[]>("/dashboard/events-by-hour"),
    getAlertsBySeverity: () => fetchAPI<AlertsBySeverity[]>("/dashboard/alerts-by-severity"),
    getTopAttackerIPs: () => fetchAPI<AttackerIP[]>("/dashboard/top-attackers"),
    getTopTargetedUsers: () => fetchAPI<TargetedUser[]>("/dashboard/targeted-users"),
  },
  events: {
    list: (params?: Record<string, string>) => {
      const query = params ? "?" + new URLSearchParams(params).toString() : "";
      return fetchAPI<{ events: SecurityEvent[]; total: number }>(`/events${query}`);
    },
    get: (id: string) => fetchAPI<SecurityEvent>(`/events/${id}`),
  },
  alerts: {
    list: (params?: Record<string, string>) => {
      const query = params ? "?" + new URLSearchParams(params).toString() : "";
      return fetchAPI<{ alerts: Alert[]; total: number }>(`/alerts${query}`);
    },
    get: (id: string) => fetchAPI<Alert>(`/alerts/${id}`),
    update: (id: string, data: Partial<Alert>) =>
      fetchAPI<Alert>(`/alerts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  },
  incidents: {
    list: (params?: Record<string, string>) => {
      const query = params ? "?" + new URLSearchParams(params).toString() : "";
      return fetchAPI<{ incidents: Incident[]; total: number }>(`/incidents${query}`);
    },
    get: (id: string) => fetchAPI<Incident>(`/incidents/${id}`),
    update: (id: string, data: Partial<Incident>) =>
      fetchAPI<Incident>(`/incidents/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  },
  threatIntel: {
    list: () => fetchAPI<ThreatIntel[]>("/threat-intelligence"),
  },
  mitre: {
    getMatrix: () => fetchAPI<MITRETactic[]>("/mitre/matrix"),
  },
  ai: {
    chat: (message: string) =>
      fetchAPI<ChatMessage>("/ai/chat", { method: "POST", body: JSON.stringify({ message }) }),
  },
  settings: {
    get: () => fetchAPI<Settings>("/settings"),
    update: (data: Partial<Settings>) =>
      fetchAPI<Settings>("/settings", { method: "PATCH", body: JSON.stringify(data) }),
  },
};
