"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { CheckCircle2, Info, Loader2, X, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Severity } from "@/lib/types";

/* ─────────────────────────── Button 3D ─────────────────────────── */
type ButtonVariant = "default" | "primary" | "danger" | "success";

export function Button3D({
  children,
  variant = "default",
  size = "md",
  loading = false,
  disabled = false,
  onClick,
  className,
  title,
  type = "button",
}: {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: "sm" | "md";
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  title?: string;
  type?: "button" | "submit";
}) {
  return (
    <button
      type={type}
      title={title}
      disabled={disabled || loading}
      onClick={onClick}
      className={cn(
        "btn-3d",
        variant === "primary" && "btn-3d-primary",
        variant === "danger" && "btn-3d-danger",
        variant === "success" && "btn-3d-success",
        size === "sm" && "btn-3d-sm",
        className
      )}
    >
      {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
      {children}
    </button>
  );
}

/* ─────────────────────────── Card 3D ─────────────────────────── */
export function Card3D({
  children,
  className,
  interactive = false,
  style,
}: {
  children: ReactNode;
  className?: string;
  interactive?: boolean;
  style?: React.CSSProperties;
}) {
  return (
    <div style={style} className={cn("card-3d", interactive && "card-3d-hover", className)}>
      {children}
    </div>
  );
}

/* ─────────────────────────── Badges ─────────────────────────── */
const sevStyle: Record<Severity, string> = {
  critical: "text-rose-300 border-rose-500/50 bg-rose-950/60 shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_3px_8px_rgba(239,68,68,0.35)]",
  high: "text-orange-300 border-orange-500/50 bg-orange-950/60 shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_3px_8px_rgba(249,115,22,0.3)]",
  medium: "text-amber-200 border-amber-500/50 bg-amber-950/50 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_3px_8px_rgba(245,158,11,0.25)]",
  low: "text-sky-300 border-sky-500/50 bg-sky-950/50 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_3px_8px_rgba(14,165,233,0.25)]",
  info: "text-slate-300 border-slate-500/40 bg-slate-800/60 shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_2px_6px_rgba(0,0,0,0.4)]",
};

export function SeverityBadge3D({ severity }: { severity: Severity }) {
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide", sevStyle[severity] ?? sevStyle.info)}>
      <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current shadow-[0_0_6px_currentColor]" />
      {severity}
    </span>
  );
}

export function StatusBadge3D({ status }: { status: string }) {
  const map: Record<string, string> = {
    new: "bg-cyan-950/60 text-cyan-300 border-cyan-500/50",
    open: "bg-rose-950/60 text-rose-300 border-rose-500/50",
    acknowledged: "bg-amber-950/50 text-amber-200 border-amber-500/50",
    investigating: "bg-orange-950/50 text-orange-300 border-orange-500/50",
    contained: "bg-violet-950/50 text-violet-300 border-violet-500/50",
    pending: "bg-yellow-950/40 text-yellow-200 border-yellow-600/40",
    resolved: "bg-emerald-950/60 text-emerald-300 border-emerald-500/50",
    closed: "bg-slate-800/60 text-slate-300 border-slate-500/40",
  };
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_2px_5px_rgba(0,0,0,0.4)]", map[status] ?? map.closed)}>
      {status}
    </span>
  );
}

/* ─────────────────────────── KPI card ─────────────────────────── */
export function KpiCard3D({
  label,
  value,
  icon,
  tone = "cyan",
  hint,
  onClick,
}: {
  label: string;
  value: string | number;
  icon: ReactNode;
  tone?: "cyan" | "red" | "orange" | "violet" | "green";
  hint?: string;
  onClick?: () => void;
}) {
  const tones: Record<string, string> = {
    cyan: "text-cyan-300 from-cyan-500/20",
    red: "text-rose-300 from-rose-500/20",
    orange: "text-orange-300 from-orange-500/20",
    violet: "text-violet-300 from-violet-500/20",
    green: "text-emerald-300 from-emerald-500/20",
  };
  return (
    <Card3D interactive className={cn("p-4", onClick && "cursor-pointer")} >
      <div className="flex items-center gap-4" onClick={onClick}>
        <div className={cn("plate-3d h-12 w-12 shrink-0 bg-gradient-to-br to-transparent", tones[tone])}>{icon}</div>
        <div className="min-w-0">
          <p className="truncate text-[11px] font-semibold uppercase tracking-widest text-slate-400">{label}</p>
          <p className="text-3d mt-0.5 text-2xl font-black tracking-tight text-white">
            {typeof value === "number" ? value.toLocaleString() : value}
          </p>
          {hint ? <p className="mt-0.5 truncate text-[11px] text-slate-500">{hint}</p> : null}
        </div>
      </div>
    </Card3D>
  );
}

/* ─────────────────────────── Modal ─────────────────────────── */
export function Modal3D({
  open,
  onClose,
  title,
  children,
  wide = false,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  wide?: boolean;
}) {
  useEffect(() => {
    const h = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    if (open) window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className={cn("card-3d animate-pop max-h-[86vh] w-full overflow-hidden", wide ? "max-w-4xl" : "max-w-xl")}
        onClick={(e) => e.stopPropagation()}
        style={{ perspective: 900 }}
      >
        <div className="flex items-center justify-between border-b border-slate-700/60 bg-gradient-to-b from-slate-800/60 to-transparent px-5 py-3.5">
          <h3 className="text-3d text-base font-bold text-white">{title}</h3>
          <button onClick={onClose} className="btn-3d btn-3d-sm !px-2" title="Close">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto px-5 py-4">{children}</div>
      </div>
    </div>
  );
}

/* ─────────────────────────── Toasts ─────────────────────────── */
type Toast = { id: number; message: string; tone: "ok" | "err" | "info" };
const ToastCtx = createContext<(message: string, tone?: Toast["tone"]) => void>(() => {});

export function useToast() {
  return useContext(ToastCtx);
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = useCallback((message: string, tone: Toast["tone"] = "ok") => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, message, tone }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3800);
  }, []);

  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="pointer-events-none fixed bottom-5 right-5 z-[60] flex w-80 flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              "card-3d animate-pop flex items-start gap-2.5 px-4 py-3 text-sm",
              t.tone === "ok" && "border-emerald-500/40",
              t.tone === "err" && "border-rose-500/40",
              t.tone === "info" && "border-cyan-500/40"
            )}
          >
            {t.tone === "ok" ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" /> : null}
            {t.tone === "err" ? <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" /> : null}
            {t.tone === "info" ? <Info className="mt-0.5 h-4 w-4 shrink-0 text-cyan-400" /> : null}
            <span className="text-slate-200">{t.message}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

/* ─────────────────────────── Page header ─────────────────────────── */
export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-3d text-2xl font-black tracking-tight text-white">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

/* ─────────────────────────── Empty state ─────────────────────────── */
export function EmptyState({ icon, message }: { icon?: ReactNode; message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-14 text-slate-500">
      <div className="plate-3d h-14 w-14">{icon}</div>
      <p className="text-sm">{message}</p>
    </div>
  );
}

/* ─────────────────────────── Search input ─────────────────────────── */
export function SearchInput({
  value,
  onChange,
  placeholder = "Search…",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="panel-inset flex items-center gap-2 px-3 py-2">
      <svg className="h-4 w-4 shrink-0 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 10a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-transparent text-sm text-slate-200 placeholder-slate-500 outline-none"
      />
      {value ? (
        <button onClick={() => onChange("")} className="text-slate-500 hover:text-slate-300" title="Clear">
          <X className="h-4 w-4" />
        </button>
      ) : null}
    </div>
  );
}
