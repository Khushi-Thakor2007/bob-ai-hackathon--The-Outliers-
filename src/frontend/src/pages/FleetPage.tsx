import { useState, useEffect } from "react";
import { getFleetAssets, getFleetSummary, redeployAsset } from "../services/api";
import type { FleetAsset, FleetSummary } from "../types";
import Header from "../components/Layout/Header";
import { Truck, Package, Anchor } from "lucide-react";

const STATUS_COLOR: Record<string, string> = {
  "Idle": "text-orange-400 bg-orange-900/20 border border-orange-700/30",
  "In-Use": "text-green-400 bg-green-900/20 border border-green-700/30",
  "Maintenance": "text-gray-400 bg-gray-800 border border-gray-700",
};

function assetIcon(type: string) {
  if (type.includes("Vessel")) return <Anchor className="w-4 h-4" />;
  if (type.includes("Container")) return <Package className="w-4 h-4" />;
  return <Truck className="w-4 h-4" />;
}

export default function FleetPage() {
  const [assets, setAssets] = useState<FleetAsset[]>([]);
  const [summary, setSummary] = useState<FleetSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (statusFilter) params.status = statusFilter;
      const [a, s] = await Promise.all([getFleetAssets(params), getFleetSummary()]);
      setAssets(a);
      setSummary(s);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [statusFilter]);

  const redeploy = async (assetId: string) => {
    try {
      const res = await redeployAsset(assetId);
      alert(res.message);
      load();
    } catch {
      alert("Redeployment failed.");
    }
  };

  return (
    <div className="flex flex-col h-full">
      <Header title="Fleet Management" onRefresh={load} loading={loading} />
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Summary KPIs */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Total Assets", value: summary.total_assets, color: "text-blue-400" },
              { label: "In-Use", value: summary.in_use_assets, color: "text-green-400" },
              { label: "Idle", value: summary.idle_assets, color: "text-orange-400" },
              { label: "Maintenance", value: summary.maintenance_assets, color: "text-gray-400" },
            ].map((k) => (
              <div key={k.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
                <p className={`text-2xl font-bold ${k.color}`}>{k.value}</p>
                <p className="text-xs text-gray-500 mt-1">{k.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Redeployment recommendations */}
        {summary && summary.redeployment_recommendations.length > 0 && (
          <div className="bg-orange-900/20 border border-orange-700/30 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-orange-400 mb-3">
              ⚡ Redeployment Recommendations ({summary.redeployment_recommendations.length})
            </h3>
            <div className="space-y-2">
              {(summary.redeployment_recommendations as Record<string, unknown>[]).map((r, i) => (
                <div key={i} className="flex items-center justify-between gap-3 bg-gray-900 border border-gray-800 rounded-lg p-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white font-medium truncate">{String(r.recommendation || "")}</p>
                    <p className="text-xs text-gray-400">{String(r.reason || "")}</p>
                  </div>
                  <button
                    onClick={() => redeploy(String(r.asset_id || ""))}
                    className="shrink-0 px-3 py-1.5 bg-orange-700 hover:bg-orange-600 rounded text-xs text-white font-medium transition-colors"
                  >
                    Deploy
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Filter */}
        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-blue-600"
          >
            <option value="">All Statuses</option>
            <option value="Idle">Idle</option>
            <option value="In-Use">In-Use</option>
            <option value="Maintenance">Maintenance</option>
          </select>
          <span className="text-xs text-gray-500">{assets.length} assets</span>
        </div>

        {/* Asset grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {assets.map((a) => (
            <div key={a.asset_id} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="text-blue-400">{assetIcon(a.type)}</div>
                  <div>
                    <p className="text-sm font-bold text-white">{a.asset_id}</p>
                    <p className="text-xs text-gray-400">{a.type}</p>
                  </div>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${STATUS_COLOR[a.status]}`}>
                  {a.status}
                </span>
              </div>
              <div className="space-y-1 text-xs text-gray-400 mb-3">
                <p>📍 {a.location}</p>
                <p>⚖ {a.capacity} {a.capacity_unit}</p>
                {a.current_route && <p>🛣 {a.current_route}</p>}
                {a.license_plate && <p>🪪 {a.license_plate}</p>}
              </div>
              {/* Utilization bar */}
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Utilization</span>
                  <span>{a.utilization.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${a.utilization > 70 ? "bg-green-500" : a.utilization > 30 ? "bg-blue-500" : "bg-orange-500"}`}
                    style={{ width: `${a.utilization}%` }}
                  />
                </div>
              </div>
              {a.status === "Idle" && (
                <button
                  onClick={() => redeploy(a.asset_id)}
                  className="mt-3 w-full px-3 py-1.5 bg-orange-800 hover:bg-orange-700 rounded text-xs text-orange-200 font-medium transition-colors"
                >
                  Redeploy Asset
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
