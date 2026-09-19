import { useState, useRef, useEffect } from "react";
import { queryBob } from "../services/api";
import type { BobResponse } from "../types";
import Header from "../components/Layout/Header";
import ToolExecutionBadge from "../components/Bob/ToolExecutionBadge";
import { Bot, Send } from "lucide-react";

interface Message {
  role: "user" | "bob";
  content: string;
  response?: BobResponse;
  ts: Date;
}

const EXAMPLES = [
  "What'\''s happening with the port strike?",
  "Which shipments are at critical risk?",
  "Tell me about shipment SHP-104",
  "How many idle fleet assets do we have?",
  "Any cold chain excursions I should know about?",
  "Recommend rerouting options for high-risk shipments",
];

export default function BobAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bob",
      content: "Hi! I'\''m Bob, your AI-powered Supply Chain Control Tower assistant. I can answer questions about active disruptions, shipment risks, fleet utilization, cold-chain excursions, and route recommendations. Try asking me something!",
      ts: new Date(),
    },
  ]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (q?: string) => {
    const text = (q || query).trim();
    if (!text || loading) return;
    setQuery("");
    setMessages((prev) => [...prev, { role: "user", content: text, ts: new Date() }]);
    setLoading(true);
    try {
      const res = await queryBob(text);
      setMessages((prev) => [
        ...prev,
        { role: "bob", content: res.direct_answer || res.answer, response: res, ts: new Date() },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bob", content: "Error connecting to the backend. Please check that the server is running on http://localhost:8000.", ts: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <Header title="Bob AI Assistant" />
      <div className="flex flex-1 overflow-hidden gap-0">
        {/* Chat */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold ${
                  m.role === "bob" ? "bg-blue-700 text-white" : "bg-gray-700 text-gray-300"
                }`}>
                  {m.role === "bob" ? <Bot className="w-4 h-4" /> : "U"}
                </div>
                <div className={`max-w-2xl ${m.role === "user" ? "items-end" : "items-start"} flex flex-col gap-2`}>
                  <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    m.role === "user" ? "bg-blue-700 text-white" : "bg-gray-900 border border-gray-800 text-gray-100"
                  }`}>
                    <p>{m.content}</p>
                  </div>
                  {m.response?.recommended_actions && m.response.recommended_actions.length > 0 && (
                    <div className="bg-green-900/20 border border-green-800/30 rounded-xl px-4 py-3 text-sm">
                      <p className="text-xs text-green-400 font-semibold mb-2 uppercase tracking-wide">Recommended Actions</p>
                      <ul className="space-y-1">
                        {m.response.recommended_actions.map((a, j) => (
                          <li key={j} className="text-green-300 flex gap-2">
                            <span className="text-green-500 mt-0.5">→</span>
                            {a}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {m.response?.key_numbers && Object.keys(m.response.key_numbers).length > 0 && (
                    <div className="bg-gray-900 border border-gray-800 rounded-xl px-4 py-3">
                      <p className="text-xs text-gray-500 font-semibold mb-2 uppercase tracking-wide">Key Numbers</p>
                      <div className="flex flex-wrap gap-3">
                        {Object.entries(m.response.key_numbers).map(([k, v]) => (
                          <div key={k} className="text-center">
                            <p className="text-sm font-bold text-blue-400">
                              {typeof v === "number" ? (v > 1000 ? `$${(v / 1e6).toFixed(1)}M` : v.toFixed(0)) : String(v)}
                            </p>
                            <p className="text-xs text-gray-500">{k.replace(/_/g, " ")}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {m.response?.tools_called && m.response.tools_called.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {m.response.tools_called.map((t, j) => (
                        <ToolExecutionBadge key={j} toolName={t.tool_name} />
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-gray-600">{m.ts.toLocaleTimeString()}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-700 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-900 border border-gray-800 rounded-2xl px-4 py-3 text-sm text-gray-400 animate-pulse">
                  Bob is analysing the control tower data…
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-800 p-4 flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Ask Bob about shipments, disruptions, fleet, cold chain…"
              className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
            />
            <button
              onClick={() => send()}
              disabled={loading || !query.trim()}
              className="px-4 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl text-white disabled:opacity-50 transition-colors flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Example queries sidebar */}
        <div className="w-56 border-l border-gray-800 p-4 overflow-y-auto bg-gray-950">
          <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold mb-3">Try asking…</p>
          <div className="space-y-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => send(ex)}
                className="w-full text-left text-xs text-gray-400 hover:text-white bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-lg p-2 transition-colors"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
