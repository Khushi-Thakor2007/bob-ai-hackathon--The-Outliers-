import type { Alert } from "../../types";
import { Thermometer } from "lucide-react";

interface ColdChainAlertsCardProps {
  alerts: Alert[];
}

export default function ColdChainAlertsCard({ alerts }: ColdChainAlertsCardProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <Thermometer className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm font-semibold text-white">Cold Chain Alerts</h3>
        {alerts.length > 0 && (
          <span className="ml-auto text-xs bg-red-900/50 text-red-400 px-2 py-0.5 rounded-full animate-pulse">
            {alerts.length} ALERT{alerts.length > 1 ? "S" : ""}
          </span>
        )}
      </div>
      {alerts.length === 0 ? (
        <p className="text-xs text-green-400">✓ All cold-chain readings nominal</p>
      ) : (
        <div className="space-y-2">
          {alerts.slice(0, 3).map((a) => (
            <div key={a.alert_id} className="bg-red-950/30 border border-red-800/30 rounded-lg p-2">
              <p className="text-xs font-semibold text-red-400">{a.title}</p>
              <p className="text-xs text-gray-400 mt-0.5">{a.related_id} — {a.current_temperature}°C</p>
              <p className="text-xs text-gray-500">{a.allowed_range}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
