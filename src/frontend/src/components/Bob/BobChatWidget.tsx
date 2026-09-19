import { useState, useRef, useEffect } from "react";
import { Bot, Send, X, Minimize2, Maximize2 } from "lucide-react";
import { queryBob } from "../../services/api";
import type { BobResponse } from "../../types";
import ToolExecutionBadge from "./ToolExecutionBadge";

interface Message {
  role: "user" | "bob";
  content: string;
  response?: BobResponse;
  timestamp: Date;
}

const QUICK_QUERIES = [
  "What'\''s happening with the port strike?",
  "Which shipments are at critical risk?",
  "How many idle fleet assets do we have?",
  "Are there any cold chain excursions?",
];

export default function BobChatWidget() {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bob",
      content: "Hello! I'\''m Bob, your Supply Chain AI assistant. I can help you analyze disruptions, shipment risks, fleet utilization, and cold-chain excursions. Ask me anything!",
      timestamp: new Date(),
    },
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (q?: string) => {
    const text = (q || query).trim();
    if (!text) return;
    setQuery("");
    setMessages((prev) => [...prev, { role: "user", content: text, timestamp: new Date() }]);
    setLoading(true);
    try {
      const res = await queryBob(text);
      setMessages((prev) => [
        ...prev,
        { role: "bob", content: res.direct_answer || res.answer, response: res, timestamp: new Date() },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bob", content: "Error contacting the control tower. Please ensure the backend is running.", timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const widgetW = expanded ? "w-[600px]" : "w-80";
  const widgetH = expanded ? "h-[600px]" : "h-96";

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-blue-600 hover:bg-blue-500 rounded-full shadow-2xl flex items-center justify-center transition-all animate-pulse-slow"
      >
        <Bot className="w-7 h-7 text-white" />
      </button>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 ${widgetW} ${widgetH} bg-gray-950 border border-gray-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-all`}>
      {/* Header */}
      <div className="bg-blue-900/50 border-b border-blue-800/50 px-4 py-3 flex items-center gap-2">
        <Bot className="w-5 h-5 text-blue-300" />
        <span className="font-semibold text-white text-sm">Bob AI Assistant</span>
        <div className="flex-1" />
        <button onClick={() => setExpanded((v) => !v)} className="p-1 rounded hover:bg-blue-800/50 text-blue-300">
          {expanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
        </button>
        <button onClick={() => setOpen(false)} className="p-1 rounded hover:bg-blue-800/50 text-blue-300">
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] ${m.role === "user" ? "bg-blue-700 text-white" : "bg-gray-800 text-gray-100"} rounded-xl px-3 py-2 text-sm`}>
              {m.role === "bob" && <p className="text-xs text-blue-400 font-semibold mb-1">Bob</p>}
              <p className="leading-relaxed">{m.content}</p>
              {m.response?.recommended_actions && m.response.recommended_actions.length > 0 && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-gray-400 font-semibold">Recommended Actions:</p>
                  {m.response.recommended_actions.map((a, j) => (
                    <p key={j} className="text-xs text-green-400">→ {a}</p>
                  ))}
                </div>
              )}
              {m.response?.tools_called && expanded && (
                <div className="mt-2 space-y-1">
                  {m.response.tools_called.map((t, j) => (
                    <ToolExecutionBadge key={j} toolName={t.tool_name} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-xl px-3 py-2 text-sm text-gray-400">
              <span className="animate-pulse">Bob is thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick queries */}
      {messages.length <= 1 && (
        <div className="px-3 py-2 flex flex-wrap gap-1 border-t border-gray-800">
          {QUICK_QUERIES.map((q) => (
            <button
              key={q}
              onClick={() => send(q)}
              className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-full px-2 py-1 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-3 border-t border-gray-800 flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about shipments, risks, fleet…"
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
        />
        <button
          onClick={() => send()}
          disabled={loading || !query.trim()}
          className="p-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white disabled:opacity-50 transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
