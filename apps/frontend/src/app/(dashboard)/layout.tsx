import { Sidebar } from "@/components/sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-transparent text-slate-800">
      <div className="mx-auto max-w-[1600px] rounded-[28px] border border-white/10 bg-[#0d121d]/85 shadow-[0_30px_80px_rgba(0,0,0,0.55)] backdrop-blur-sm">
        <Sidebar />
        <main className="min-h-screen transition-all duration-300">
          <header className="px-6 pb-4 pt-2">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h1 className="text-[4rem] font-black leading-[0.9] tracking-[-0.05em] text-slate-900 dark:text-white">Security Operations Center</h1>
              </div>
            </div>
            <div className="mt-8 space-y-4 text-slate-700 dark:text-slate-300">
              <div className="text-2xl font-medium">Systems Online</div>
              <div className="text-2xl font-medium text-slate-700 dark:text-slate-300">
                {new Date().toLocaleDateString("en-US", {
                  weekday: "long",
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </div>
            </div>
          </header>
          <div className="animate-rise px-6 pb-10">{children}</div>
        </main>
      </div>
    </div>
  );
}
