import { useState, useEffect } from "react";
import { getShipments } from "../services/api";
import type { Shipment } from "../types";
import Header from "../components/Layout/Header";
import ShipmentDetailDrawer from "../components/Shipments/ShipmentDetailDrawer";
import { Search, Filter } from "lucide-react";

const RISK_BADGE: Record<string, string> = {
  Critical: "bg-red-900/50 text-red-400 border border-red-700/50",
  High: "bg-orange-900/50 text-orange-400 border border-orange-700/50",
  Medium: "bg-yellow-900/50 text-yellow-400 border border-yellow-700/50",
  Low: "bg-green-900/50 text-green-400 border border-green-700/50",
};

export default function ShipmentsPage() {
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [selected, setSelected] = useState<Shipment | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (riskFilter) params.risk_level = riskFilter;
      const data = await getShipments(params);
      setShipments(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [search, riskFilter]);

  return (
    <div className="flex flex-col h-full">
      <Header title="Shipments" onRefresh={load} loading={loading} />
      <div className="flex-1 overflow-y-auto p-5">
        {/* Filters */}
        <div className="flex gap-3 mb-4 flex-wrap">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
            <input
              type="text"
              placeholder="Search by ID, cargo, carrier…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 w-64 focus:outline-none focus:border-blue-600"
            />
          </div>
          <div className="relative flex items-center">
            <Filter className="absolute left-3 w-3.5 h-3.5 text-gray-500" />
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="pl-9 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-blue-600"
            >
              <option value="">All Risk Levels</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          <span className="flex items-center text-xs text-gray-500 ml-auto">
            {shipments.length} shipments
          </span>
        </div>

        {/* Table */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-gray-950 text-gray-500 border-b border-gray-800">
                <th className="px-4 py-3 text-left">ID</th>
                <th className="px-4 py-3 text-left">Cargo</th>
                <th className="px-4 py-3 text-left">Route</th>
                <th className="px-4 py-3 text-left">Carrier</th>
                <th className="px-4 py-3 text-left">Mode</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Risk</th>
                <th className="px-4 py-3 text-left">Score</th>
                <th className="px-4 py-3 text-left">Value</th>
                <th className="px-4 py-3 text-left">Delay</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {loading ? (
                <tr><td colSpan={10} className="text-center py-10 text-gray-500">Loading…</td></tr>
              ) : shipments.length === 0 ? (
                <tr><td colSpan={10} className="text-center py-10 text-gray-500">No shipments found.</td></tr>
              ) : shipments.map((s) => (
                <tr
                  key={s.shipment_id}
                  onClick={() => setSelected(s)}
                  className="cursor-pointer hover:bg-gray-800/50 transition-colors"
                >
                  <td className="px-4 py-2.5 text-blue-400 font-mono">{s.shipment_id}</td>
                  <td className="px-4 py-2.5 text-gray-300">
                    {s.cargo_type}
                    {s.is_cold_chain && <span className="ml-1 text-cyan-500">❄</span>}
                  </td>
                  <td className="px-4 py-2.5 text-gray-400">{s.origin} → {s.destination}</td>
                  <td className="px-4 py-2.5 text-gray-400">{s.carrier}</td>
                  <td className="px-4 py-2.5 text-gray-400">{s.mode}</td>
                  <td className="px-4 py-2.5 text-gray-300">{s.status}</td>
                  <td className="px-4 py-2.5">
                    <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${RISK_BADGE[s.risk_level] || ""}`}>
                      {s.risk_level}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-gray-300">{s.current_risk_score.toFixed(0)}</td>
                  <td className="px-4 py-2.5 text-gray-300">${(s.cargo_value / 1e3).toFixed(0)}K</td>
                  <td className={`px-4 py-2.5 ${s.delay_hours > 0 ? "text-orange-400" : "text-gray-400"}`}>
                    {s.delay_hours > 0 ? `+${s.delay_hours}h` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <ShipmentDetailDrawer shipment={selected} onClose={() => setSelected(null)} onUpdate={load} />
    </div>
  );
}
