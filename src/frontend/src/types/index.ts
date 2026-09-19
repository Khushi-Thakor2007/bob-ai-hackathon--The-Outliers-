// ---- API Types ----

export interface Disruption {
  id: number;
  disruption_id: string;
  type: string;
  name: string;
  location: string;
  latitude?: number;
  longitude?: number;
  severity: "Low" | "Medium" | "High" | "Critical";
  start_time?: string;
  expected_duration?: string;
  affected_area?: string;
  radius_km?: number;
  description?: string;
  is_active: boolean;
  impacted_shipment_count: number;
  critical_shipment_count: number;
  high_risk_shipment_count: number;
  cargo_value_at_risk: number;
}

export interface RouteAlternative {
  id?: number;
  shipment_id?: string;
  route_name: string;
  carrier_name?: string;
  mode?: string;
  distance_km?: number;
  estimated_eta?: string;
  delay_hours?: number;
  cost_delta_pct?: number;
  risk_level?: string;
  recommendation_score?: number;
  is_recommended?: boolean;
  explanation?: string;
}

export interface SensorPoint {
  timestamp: string;
  temperature: number;
  humidity?: number;
  is_excursion: boolean;
}

export interface Shipment {
  id: number;
  shipment_id: string;
  origin: string;
  destination: string;
  current_location?: string;
  carrier?: string;
  mode?: string;
  cargo_type?: string;
  cargo_value: number;
  weight_kg?: number;
  status: string;
  priority?: string;
  eta?: string;
  delay_hours: number;
  risk_level: "Low" | "Medium" | "High" | "Critical";
  current_risk_score: number;
  disruption_exposure?: string;
  recommended_action?: string;
  explanation?: string;
  is_cold_chain: boolean;
  required_min_temperature?: number;
  required_max_temperature?: number;
  current_temperature?: number;
  origin_lat?: number;
  origin_lon?: number;
  dest_lat?: number;
  dest_lon?: number;
  current_lat?: number;
  current_lon?: number;
  route_alternatives: RouteAlternative[];
  sensor_history: SensorPoint[];
}

export interface FleetAsset {
  id: number;
  asset_id: string;
  type: string;
  license_plate?: string;
  location: string;
  latitude?: number;
  longitude?: number;
  status: "Idle" | "In-Use" | "Maintenance";
  availability: string;
  capacity: number;
  capacity_unit: string;
  utilization: number;
  current_route?: string;
  last_updated?: string;
}

export interface RedeploymentRecommendation {
  id?: number;
  asset_id: string;
  asset_type: string;
  location: string;
  capacity?: string;
  affected_corridor: string;
  required_capacity?: string;
  utilization_pct: number;
  recommendation: string;
  reason?: string;
  status: string;
}

export interface FleetSummary {
  total_assets: number;
  in_use_assets: number;
  idle_assets: number;
  maintenance_assets: number;
  average_utilization: number;
  underutilized_assets_count: number;
  assets: FleetAsset[];
  redeployment_recommendations: RedeploymentRecommendation[];
}

export interface Alert {
  id: number;
  alert_id: string;
  category: string;
  severity: string;
  title: string;
  message: string;
  related_id?: string;
  cargo_type?: string;
  current_temperature?: number;
  allowed_range?: string;
  excursion_duration?: string;
  recommended_action?: string;
  is_resolved: boolean;
  detected_at?: string;
}

export interface KpiMetrics {
  active_shipments: number;
  at_risk_shipments: number;
  critical_shipments: number;
  idle_fleet_assets: number;
  cold_chain_alerts: number;
  cargo_value_at_risk: number;
  total_fleet_assets: number;
  average_fleet_utilization: number;
}

export interface DashboardData {
  kpis: KpiMetrics;
  active_disruptions: Disruption[];
  highest_risk_shipments: Shipment[];
  fleet_summary: FleetSummary;
  cold_chain_alerts: Alert[];
  recent_alerts: Alert[];
}

export interface BobResponse {
  answer: string;
  direct_answer?: string;
  key_numbers?: Record<string, unknown>;
  reasoning?: string;
  recommended_actions?: string[];
  tools_called?: Array<{ tool_name: string; arguments: Record<string, unknown>; result: unknown }>;
}
