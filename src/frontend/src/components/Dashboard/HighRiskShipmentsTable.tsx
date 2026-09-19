import type { Shipment } from "../../types";

interface HighRiskShipmentsTableProps {
  shipments: Shipment[];
  onSelect: (s: Shipment) => void;
}

const RISK_BADGE: Record<string, string> = {
  Critical: "bg-red-900/50 text-red-400 border border-red-700/50",
  High: "bg-orange-900/50 text-orange-400 border border-orange-700/50",
  Medium: "bg-yellow-900/50 text-yellow-400 border border-yellow-700/50",
  Low: "bg-green-900/50 text-green-400 border border-green-700/50",
};

export default function HighRiskShipmentsTable({ shipments, onSelect }: HighRiskShipmentsTableProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-white mb-3">Highest-Risk Shipments</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-gray-500 border-b border-gray-800">
              <th className="pb-2 text-left font-medium">ID</th>
              <th className="pb-2 text-left font-medium">Cargo</th>
              <th className="pb-2 text-left font-medium">Route</th>
              <th className="pb-2 text-left font-medium">Risk</th>
              <th className="pb-2 text-left font-medium">Score</th>
              <th className="pb-2 text-left font-medium">Value</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/50">
            {shipments.map((s) => (
              <tr
                key={s.shipment_id}
                onClick={() => onSelect(s)}
                className="cursor-pointer hover:bg-gray-800/50 transition-colors"
              >
                <td className="py-2 pr-2 text-blue-400 font-mono">{s.shipment_id}</td>
                <td className="py-2 pr-2 text-gray-300">{s.cargo_type}</td>
                <td className="py-2 pr-2 text-gray-400">
                  {s.origin} → {s.destination}
                </td>
                <td className="py-2 pr-2">
                  <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${RISK_BADGE[s.risk_level]}`}>
                    {s.risk_level}
                  </span>
                </td>
                <td className="py-2 pr-2 text-gray-300">{s.current_risk_score.toFixed(0)}</td>
                <td className="py-2 text-gray-300">${(s.cargo_value / 1e3).toFixed(0)}K</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
