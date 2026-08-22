"use client";

import { useMemo, useState, type ReactNode } from "react";
import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight, Inbox } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button3D, EmptyState } from "./ui";

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  sortValue?: (row: T) => string | number;
  className?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  pageSize?: number;
  emptyMessage?: string;
  toolbar?: ReactNode;
}

/** Generic table: client-side sort (click headers), search-aware via parent, working pagination. */
export function DataTable<T>({
  data,
  columns,
  rowKey,
  onRowClick,
  pageSize = 10,
  emptyMessage = "No records match the current filters.",
  toolbar,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(1);

  const sorted = useMemo(() => {
    const col = columns.find((c) => c.key === sortKey);
    if (!col?.sortValue) return data;
    const fn = col.sortValue;
    return [...data].sort((a, b) => {
      const va = fn(a);
      const vb = fn(b);
      const cmp = typeof va === "number" && typeof vb === "number"
        ? va - vb
        : String(va).localeCompare(String(vb));
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [data, columns, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const current = Math.min(page, totalPages);
  const rows = sorted.slice((current - 1) * pageSize, current * pageSize);

  function toggleSort(col: Column<T>) {
    if (!col.sortValue) return;
    if (sortKey === col.key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(col.key);
      setSortDir("desc");
    }
  }

  return (
    <div className="card-3d overflow-hidden">
      {toolbar ? <div className="border-b border-slate-700/50 px-4 py-3">{toolbar}</div> : null}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/50 bg-gradient-to-b from-slate-800/70 to-slate-900/40">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => toggleSort(col)}
                  className={cn(
                    "select-none whitespace-nowrap px-4 py-3 text-left text-[11px] font-bold uppercase tracking-widest text-slate-400",
                    col.sortValue && "cursor-pointer hover:text-cyan-300",
                    col.className
                  )}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {sortKey === col.key ? (
                      sortDir === "asc" ? <ArrowUp className="h-3 w-3 text-cyan-400" /> : <ArrowDown className="h-3 w-3 text-cyan-400" />
                    ) : null}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={rowKey(row)}
                onClick={() => onRowClick?.(row)}
                className={cn(
                  "border-b border-slate-800/70 transition-colors last:border-0",
                  i % 2 === 1 && "bg-slate-900/30",
                  onRowClick && "cursor-pointer hover:bg-cyan-950/30"
                )}
              >
                {columns.map((col) => (
                  <td key={col.key} className={cn("whitespace-nowrap px-4 py-3 text-slate-300", col.className)}>
                    {col.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length === 0 ? <EmptyState icon={<Inbox className="h-6 w-6" />} message={emptyMessage} /> : null}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-700/50 bg-slate-900/40 px-4 py-2.5">
        <span className="text-xs text-slate-500">
          {sorted.length.toLocaleString()} record{sorted.length === 1 ? "" : "s"} · page {current}/{totalPages}
        </span>
        <div className="flex items-center gap-2">
          <Button3D size="sm" disabled={current <= 1} onClick={() => setPage(current - 1)}>
            <ChevronLeft className="h-3.5 w-3.5" /> Prev
          </Button3D>
          <Button3D size="sm" disabled={current >= totalPages} onClick={() => setPage(current + 1)}>
            Next <ChevronRight className="h-3.5 w-3.5" />
          </Button3D>
        </div>
      </div>
    </div>
  );
}
