import { useState, useEffect } from "react";
import { getColdChainShipments, getColdChainAlerts, getTemperatureHistory } from "../services/api";
import type { Shipment, Alert } from "../types";
import Header from "../components/Layout/Header";
import TemperatureChart from "../components/ColdChain/TemperatureChart";
import { Thermometer } from "lucide-react";

export default function ColdChainPage() {
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Shipment | null>(null);
  const [tempData, setTempData] = useState<Record<string, unknown> | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [s, a] = await Promise.all([getColdChainShipments(), getColdChainAlerts()]);
      setShipments(s);
      setAlerts(a);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const viewTemp = async (s: Shipment) => {
    setSelected(s);
    try {
      const data = await getTemperatureHistory(s.shipment_id);
      setTempData(data as Record<string, unknown>);
    } catch {
      setTempData(null);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <Header title="Cold Chain Monitor" onRefresh={load} loading={loading} />
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-red-400 flex items-center gap-2">
              <Thermometer className="w-4 h-4" /> Active Excursion Alerts ({alerts.length})
            </h3>
            {alerts.map((a) => (
              <div key={a.alert_id} className="bg-red-950/30 border border-red-800/40 rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-bold text-red-400">{a.title}</p>
                    <p className="text-xs text-gray-300 mt-1">{a.message}</p>
                    {a.recommended_action && (
                      <p className="text-xs text-orange-300 mt-1">→ {a.recommended_action}</p>
                    )}
                  </div>
                  <div className="text-right text-xs">
                    <p className="text-red-300 font-bold text-base">{a.current_temperature}°C</p>
                    <p className="text-gray-500">{a.allowed_range}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Shipment list */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-800">
              <h3 className="text-sm font-semibold text-white">Cold-Chain Shipments ({shipments.length})</h3>
            </div>
            <div className="divide-y divide-gray-800/50">
              {shipments.map((s) => (
                <button
                  key={s.shipment_id}
                  onClick={() => viewTemp(s)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-800/50 transition-colors ${selected?.shipment_id === s.shipment_id ? "bg-blue-900/20" : ""}`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-400">{s.shipment_id}</p>
                      <p className="text-xs text-gray-400">{s.cargo_type} | {s.origin} → {s.destination}</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-bold ${
                        s.current_temperature && s.required_max_temperature &&
                        s.current_temperature > s.required_max_temperature
                          ? "text-red-400"
                          : "text-cyan-400"
                      }`}>
                        {s.current_temperature}°C
                      </p>
                      <p className="text-xs text-gray-500">
                        {s.required_min_temperature}–{s.required_max_temperature}°C
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Temperature chart */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            {selected ? (
              <>
                <h3 className="text-sm font-semibold text-white mb-1">
                  {selected.shipment_id} — Temperature History
                </h3>
                <p className="text-xs text-gray-400 mb-3">
                  {selected.cargo_type} | Allowed: {selected.required_min_temperature}°C – {selected.required_max_temperature}°C
                </p>
                <TemperatureChart
                  data={selected.sensor_history.length > 0
                    ? selected.sensor_history
                    : tempData && Array.isArray((tempData as Record<string, unknown>).telemetry_points)
                      ? ((tempData as Record<string, unknown>).telemetry_points as { timestamp: string; temperature: number; humidity?: number; is_excursion: boolean }[])
                      : []
                  }
                  minAllowed={selected.required_min_temperature ?? undefined}
                  maxAllowed={selected.required_max_temperature ?? undefined}
                />
                {tempData && (tempData as Record<string, unknown>).analysis && (
                  <div className="mt-3 text-xs text-gray-400 space-y-1">
                    <p>Excursion count: {String(((tempData as Record<string, unknown>).analysis as Record<string, unknown>)?.excursion_count ?? 0)}</p>
                    <p>Severity: {String(((tempData as Record<string, unknown>).analysis as Record<string, unknown>)?.severity ?? "Nominal")}</p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center h-48 text-gray-500 text-sm">
                Select a shipment to view temperature history
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
