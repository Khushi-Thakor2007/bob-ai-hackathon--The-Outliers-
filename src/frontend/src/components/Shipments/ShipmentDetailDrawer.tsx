import type { Shipment } from "../../types";
import { X, Package, MapPin, AlertTriangle, Thermometer, Route } from "lucide-react";
import { applyRoute } from "../../services/api";

interface ShipmentDetailDrawerProps {
  shipment: Shipment | null;
  onClose: () => void;
  onUpdate: () => void;
}

const RISK_COLOR: Record<string, string> = {
  Critical: "text-red-400 bg-red-900/30 border-red-700/40",
  High: "text-orange-400 bg-orange-900/30 border-orange-700/40",
  Medium: "text-yellow-400 bg-yellow-900/30 border-yellow-700/40",
  Low: "text-green-400 bg-green-900/30 border-green-700/40",
};

export default function ShipmentDetailDrawer({ shipment, onClose, onUpdate }: ShipmentDetailDrawerProps) {
  if (!shipment) return null;

  const handleApply = async (routeName: string) => {
    try {
      await applyRoute(shipment.shipment_id, routeName);
      alert(`Route "${routeName}" applied successfully!`);
      onUpdate();
      onClose();
    } catch {
      alert("Failed to apply route.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="w-full max-w-lg bg-gray-950 border-l border-gray-800 h-full overflow-y-auto">
        <div className="sticky top-0 bg-gray-950 border-b border-gray-800 px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Package className="w-5 h-5 text-blue-400" />
            <span className="font-semibold text-white">{shipment.shipment_id}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${RISK_COLOR[shipment.risk_level]}`}>
              {shipment.risk_level}
            </span>
          </div>
          <button onClick={onClose} className="p-1.5 rounded hover:bg-gray-800 text-gray-400">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* Basics */}
          <section>
            <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-2">Shipment Details</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {[
                ["Cargo", shipment.cargo_type],
                ["Carrier", shipment.carrier],
                ["Mode", shipment.mode],
                ["Status", shipment.status],
                ["Priority", shipment.priority],
                ["Weight", `${shipment.weight_kg?.toFixed(0)} kg`],
                ["Value", `$${shipment.cargo_value.toLocaleString()}`],
                ["ETA", shipment.eta],
                ["Delay", `${shipment.delay_hours}h`],
                ["Risk Score", `${shipment.current_risk_score.toFixed(0)}/100`],
              ].map(([label, val]) => (
                <div key={label as string}>
                  <p className="text-xs text-gray-500">{label}</p>
                  <p className="text-gray-200 truncate">{val || "—"}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Route */}
          <section>
            <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-2 flex items-center gap-1">
              <MapPin className="w-3 h-3" /> Route
            </h4>
            <div className="bg-gray-900 rounded-lg p-3 text-sm">
              <p className="text-gray-300">{shipment.origin} → <span className="text-white font-medium">{shipment.current_location}</span> → {shipment.destination}</p>
            </div>
          </section>

          {/* Disruption */}
          {shipment.disruption_exposure && shipment.disruption_exposure !== "None" && (
            <section className="bg-orange-900/20 border border-orange-700/30 rounded-lg p-3">
              <h4 className="text-xs uppercase tracking-wide text-orange-400 mb-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Disruption Exposure
              </h4>
              <p className="text-sm text-orange-300">{shipment.disruption_exposure}</p>
              {shipment.explanation && <p className="text-xs text-gray-400 mt-1">{shipment.explanation}</p>}
            </section>
          )}

          {/* Recommended Action */}
          {shipment.recommended_action && (
            <section className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-3">
              <h4 className="text-xs uppercase tracking-wide text-blue-400 mb-1">Recommended Action</h4>
              <p className="text-sm text-blue-300">{shipment.recommended_action}</p>
            </section>
          )}

          {/* Cold Chain */}
          {shipment.is_cold_chain && (
            <section>
              <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-2 flex items-center gap-1">
                <Thermometer className="w-3 h-3" /> Cold Chain
              </h4>
              <div className="bg-gray-900 rounded-lg p-3 text-sm">
                <p className="text-gray-300">
                  Current: <span className="text-cyan-400 font-bold">{shipment.current_temperature}°C</span>
                  {" "}(Allowed: {shipment.required_min_temperature}°C – {shipment.required_max_temperature}°C)
                </p>
              </div>
            </section>
          )}

          {/* Route Alternatives */}
          {shipment.route_alternatives.length > 0 && (
            <section>
              <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-2 flex items-center gap-1">
                <Route className="w-3 h-3" /> Route Alternatives
              </h4>
              <div className="space-y-2">
                {shipment.route_alternatives.map((r, i) => (
                  <div
                    key={i}
                    className={`rounded-lg p-3 border text-xs ${
                      r.is_recommended
                        ? "border-green-600/50 bg-green-900/20"
                        : "border-gray-700/50 bg-gray-900"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-white text-sm">{r.route_name}</span>
                      {r.is_recommended && (
                        <span className="text-green-400 text-xs font-bold">★ RECOMMENDED</span>
                      )}
                    </div>
                    <div className="flex gap-4 text-gray-400">
                      <span>{r.mode}</span>
                      <span>+{r.delay_hours}h delay</span>
                      <span>{r.cost_delta_pct && r.cost_delta_pct > 0 ? "+" : ""}{r.cost_delta_pct}% cost</span>
                      <span>Score: {r.recommendation_score}</span>
                    </div>
                    {r.explanation && <p className="mt-1 text-gray-500">{r.explanation}</p>}
                    <button
                      onClick={() => handleApply(r.route_name)}
                      className="mt-2 px-3 py-1 bg-blue-700 hover:bg-blue-600 rounded text-white text-xs font-medium transition-colors"
                    >
                      Apply This Route
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
