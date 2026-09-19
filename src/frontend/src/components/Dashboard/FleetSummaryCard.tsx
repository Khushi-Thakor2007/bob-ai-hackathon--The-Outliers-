import type { FleetSummary } from "../../types";
import { Truck } from "lucide-react";

interface FleetSummaryCardProps {
  summary: FleetSummary;
}

export default function FleetSummaryCard({ summary }: FleetSummaryCardProps) {
  const pct = summary.average_utilization;
  const barColor = pct > 80 ? "bg-green-500" : pct > 50 ? "bg-blue-500" : "bg-orange-500";

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <Truck className="w-4 h-4 text-blue-400" />
        <h3 className="text-sm font-semibold text-white">Fleet Utilisation</h3>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center">
          <p className="text-xl font-bold text-white">{summary.total_assets}</p>
          <p className="text-xs text-gray-500">Total</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-bold text-orange-400">{summary.idle_assets}</p>
          <p className="text-xs text-gray-500">Idle</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-bold text-green-400">{summary.in_use_assets}</p>
          <p className="text-xs text-gray-500">In-Use</p>
        </div>
      </div>
      <div>
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Avg Utilization</span>
          <span>{pct.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-2">
          <div className={`h-2 rounded-full transition-all ${barColor}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
      {summary.redeployment_recommendations.length > 0 && (
        <div className="mt-3 text-xs text-orange-400 font-medium">
          ⚡ {summary.redeployment_recommendations.length} redeployment{summary.redeployment_recommendations.length > 1 ? "s" : ""} suggested
        </div>
      )}
    </div>
  );
}
