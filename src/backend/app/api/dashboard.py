from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models.models import Disruption, Shipment, FleetAsset, Alert, RouteAlternative, SensorLog
from app.services.fleet_optimizer import FleetOptimizer
from app.schemas.schemas import DashboardSummary, KpiMetrics, FleetUtilisationSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    # Shipments calculations
    all_shipments = db.query(Shipment).all()
    active_shipments = [s for s in all_shipments if s.status != "Delivered"]
    at_risk_shipments = [s for s in active_shipments if s.risk_level in ["High", "Critical"] or s.current_risk_score >= 60.0]
    critical_shipments = [s for s in active_shipments if s.risk_level == "Critical" or s.current_risk_score >= 80.0]
    
    cargo_val_at_risk = sum(s.cargo_value for s in at_risk_shipments)

    # Fleet calculations
    all_assets = db.query(FleetAsset).all()
    fleet_summary_data = FleetOptimizer.calculate_utilization_summary(all_assets)
    redeploy_recs = FleetOptimizer.generate_redeployment_recommendations(all_assets)

    # Cold chain alerts
    cold_alerts = db.query(Alert).filter(Alert.category == "Cold Chain", Alert.is_resolved == False).all()
    recent_alerts = db.query(Alert).order_by(Alert.detected_at.desc()).limit(5).all()

    # Active Disruptions
    disruptions = db.query(Disruption).filter(Disruption.is_active == True).all()
    disruption_outs = []
    for d in disruptions:
        impacted = [s for s in active_shipments if d.name.lower() in (s.disruption_exposure or "").lower() or (s.current_location and d.location.lower() in s.current_location.lower())]
        d_out = {
            "id": d.id,
            "disruption_id": d.disruption_id,
            "type": d.type,
            "name": d.name,
            "location": d.location,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "severity": d.severity,
            "start_time": d.start_time,
            "expected_duration": d.expected_duration,
            "affected_area": d.affected_area,
            "radius_km": d.radius_km,
            "description": d.description,
            "is_active": d.is_active,
            "impacted_shipment_count": len(impacted),
            "critical_shipment_count": sum(1 for s in impacted if s.risk_level == "Critical"),
            "high_risk_shipment_count": sum(1 for s in impacted if s.risk_level == "High"),
            "cargo_value_at_risk": sum(s.cargo_value for s in impacted)
        }
        disruption_outs.append(d_out)

    # Highest-risk shipments (top 8)
    sorted_risk_shipments = sorted(active_shipments, key=lambda x: x.current_risk_score, reverse=True)[:8]

    # Populate route alternatives and sensor history for the high-risk shipments
    for s in sorted_risk_shipments:
        s.route_alternatives = db.query(RouteAlternative).filter(RouteAlternative.shipment_id == s.shipment_id).all()
        if s.is_cold_chain:
            logs = db.query(SensorLog).filter(SensorLog.shipment_id == s.shipment_id).order_by(SensorLog.timestamp.desc()).limit(10).all()
            s.sensor_history = [
                {"timestamp": l.timestamp, "temperature": l.temperature, "humidity": l.humidity, "is_excursion": l.is_excursion}
                for l in reversed(logs)
            ]

    kpis = KpiMetrics(
        active_shipments=len(active_shipments),
        at_risk_shipments=len(at_risk_shipments),
        critical_shipments=len(critical_shipments),
        idle_fleet_assets=fleet_summary_data["idle_assets"],
        cold_chain_alerts=len(cold_alerts),
        cargo_value_at_risk=round(cargo_val_at_risk, 2),
        total_fleet_assets=fleet_summary_data["total_assets"],
        average_fleet_utilization=fleet_summary_data["average_utilization"]
    )

    fleet_summary = FleetUtilisationSummary(
        total_assets=fleet_summary_data["total_assets"],
        in_use_assets=fleet_summary_data["in_use_assets"],
        idle_assets=fleet_summary_data["idle_assets"],
        maintenance_assets=fleet_summary_data["maintenance_assets"],
        average_utilization=fleet_summary_data["average_utilization"],
        underutilized_assets_count=fleet_summary_data["underutilized_assets_count"],
        assets=all_assets,
        redeployment_recommendations=[
            {
                "id": idx + 1,
                "asset_id": r["asset_id"],
                "asset_type": r["asset_type"],
                "location": r["location"],
                "capacity": r["capacity"],
                "affected_corridor": r["affected_corridor"],
                "required_capacity": r["required_capacity"],
                "utilization_pct": r["utilization_pct"],
                "target_shipment_id": None,
                "recommendation": r["recommendation"],
                "reason": r["reason"],
                "status": r["status"]
            }
            for idx, r in enumerate(redeploy_recs)
        ]
    )

    return DashboardSummary(
        kpis=kpis,
        active_disruptions=disruption_outs,
        highest_risk_shipments=sorted_risk_shipments,
        fleet_summary=fleet_summary,
        cold_chain_alerts=cold_alerts,
        recent_alerts=recent_alerts
    )
