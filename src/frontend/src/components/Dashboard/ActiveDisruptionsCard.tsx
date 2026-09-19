import type { Disruption } from "../../types";
import { AlertTriangle } from "lucide-react";

interface ActiveDisruptionsCardProps {
  disruptions: Disruption[];
}

const SEVERITY_COLOR: Record<string, string> = {
  Critical: "bg-red-900/40 border-red-600/40 text-red-400",
  High: "bg-orange-900/40 border-orange-600/40 text-orange-400",
  Medium: "bg-yellow-900/40 border-yellow-600/40 text-yellow-400",
  Low: "bg-blue-900/40 border-blue-600/40 text-blue-400",
};

export default function ActiveDisruptionsCard({ disruptions }: ActiveDisruptionsCardProps) {
  const active = disruptions.filter((d) => d.is_active);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle className="w-4 h-4 text-orange-400" />
        <h3 className="text-sm font-semibold text-white">Active Disruptions</h3>
        <span className="ml-auto text-xs bg-red-900/50 text-red-400 px-2 py-0.5 rounded-full">
          {active.length} active
        </span>
      </div>
      <div className="space-y-2">
        {active.length === 0 && (
          <p className="text-xs text-gray-500">No active disruptions.</p>
        )}
        {active.map((d) => (
          <div key={d.disruption_id} className={`rounded-lg border p-3 ${SEVERITY_COLOR[d.severity] || "bg-gray-800"}`}>
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-white">{d.name}</p>
                <p className="text-xs text-gray-400">{d.location}</p>
              </div>
              <span className="text-xs font-bold shrink-0">{d.severity}</span>
            </div>
            <div className="flex gap-4 mt-2 text-xs text-gray-400">
              <span>{d.impacted_shipment_count} shipments</span>
              <span>${(d.cargo_value_at_risk / 1e6).toFixed(1)}M exposed</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
