import { useState, useEffect } from "react";
import { getDisruptions, getDisruptionImpact, toggleDisruption } from "../services/api";
import type { Disruption } from "../types";
import Header from "../components/Layout/Header";

const SEV_COLOR: Record<string, string> = {
  Critical: "text-red-400 bg-red-900/30 border-red-700/40",
  High: "text-orange-400 bg-orange-900/30 border-orange-700/40",
  Medium: "text-yellow-400 bg-yellow-900/30 border-yellow-700/40",
  Low: "text-blue-400 bg-blue-900/30 border-blue-700/40",
};

export default function DisruptionsPage() {
  const [disruptions, setDisruptions] = useState<Disruption[]>([]);
  const [loading, setLoading] = useState(true);
  const [impact, setImpact] = useState<Record<string, unknown> | null>(null);
  const [impactLoading, setImpactLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getDisruptions();
      setDisruptions(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const viewImpact = async (id: string) => {
    setImpactLoading(true);
    try {
      const data = await getDisruptionImpact(id);
      setImpact(data as Record<string, unknown>);
    } finally {
      setImpactLoading(false);
    }
  };

  const toggle = async (id: string) => {
    await toggleDisruption(id);
    load();
  };

  return (
    <div className="flex flex-col h-full">
      <Header title="Disruptions" onRefresh={load} loading={loading} />
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {disruptions.map((d) => (
          <div key={d.disruption_id} className={`rounded-xl border p-5 ${d.is_active ? SEV_COLOR[d.severity] : "border-gray-800 bg-gray-900 text-gray-500"}`}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="text-base font-bold text-white">{d.name}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${d.is_active ? SEV_COLOR[d.severity] : "border-gray-700 text-gray-500"}`}>
                    {d.severity}
                  </span>
                  {d.is_active && (
                    <span className="text-xs bg-red-900/50 text-red-400 px-2 py-0.5 rounded-full animate-pulse font-bold">
                      ACTIVE
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mb-1">{d.type} — {d.location}</p>
                <p className="text-sm text-gray-300 mb-3">{d.description}</p>
                <div className="flex gap-6 text-xs text-gray-400">
                  <span>⏱ {d.expected_duration}</span>
                  <span>📦 {d.impacted_shipment_count} shipments</span>
                  <span>⚠ {d.critical_shipment_count} critical</span>
                  <span>💰 ${(d.cargo_value_at_risk / 1e6).toFixed(2)}M at risk</span>
                </div>
              </div>
              <div className="flex flex-col gap-2 shrink-0">
                <button
                  onClick={() => viewImpact(d.disruption_id)}
                  className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 rounded text-xs text-white font-medium transition-colors"
                >
                  View Impact
                </button>
                <button
                  onClick={() => toggle(d.disruption_id)}
                  className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                    d.is_active
                      ? "bg-gray-700 hover:bg-gray-600 text-gray-300"
                      : "bg-green-800 hover:bg-green-700 text-green-300"
                  }`}
                >
                  {d.is_active ? "Deactivate" : "Activate"}
                </button>
              </div>
            </div>
          </div>
        ))}

        {/* Impact panel */}
        {(impact || impactLoading) && (
          <div className="bg-gray-900 border border-blue-800/50 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-blue-400 mb-3">Impact Analysis</h3>
            {impactLoading ? (
              <p className="text-gray-500 text-sm animate-pulse">Analysing…</p>
            ) : (
              <pre className="text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(impact, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
