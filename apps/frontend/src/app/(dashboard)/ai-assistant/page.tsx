"use client";

import { useRef, useState } from "react";
import { Bot, Send, Sparkles, User } from "lucide-react";
import { api } from "@/lib/api";
import { demoAIReply } from "@/lib/demo-data";
import { Button3D, Card3D, PageHeader } from "@/components/ui";

interface Msg {
  role: "user" | "ai";
  text: string;
  meta?: string;
}

const SUGGESTIONS = [
  "Analyse the latest brute force activity",
  "Check for signs of data exfiltration",
  "Summarise the current incident load",
  "Which MITRE techniques lack coverage?",
  "What should I triage first right now?",
];

export default function AiAssistantPage() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "ai",
      text: "Bonjour — I'm your SOC AI analyst. I correlate live events, alerts and incidents. Ask me anything, or pick a suggestion below.",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  async function send(text?: string) {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setBusy(true);
    let reply: Msg;
    try {
      const r = await api.aiAnalyze(q);
      reply = {
        role: "ai",
        text: r.response,
        meta: [r.model_used, r.confidence != null ? `confidence ${(r.confidence * 100).toFixed(0)}%` : null]
          .filter(Boolean)
          .join(" · "),
      };
    } catch {
      await new Promise((res) => setTimeout(res, 600));
      reply = { role: "ai", text: demoAIReply(q), meta: "offline analyst · heuristic mode" };
    }
    setMessages((m) => [...m, reply]);
    setBusy(false);
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }

  return (
    <>
      <PageHeader
        title="AI Assistant"
        subtitle="Threat analysis copilot backed by the RAG engine (falls back to heuristic mode when offline)"
      />

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Chat */}
        <Card3D className="flex h-[600px] flex-col p-5 lg:col-span-2">
          <div className="panel-inset flex-1 space-y-4 overflow-y-auto p-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                <div
                  className={`plate-3d h-9 w-9 shrink-0 ${
                    m.role === "ai" ? "border-violet-500/40" : "border-cyan-500/40"
                  }`}
                >
                  {m.role === "ai" ? <Bot className="h-4 w-4 text-violet-300" /> : <User className="h-4 w-4 text-cyan-300" />}
                </div>
                <div
                  className={`animate-pop max-w-[75%] rounded-xl border px-3.5 py-2.5 text-sm leading-relaxed ${
                    m.role === "ai"
                      ? "border-violet-500/25 bg-violet-950/20 text-slate-200"
                      : "border-cyan-500/25 bg-cyan-950/20 text-slate-100"
                  }`}
                  style={{ boxShadow: "inset 0 1px 0 rgba(255,255,255,0.06), 0 4px 12px rgba(0,0,0,0.35)" }}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>
                  {m.meta ? <p className="mt-1.5 text-[10px] uppercase tracking-widest text-slate-500">{m.meta}</p> : null}
                </div>
              </div>
            ))}
            {busy ? (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Sparkles className="h-4 w-4 animate-pulse text-violet-400" /> Correlating events…
              </div>
            ) : null}
            <div ref={endRef} />
          </div>
          <div className="mt-3 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Ask the analyst…"
              className="panel-inset flex-1 px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none"
            />
            <Button3D variant="primary" loading={busy} onClick={() => send()}>
              <Send className="h-4 w-4" /> Send
            </Button3D>
          </div>
        </Card3D>

        {/* Suggestions */}
        <Card3D className="p-5">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-400">
            <Sparkles className="h-4 w-4 text-violet-400" /> Quick Prompts
          </h3>
          <div className="space-y-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                disabled={busy}
                className="card-3d card-3d-hover w-full px-3.5 py-3 text-left text-xs font-medium text-slate-300 disabled:opacity-50"
              >
                {s}
              </button>
            ))}
          </div>
          <div className="panel-inset mt-4 p-3 text-[11px] leading-relaxed text-slate-500">
            The assistant queries the ai-service RAG pipeline (retrieval over MITRE, threat intel and recent events).
            Without the backend it answers in heuristic offline mode so the console stays usable.
          </div>
        </Card3D>
      </div>
    </>
  );
}
