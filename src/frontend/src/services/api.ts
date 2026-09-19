import type { DashboardData, Shipment, Disruption, FleetAsset, FleetSummary, Alert, BobResponse } from "../types";

const API_BASE = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// Dashboard
export const getDashboardSummary = () => request<DashboardData>("/dashboard/summary");

// Shipments
export const getShipments = (params?: Record<string, string>) => {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return request<Shipment[]>(`/shipments${qs}`);
};
export const getShipment = (id: string) => request<Shipment>(`/shipments/${id}`);
export const applyRoute = (shipmentId: string, routeName: string) =>
  request<{ status: string; message: string }>(
    `/shipments/${shipmentId}/apply-route?route_name=${encodeURIComponent(routeName)}`,
    { method: "POST" }
  );

// Disruptions
export const getDisruptions = () => request<Disruption[]>("/disruptions");
export const getDisruptionImpact = (id: string) => request<unknown>(`/disruptions/${id}/impact`);
export const toggleDisruption = (id: string) =>
  request<{ status: string; is_active: boolean }>(`/disruptions/${id}/toggle`, { method: "POST" });

// Fleet
export const getFleetAssets = (params?: Record<string, string>) => {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return request<FleetAsset[]>(`/fleet${qs}`);
};
export const getFleetSummary = () => request<FleetSummary>("/fleet/summary");
export const redeployAsset = (assetId: string) =>
  request<{ status: string; message: string }>(`/fleet/redeploy/${assetId}`, { method: "POST" });

// Cold Chain
export const getColdChainAlerts = () => request<Alert[]>("/cold-chain/alerts");
export const getColdChainShipments = () => request<Shipment[]>("/cold-chain/shipments");
export const getTemperatureHistory = (shipmentId: string) =>
  request<unknown>(`/cold-chain/${shipmentId}/temperature`);

// Bob AI
export const queryBob = (query: string) =>
  request<BobResponse>("/bob/query", {
    method: "POST",
    body: JSON.stringify({ query }),
  });

// Simulation
export const runPortStrike = () =>
  request<{ status: string; message: string; impact_summary: unknown }>("/simulation/port-strike", { method: "POST" });
export const runTempExcursion = (shipmentId = "SHP-221") =>
  request<{ status: string; message: string; impact_summary: unknown }>(
    `/simulation/temperature-excursion?shipment_id=${shipmentId}`,
    { method: "POST" }
  );
export const resetSimulation = () =>
  request<{ status: string; message: string }>("/simulation/reset", { method: "POST" });
