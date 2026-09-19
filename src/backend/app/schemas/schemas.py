from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime


# ---- Disruption ----
class DisruptionOut(BaseModel):
    id: int
    disruption_id: str
    type: str
    name: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    severity: str
    start_time: Optional[datetime] = None
    expected_duration: Optional[str] = None
    affected_area: Optional[str] = None
    radius_km: Optional[float] = None
    description: Optional[str] = None
    is_active: bool
    impacted_shipment_count: int = 0
    critical_shipment_count: int = 0
    high_risk_shipment_count: int = 0
    cargo_value_at_risk: float = 0.0

    model_config = {"from_attributes": True}


# ---- Route Alternative ----
class RouteAlternativeOut(BaseModel):
    id: Optional[int] = None
    shipment_id: Optional[str] = None
    route_name: str
    carrier_name: Optional[str] = None
    mode: Optional[str] = None
    distance_km: Optional[float] = None
    estimated_eta: Optional[str] = None
    delay_hours: Optional[float] = None
    cost_delta_pct: Optional[float] = None
    risk_level: Optional[str] = None
    recommendation_score: Optional[float] = None
    is_recommended: Optional[bool] = None
    explanation: Optional[str] = None

    model_config = {"from_attributes": True}


# ---- Shipment ----
class ShipmentOut(BaseModel):
    id: int
    shipment_id: str
    origin: str
    destination: str
    current_location: Optional[str] = None
    carrier: Optional[str] = None
    mode: Optional[str] = None
    cargo_type: Optional[str] = None
    cargo_value: float
    weight_kg: Optional[float] = None
    status: str
    priority: Optional[str] = None
    eta: Optional[str] = None
    delay_hours: float = 0.0
    risk_level: str = "Low"
    current_risk_score: float = 0.0
    disruption_exposure: Optional[str] = "None"
    recommended_action: Optional[str] = None
    explanation: Optional[str] = None
    is_cold_chain: bool = False
    required_min_temperature: Optional[float] = None
    required_max_temperature: Optional[float] = None
    current_temperature: Optional[float] = None
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    dest_lat: Optional[float] = None
    dest_lon: Optional[float] = None
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None
    route_alternatives: List[RouteAlternativeOut] = []
    sensor_history: List[Dict[str, Any]] = []

    model_config = {"from_attributes": True}


# ---- Fleet Asset ----
class FleetAssetOut(BaseModel):
    id: int
    asset_id: str
    type: str
    license_plate: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    availability: str
    capacity: float
    capacity_unit: str = "tonnes"
    utilization: float = 0.0
    current_route: Optional[str] = None
    last_updated: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---- Redeployment Recommendation ----
class RedeploymentRecommendationOut(BaseModel):
    id: Optional[int] = None
    asset_id: str
    asset_type: str
    location: str
    capacity: Optional[str] = None
    affected_corridor: str
    required_capacity: Optional[str] = None
    utilization_pct: float
    recommendation: str
    reason: Optional[str] = None
    status: str = "Pending"

    model_config = {"from_attributes": True}


# ---- Fleet Utilisation Summary ----
class FleetUtilisationSummary(BaseModel):
    total_assets: int
    in_use_assets: int
    idle_assets: int
    maintenance_assets: int
    average_utilization: float
    underutilized_assets_count: int
    assets: List[FleetAssetOut] = []
    redeployment_recommendations: List[Any] = []

    model_config = {"from_attributes": True}


# ---- Alert ----
class AlertOut(BaseModel):
    id: int
    alert_id: str
    category: str
    severity: str
    title: str
    message: str
    related_id: Optional[str] = None
    cargo_type: Optional[str] = None
    current_temperature: Optional[float] = None
    allowed_range: Optional[str] = None
    excursion_duration: Optional[str] = None
    recommended_action: Optional[str] = None
    is_resolved: bool = False
    detected_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---- KPI Metrics ----
class KpiMetrics(BaseModel):
    active_shipments: int
    at_risk_shipments: int
    critical_shipments: int
    idle_fleet_assets: int
    cold_chain_alerts: int
    cargo_value_at_risk: float
    total_fleet_assets: int
    average_fleet_utilization: float


# ---- Dashboard Summary ----
class DashboardSummary(BaseModel):
    kpis: KpiMetrics
    active_disruptions: List[Any] = []
    highest_risk_shipments: List[ShipmentOut] = []
    fleet_summary: FleetUtilisationSummary
    cold_chain_alerts: List[AlertOut] = []
    recent_alerts: List[AlertOut] = []

    model_config = {"from_attributes": True}


# ---- Bob AI ----
class BobQueryRequest(BaseModel):
    query: str

class BobQueryResponse(BaseModel):
    answer: str
    direct_answer: Optional[str] = None
    key_numbers: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    recommended_actions: Optional[List[str]] = None
    tools_called: Optional[List[Dict[str, Any]]] = None


# ---- Simulation ----
class SimulationResponse(BaseModel):
    status: str
    scenario: str
    message: str
    impact_summary: Optional[Dict[str, Any]] = None
