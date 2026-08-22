"use client";

import { useState } from "react";
import { Bell, Building2, Database, Save } from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    orgName: "SOC Platform",
    timezone: "Africa/Casablanca",
    emailEnabled: true,
    slackEnabled: false,
    criticalOnly: true,
    eventsDays: 90,
    alertsDays: 180,
    incidentsDays: 365,
  });
  const [saved, setSaved] = useState(false);

  const saveSettings = () => {
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2200);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Settings</h2>
          <p className="mt-1 text-sm text-slate-400">Platform preferences, notifications, and retention</p>
        </div>
        <button
          onClick={saveSettings}
          className="inline-flex items-center gap-2 rounded-lg bg-cyber-cyan px-4 py-2 text-sm font-medium text-soc-bg hover:bg-cyber-cyan/90"
        >
          <Save className="h-4 w-4" />
          {saved ? "Saved" : "Save Changes"}
        </button>
      </div>

      <section className="card-glow rounded-xl p-5">
        <div className="mb-5 flex items-center gap-3">
          <Building2 className="h-5 w-5 text-cyber-cyan" />
          <h3 className="text-lg font-semibold text-white">General</h3>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm text-slate-400">Organization Name</span>
            <input
              value={settings.orgName}
              onChange={(event) => setSettings({ ...settings, orgName: event.target.value })}
              className="w-full rounded-lg border border-soc-border bg-soc-surface px-3 py-2.5 text-sm text-slate-200 focus:border-cyber-cyan/50 focus:outline-none"
            />
          </label>
          <label className="space-y-2">
            <span className="text-sm text-slate-400">Timezone</span>
            <select
              value={settings.timezone}
              onChange={(event) => setSettings({ ...settings, timezone: event.target.value })}
              className="w-full rounded-lg border border-soc-border bg-soc-surface px-3 py-2.5 text-sm text-slate-200 focus:border-cyber-cyan/50 focus:outline-none"
            >
              <option>Africa/Casablanca</option>
              <option>UTC</option>
              <option>Europe/Paris</option>
              <option>America/New_York</option>
            </select>
          </label>
        </div>
      </section>

      <section className="card-glow rounded-xl p-5">
        <div className="mb-5 flex items-center gap-3">
          <Bell className="h-5 w-5 text-cyber-orange" />
          <h3 className="text-lg font-semibold text-white">Notifications</h3>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          {[
            ["emailEnabled", "Email alerts"],
            ["slackEnabled", "Slack alerts"],
            ["criticalOnly", "Critical only"],
          ].map(([key, label]) => (
            <label key={key} className="flex items-center justify-between rounded-lg border border-soc-border bg-soc-surface/50 p-4 text-sm text-slate-300">
              {label}
              <input
                type="checkbox"
                checked={settings[key as "emailEnabled" | "slackEnabled" | "criticalOnly"]}
                onChange={(event) => setSettings({ ...settings, [key]: event.target.checked })}
                className="h-4 w-4 accent-cyber-cyan"
              />
            </label>
          ))}
        </div>
      </section>

      <section className="card-glow rounded-xl p-5">
        <div className="mb-5 flex items-center gap-3">
          <Database className="h-5 w-5 text-cyber-green" />
          <h3 className="text-lg font-semibold text-white">Retention</h3>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            ["eventsDays", "Events"],
            ["alertsDays", "Alerts"],
            ["incidentsDays", "Incidents"],
          ].map(([key, label]) => (
            <label key={key} className="space-y-2">
              <span className="text-sm text-slate-400">{label} retention days</span>
              <input
                type="number"
                min={1}
                value={settings[key as "eventsDays" | "alertsDays" | "incidentsDays"]}
                onChange={(event) => setSettings({ ...settings, [key]: Number(event.target.value) })}
                className="w-full rounded-lg border border-soc-border bg-soc-surface px-3 py-2.5 text-sm text-slate-200 focus:border-cyber-cyan/50 focus:outline-none"
              />
            </label>
          ))}
        </div>
      </section>
    </div>
  );
}
