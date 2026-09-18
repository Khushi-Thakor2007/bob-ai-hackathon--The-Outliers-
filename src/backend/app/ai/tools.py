from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import (
    Disruption, Shipment, FleetAsset, RouteAlternative,
    Alert, SensorLog, RedeploymentRecommendation
)
from app.services.fleet_optimizer import FleetOptimizer
from app.services.cold_chain_engine import ColdChainEngine
from app.services.simulation_engine import SimulationEngine

class ControlTowerTools:
    @staticmethod
    def get_control_tower_summary(db: Session) -> Dict[str, Any]:
        """Returns overall KPI counts, active disruptions, and cargo value at risk"""
        active_shipments = db.query(Shipment).filter(Shipment.status != "Delivered").count()
        at_risk = db.query(Shipment).filter(Shipment.risk_level.in_(["High", "Critical"])).count()
        critical = db.query(Shipment).filter(Shipment.risk_level == "Critical").count()
        idle_assets = db.query(FleetAsset).filter(FleetAsset.status == "Idle").count()
        cold_chain_alerts = db.query(Alert).filter(Alert.category == "Cold Chain", Alert.is_resolved == False).count()
        
        at_risk_shipments = db.query(Shipment).filter(Shipment.risk_level.in_(["High", "Critical"])).all()
        val_at_risk = sum(s.cargo_value for s in at_risk_shipments)
        
        active_disruptions = db.query(Disruption).filter(Disruption.is_active == True).all()

        return {
            "active_shipments": active_shipments,
            "at_risk_shipments": at_risk,
            "critical_shipments": critical,
            "idle_fleet_assets": idle_assets,
            "cold_chain_alerts": cold_chain_alerts,
            "cargo_value_at_risk": round(val_at_risk, 2),
            "active_disruptions_count": len(active_disruptions),
            "active_disruptions": [{"id": d.disruption_id, "name": d.name, "severity": d.severity, "location": d.location} for d in active_disruptions]
        }

    @staticmethod
    def get_active_disruptions(db: Session) -> List[Dict[str, Any]]:
        """Returns all currently active disruptions and their details"""
        disruptions = db.query(Disruption).filter(Disruption.is_active == True).all()
        result = []
        for d in disruptions:
            impacted = db.query(Shipment).filter(Shipment.disruption_exposure.contains(d.name)).count()
            result.append({
                "disruption_id": d.disruption_id,
                "name": d.name,
                "type": d.type,
                "location": d.location,
                "severity": d.severity,
                "expected_duration": d.expected_duration,
                "description": d.description,
                "impacted_shipments_count": impacted
            })
        return result

    @staticmethod
    def get_affected_shipments(db: Session, disruption_id: str = None) -> List[Dict[str, Any]]:
        """Returns list of shipments affected by active disruptions"""
        query = db.query(Shipment).filter(Shipment.disruption_exposure != "None")
        shipments = query.all()
        return [
            {
                "shipment_id": s.shipment_id,
                "origin": s.origin,
                "destination": s.destination,
                "current_location": s.current_location,
                "carrier": s.carrier,
                "cargo_type": s.cargo_type,
                "cargo_value": s.cargo_value,
                "priority": s.priority,
                "risk_level": s.risk_level,
                "risk_score": s.current_risk_score,
                "delay_hours": s.delay_hours,
                "recommended_action": s.recommended_action,
                "explanation": s.explanation
            }
            for s in shipments
        ]

    @staticmethod
    def get_shipment_risk(db: Session, shipment_id: str) -> Dict[str, Any]:
        """Returns comprehensive risk details for a specific shipment"""
        s = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
        if not s:
            return {"error": f"Shipment {shipment_id} not found."}
        
        return {
            "shipment_id": s.shipment_id,
            "origin": s.origin,
            "destination": s.destination,
            "current_location": s.current_location,
            "carrier": s.carrier,
            "cargo_type": s.cargo_type,
            "cargo_value": s.cargo_value,
            "priority": s.priority,
            "status": s.status,
            "eta": s.eta,
            "risk_score": s.current_risk_score,
            "risk_level": s.risk_level,
            "delay_hours": s.delay_hours,
            "disruption_exposure": s.disruption_exposure,
            "recommended_action": s.recommended_action,
            "explanation": s.explanation,
            "is_cold_chain": s.is_cold_chain,
            "current_temperature": s.current_temperature
        }

    @staticmethod
    def get_route_alternatives(db: Session, shipment_id: str) -> List[Dict[str, Any]]:
        """Returns available alternative routes and recommendations for a shipment"""
        alts = db.query(RouteAlternative).filter(RouteAlternative.shipment_id == shipment_id).all()
        if not alts:
            s = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
            if s:
                from app.services.route_optimizer import RouteOptimizer
                raw = RouteOptimizer.generate_alternatives_for_shipment(s)
                return raw
            return []
        
        return [
            {
                "route_name": a.route_name,
                "carrier_name": a.carrier_name,
                "mode": a.mode,
                "distance_km": a.distance_km,
                "estimated_eta": a.estimated_eta,
                "delay_hours": a.delay_hours,
                "cost_delta_pct": a.cost_delta_pct,
                "risk_level": a.risk_level,
                "recommendation_score": a.recommendation_score,
                "is_recommended": a.is_recommended,
                "explanation": a.explanation
            }
            for a in alts
        ]

    @staticmethod
    def get_carrier_alternatives(db: Session, shipment_id: str) -> List[Dict[str, Any]]:
        """Returns carrier alternatives and capacity availability"""
        alts = ControlTowerTools.get_route_alternatives(db, shipment_id)
        carriers = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
        current_carrier = carriers.carrier if carriers else ""
        return [a for a in alts if a.get("carrier_name") != current_carrier]

    @staticmethod
    def get_idle_fleet(db: Session) -> List[Dict[str, Any]]:
        """Returns all idle or underutilized fleet assets"""
        assets = db.query(FleetAsset).filter(FleetAsset.status == "Idle").all()
        return [
            {
                "asset_id": a.asset_id,
                "type": a.type,
                "location": a.location,
                "capacity": f"{a.capacity} {a.capacity_unit}",
                "status": a.status,
                "availability": a.availability,
                "utilization_pct": a.utilization,
                "current_route": a.current_route
            }
            for a in assets
        ]

    @staticmethod
    def get_redeployment_recommendations(db: Session) -> List[Dict[str, Any]]:
        """Returns all generated redeployment recommendations matching idle assets to corridors"""
        recs = db.query(RedeploymentRecommendation).all()
        return [
            {
                "asset_id": r.asset_id,
                "asset_type": r.asset_type,
                "location": r.location,
                "capacity": r.capacity,
                "affected_corridor": r.affected_corridor,
                "required_capacity": r.required_capacity,
                "utilization_pct": r.utilization_pct,
                "recommendation": r.recommendation,
                "reason": r.reason
            }
            for r in recs
        ]

    @staticmethod
    def get_cold_chain_alerts(db: Session) -> List[Dict[str, Any]]:
        """Returns all active cold-chain alerts and excursions"""
        alerts = db.query(Alert).filter(Alert.category == "Cold Chain").all()
        return [
            {
                "alert_id": a.alert_id,
                "shipment_id": a.related_id,
                "cargo_type": a.cargo_type,
                "severity": a.severity,
                "current_temperature": a.current_temperature,
                "allowed_range": a.allowed_range,
                "excursion_duration": a.excursion_duration,
                "recommended_action": a.recommended_action,
                "title": a.title,
                "message": a.message
            }
            for a in alerts
        ]

    @staticmethod
    def get_temperature_history(db: Session, shipment_id: str) -> Dict[str, Any]:
        """Returns time series IoT sensor data and excursion status for a cold-chain shipment"""
        s = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
        if not s:
            return {"error": f"Shipment {shipment_id} not found."}
        
        logs = db.query(SensorLog).filter(SensorLog.shipment_id == shipment_id).order_by(SensorLog.timestamp.asc()).all()
        analysis = ColdChainEngine.analyze_sensor_stream(s, logs)
        
        return {
            "shipment_id": s.shipment_id,
            "cargo_type": s.cargo_type,
            "analysis": analysis,
            "telemetry_points": [
                {
                    "timestamp": l.timestamp.isoformat(),
                    "temperature": l.temperature,
                    "humidity": l.humidity,
                    "battery_pct": l.battery_pct,
                    "is_excursion": l.is_excursion
                }
                for l in logs
            ]
        }
