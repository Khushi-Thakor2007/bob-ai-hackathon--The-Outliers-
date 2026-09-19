import { useState, useEffect } from "react";
import { getDashboardSummary } from "../services/api";
import type { DashboardData, Shipment } from "../types";
import Header from "../components/Layout/Header";
import DemoBanner from "../components/Layout/DemoBanner";
import KpiCard from "../components/Dashboard/KpiCard";
import LogisticsMap from "../components/Dashboard/LogisticsMap";
import ActiveDisruptionsCard from "../components/Dashboard/ActiveDisruptionsCard";
import HighRiskShipmentsTable from "../components/Dashboard/HighRiskShipmentsTable";
import FleetSummaryCard from "../components/Dashboard/FleetSummaryCard";
import ColdChainAlertsCard from "../components/Dashboard/ColdChainAlertsCard";
import ShipmentDetailDrawer from "../components/Shipments/ShipmentDetailDrawer";
import {
  Package, AlertTriangle, Truck, Thermometer, TrendingUp
} from "lucide-react";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Shipment | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const d = await getDashboardSummary();
      setData(d);
    } catch (e) {
      setError("Cannot reach backend. Ensure it is running on http://localhost:8000");
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const fmt = (v: number) =>
    v >= 1e6 ? `$${(v / 1e6).toFixed(1)}M` : v >= 1e3 ? `$${(v / 1e3).toFixed(0)}K` : `$${v}`;

  return (
    <div className="flex flex-col h-full">
      <Header title="Control Tower Dashboard" onRefresh={load} loading={loading} />
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        <DemoBanner onSimulate={load} />

        {error && (
          <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-4 text-red-400 text-sm">
            ⚠ {error}
          </div>
        )}

        {loading && !data && (
          <div className="text-center py-20 text-gray-500">Loading dashboard data…</div>
        )}

        {data && (
          <>
            {/* KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <KpiCard label="Active Shipments" value={data.kpis.active_shipments}
                color="blue" icon={<Package className="w-6 h-6 text-blue-400" />} />
              <KpiCard label="At-Risk Shipments" value={data.kpis.at_risk_shipments}
                sub={`${data.kpis.critical_shipments} critical`}
                color="red" icon={<AlertTriangle className="w-6 h-6 text-red-400" />} />
              <KpiCard label="Cargo at Risk" value={fmt(data.kpis.cargo_value_at_risk)}
                color="orange" icon={<TrendingUp className="w-6 h-6 text-orange-400" />} />
              <KpiCard label="Idle Fleet Assets" value={data.kpis.idle_fleet_assets}
                sub={`of ${data.kpis.total_fleet_assets} total`}
                color="yellow" icon={<Truck className="w-6 h-6 text-yellow-400" />} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <KpiCard label="Cold Chain Alerts" value={data.kpis.cold_chain_alerts}
                color={data.kpis.cold_chain_alerts > 0 ? "red" : "green"}
                icon={<Thermometer className="w-6 h-6 text-cyan-400" />} />
              <KpiCard label="Fleet Utilization" value={`${data.kpis.average_fleet_utilization.toFixed(1)}%`}
                color="green" />
            </div>

            {/* Map */}
            <LogisticsMap
              shipments={data.highest_risk_shipments}
              disruptions={data.active_disruptions}
            />

            {/* Bottom row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2">
                <HighRiskShipmentsTable
                  shipments={data.highest_risk_shipments}
                  onSelect={setSelected}
                />
              </div>
              <div className="space-y-4">
                <ActiveDisruptionsCard disruptions={data.active_disruptions} />
                <FleetSummaryCard summary={data.fleet_summary} />
                <ColdChainAlertsCard alerts={data.cold_chain_alerts} />
              </div>
            </div>
          </>
        )}
      </div>
      <ShipmentDetailDrawer shipment={selected} onClose={() => setSelected(null)} onUpdate={load} />
    </div>
  );
}
