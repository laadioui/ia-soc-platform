"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface AlertChartProps {
  data: { hour: string; count: number; critical: number; high: number; medium: number }[];
}

export function AlertChart({ data }: AlertChartProps) {
  return (
    <div className="card-glow rounded-xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-400">Events by Hour</h3>
        <div className="flex items-center gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-cyber-red" />Critical</span>
          <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-cyber-orange" />High</span>
          <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-cyber-blue" />Medium</span>
        </div>
      </div>

      <div className="h-[300px] rounded-lg border border-soc-border/60 bg-soc-bg/30 p-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
            <XAxis dataKey="hour" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} width={40} />
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(15,23,42,0.96)",
                border: "1px solid rgba(148,163,184,0.2)",
                borderRadius: 12,
                color: "#e2e8f0",
              }}
              formatter={(value: number, name: string) => [value.toLocaleString(), name]}
            />
            <Line type="monotone" dataKey="critical" stroke="#ef4444" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="high" stroke="#f59e0b" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="medium" stroke="#3b82f6" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
