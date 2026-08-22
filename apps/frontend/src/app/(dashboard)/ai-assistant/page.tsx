"use client";

import { useState } from "react";
import { Bot, CheckCircle2, Gauge, Send, Sparkles, User, Wrench } from "lucide-react";

const starterMessages = [
  {
    role: "assistant",
    content:
      "Bonjour. Je suis prêt pour le triage SOC, les IOC, MITRE, les incidents, la performance, l’export report et les problèmes frontend.",
  },
  {
    role: "assistant",
    content:
      "Posez n’importe quelle question. Je réponds directement avec une analyse courte, les causes probables et les actions à appliquer.",
  },
];

const appKnowledge = {
  incident: {
    id: "INC-0042",
    attackerIp: "185.220.101.34",
    affectedHosts: "PROD-WEB-01, PROD-APP-03, EDR-01, EDR-03, FW-01",
    pattern: "credential stuffing, mouvement lateral, tentative de dump LSASS, staging puis exfiltration",
    risk: 87,
  },
  routes: ["/dashboard", "/events", "/alerts", "/incidents", "/investigation", "/threat-intelligence", "/mitre", "/ai-assistant", "/settings"],
  mitre: ["T1110 Brute Force", "T1003 OS Credential Dumping", "T1021 Remote Services", "T1041 Exfiltration Over C2 Channel"],
};

type ChatMessage = {
  role: "assistant" | "user";
  content: string;
};

function buildAssistantAnswer(question: string) {
  const q = question.toLowerCase();

  if (q.includes("ioc") || q.includes("ip") || q.includes("hash") || q.includes("domain")) {
    return `IOC prioritaires: ${appKnowledge.incident.attackerIp} est l’IP source la plus critique. Cherchez aussi les connexions vers 45.33.32.156:4444, les comptes deploy/root/admin, et les archives creees dans /tmp/.cache/. Action: bloquer l’IP au firewall, enrichir dans Threat Intel, puis verifier les alertes liees.`;
  }

  if (q.includes("incident") || q.includes("inc-0042") || q.includes("attaque")) {
    return `${appKnowledge.incident.id}: risque ${appKnowledge.incident.risk}/100. Le schema montre ${appKnowledge.incident.pattern}. Hotes touches: ${appKnowledge.incident.affectedHosts}. Action immediate: isoler PROD-WEB-01, revoquer les credentials deploy, capturer la memoire, puis exporter le rapport depuis Investigation.`;
  }

  if (q.includes("mitre") || q.includes("att&ck") || q.includes("tactic") || q.includes("technique")) {
    return `Mapping MITRE probable: ${appKnowledge.mitre.join(", ")}. Priorite detection: brute force, remote services, credential dumping, puis exfiltration C2. Dans la page MITRE, utilisez ces techniques pour verifier la couverture et les detections actives.`;
  }

  if (q.includes("lent") || q.includes("slow") || q.includes("rapide") || q.includes("performance") || q.includes("vitesse")) {
    return "Pour la rapidite: garder les pages statiques quand possible, eviter les gros graphiques JS, limiter les animations permanentes, charger les donnees avec cache, et separer les composants lourds. J’ai deja allege le dashboard en remplacant les graphiques Recharts par des graphes CSS rapides.";
  }

  if (q.includes("404") || q.includes("route") || q.includes("page not found") || q.includes("not found")) {
    return `Les routes disponibles sont: ${appKnowledge.routes.join(", ")}. Si une page retourne encore 404, redemarrez le serveur frontend pour recharger les fichiers de route Next.js, puis testez l’URL exacte.`;
  }

  if (q.includes("export") || q.includes("rapport") || q.includes("report")) {
    return "Export Report fonctionne depuis Investigation. Il genere un fichier texte avec resume executif, timeline, preuves et prochaines actions. Si le telechargement ne part pas, verifier que le navigateur n’a pas bloque les telechargements automatiques.";
  }

  if (q.includes("bug") || q.includes("problem") || q.includes("probleme") || q.includes("solve") || q.includes("fix")) {
    return "Diagnostic rapide: 1. reproduire le probleme avec l’URL exacte, 2. regarder console navigateur et terminal Next.js, 3. verifier route/fichier page.tsx, 4. tester npm run build, 5. corriger puis tester HTTP 200. Donnez-moi le message d’erreur exact et je peux cibler le fichier.";
  }

  if (q.includes("settings") || q.includes("param") || q.includes("configuration")) {
    return "Dans Settings, configurez organisation, fuseau horaire, notifications et retention. Pour fiabilite SOC: activer les alertes critiques, garder incidents 365 jours, et surveiller la retention events pour eviter une base trop lourde.";
  }

  if (q.includes("bonjour") || q.includes("salut") || q.includes("hello")) {
    return "Bonjour. Je peux aider sur analyse SOC, incidents, IOC, MITRE, performance, erreurs 404, export report, UI et configuration. Posez votre question directement.";
  }

  return `Reponse courte: pour "${question}", je recommande de verifier le contexte SOC, identifier les donnees touchees, classer le risque, puis appliquer une action mesurable. Si c’est securite: collecter IOC, mapper MITRE, contenir, eradiquer, documenter. Si c’est application: reproduire, lire l’erreur, corriger le composant ou la route, puis valider avec npm run build.`;
}

export default function AiAssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(starterMessages as ChatMessage[]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);

  const sendMessage = () => {
    if (!input.trim() || isThinking) return;
    const question = input.trim();
    setMessages((current) => [...current, { role: "user", content: question }]);
    setInput("");
    setIsThinking(true);

    window.setTimeout(() => {
      setMessages((current) => [...current, { role: "assistant", content: buildAssistantAnswer(question) }]);
      setIsThinking(false);
    }, 180);
  };

  return (
    <div className="grid min-h-[calc(100vh-7rem)] grid-cols-1 gap-6 xl:grid-cols-[1fr_320px]">
      <section className="card-glow flex min-h-[620px] flex-col rounded-xl">
        <div className="flex items-center justify-between border-b border-soc-border p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyber-cyan/10">
              <Bot className="h-5 w-5 text-cyber-cyan" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Assistant IA</h2>
              <p className="text-sm text-slate-400">Triage, diagnostic et aide operationnelle</p>
            </div>
          </div>
          <span className="rounded-full border border-cyber-green/20 bg-cyber-green/10 px-2.5 py-0.5 text-xs text-cyber-green">
            Online
          </span>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.map((message, index) => (
            <div key={index} className={`flex gap-3 ${message.role === "user" ? "justify-end" : ""}`}>
              {message.role === "assistant" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyber-cyan/10">
                  <Bot className="h-4 w-4 text-cyber-cyan" />
                </div>
              )}
              <div
                className={`max-w-2xl rounded-lg border px-4 py-3 text-sm ${
                  message.role === "user"
                    ? "border-cyber-blue/20 bg-cyber-blue/10 text-slate-100"
                    : "border-soc-border bg-soc-surface/60 text-slate-300"
                }`}
              >
                {message.content}
              </div>
              {message.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyber-blue/10">
                  <User className="h-4 w-4 text-cyber-blue" />
                </div>
              )}
            </div>
          ))}
          {isThinking && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyber-cyan/10">
                <Bot className="h-4 w-4 text-cyber-cyan" />
              </div>
              <div className="rounded-lg border border-soc-border bg-soc-surface/60 px-4 py-3 text-sm text-slate-400">
                Analyse...
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-soc-border p-4">
          <div className="flex gap-3">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") sendMessage();
              }}
              placeholder="Ask about an incident, IOC, or containment step..."
              className="flex-1 rounded-lg border border-soc-border bg-soc-surface px-4 py-2.5 text-sm text-slate-200 placeholder:text-slate-500 focus:border-cyber-cyan/50 focus:outline-none"
            />
            <button
              onClick={sendMessage}
              disabled={isThinking}
              className="inline-flex items-center gap-2 rounded-lg bg-cyber-cyan px-4 py-2.5 text-sm font-medium text-soc-bg transition-colors hover:bg-cyber-cyan/90"
            >
              <Send className="h-4 w-4" />
              Send
            </button>
          </div>
        </div>
      </section>

      <aside className="space-y-4">
        <div className="card-glow rounded-xl p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-medium text-white">
            <Gauge className="h-4 w-4 text-cyber-green" />
            Etat application
          </div>
          <div className="space-y-2 text-xs text-slate-400">
            <p className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-cyber-green" />Routes principales disponibles</p>
            <p className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-cyber-green" />Assistant local instantane</p>
            <p className="flex items-center gap-2"><Wrench className="h-3.5 w-3.5 text-cyber-orange" />Diagnostic guide par question</p>
          </div>
        </div>
        {["Resume INC-0042", "Liste les IOC critiques", "Pourquoi l’application est lente ?", "Comment corriger une erreur 404 ?", "Mappe l’incident a MITRE"].map((prompt) => (
          <button
            key={prompt}
            onClick={() => setInput(prompt)}
            className="card-glow flex w-full items-center gap-3 rounded-xl p-4 text-left text-sm text-slate-300 transition-colors hover:border-cyber-cyan/30"
          >
            <Sparkles className="h-4 w-4 text-cyber-cyan" />
            {prompt}
          </button>
        ))}
      </aside>
    </div>
  );
}
