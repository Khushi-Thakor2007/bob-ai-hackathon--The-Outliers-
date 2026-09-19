from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.models import (
    Disruption, Shipment, FleetAsset, Alert, RouteAlternative,
    SensorLog, RedeploymentRecommendation
)
from app.services.risk_engine import RiskEngine
from app.services.disruption_engine import DisruptionEngine
from app.services.route_optimizer import RouteOptimizer
from app.services.fleet_optimizer import FleetOptimizer
import random


class SimulationEngine:

    @staticmethod
    def simulate_port_strike(db: Session) -> Dict[str, Any]:
        """Activate the JNPT Port Strike disruption and re-score impacted shipments."""
        # Activate disruption
        disruption = db.query(Disruption).filter(
            Disruption.disruption_id == "DISRUPT-001"
        ).first()
        if not disruption:
            # Fallback: activate first disruption
            disruption = db.query(Disruption).first()

        if disruption:
            disruption.is_active = True

        # Re-score all active shipments
        shipments = db.query(Shipment).filter(Shipment.status != "Delivered").all()
        impacted = []

        for s in shipments:
            if disruption:
                is_imp, delay, reason = DisruptionEngine.is_shipment_impacted(s, disruption)
            else:
                is_imp, delay, reason = False, 0.0, ""

            if is_imp:
                risk_result = RiskEngine.compute_risk_score(s, disruption.severity if disruption else "High", delay)
                s.current_risk_score = risk_result["risk_score"]
                s.risk_level = risk_result["risk_level"]
                s.delay_hours = delay
                s.disruption_exposure = disruption.name if disruption else "Port Strike"
                s.status = "At-Risk" if s.status == "In-Transit" else s.status
                s.recommended_action = RiskEngine.get_recommended_action(
                    risk_result["risk_level"], s.cargo_type or "", s.mode or "Road"
                )
                s.explanation = RiskEngine.get_explanation(
                    s, risk_result["risk_level"],
                    disruption.name if disruption else "Port Strike", delay
                )
                impacted.append(s)

                # Generate and store route alternatives
                existing = db.query(RouteAlternative).filter(
                    RouteAlternative.shipment_id == s.shipment_id
                ).count()
                if existing == 0:
                    alts = RouteOptimizer.generate_alternatives_for_shipment(s)
                    for idx, alt in enumerate(alts):
                        db.add(RouteAlternative(shipment_id=s.shipment_id, **alt))

        # Generate redeployment recommendations for idle fleet
        idle_assets = db.query(FleetAsset).filter(FleetAsset.status == "Idle").all()
        existing_recs = db.query(RedeploymentRecommendation).count()
        if existing_recs == 0:
            recs = FleetOptimizer.generate_redeployment_recommendations(idle_assets)
            for r in recs:
                db.add(RedeploymentRecommendation(**r))

        db.commit()

        cargo_val = sum(s.cargo_value for s in impacted)
        critical = sum(1 for s in impacted if s.risk_level == "Critical")

        return {
            "disruption": disruption.name if disruption else "Port Strike",
            "impacted_shipments": len(impacted),
            "critical_shipments": critical,
            "cargo_value_at_risk": round(cargo_val, 2),
            "redeployment_recommendations": db.query(RedeploymentRecommendation).count(),
        }

    @staticmethod
    def simulate_temperature_excursion(db: Session, target_shipment_id: str = "SHP-221") -> Dict[str, Any]:
        """Inject a temperature excursion into a cold-chain shipment."""
        shipment = db.query(Shipment).filter(
            Shipment.shipment_id == target_shipment_id,
            Shipment.is_cold_chain == True
        ).first()

        if not shipment:
            # Fall back to any cold-chain shipment
            shipment = db.query(Shipment).filter(Shipment.is_cold_chain == True).first()

        if not shipment:
            return {"error": "No cold-chain shipment found for simulation"}

        excursion_temp = (shipment.required_max_temperature or 8.0) + 2.1
        shipment.current_temperature = round(excursion_temp, 1)
        shipment.status = "At-Risk"
        shipment.risk_level = "Critical"
        shipment.current_risk_score = 92.0

        # Inject excursion sensor log
        new_log = SensorLog(
            shipment_id=shipment.shipment_id,
            sensor_id=f"SENSOR-SIM-{shipment.shipment_id}",
            timestamp=datetime.utcnow(),
            temperature=round(excursion_temp, 1),
            humidity=72.0,
            battery_pct=88.0,
            latitude=shipment.current_lat,
            longitude=shipment.current_lon,
            is_excursion=True,
        )
        db.add(new_log)

        # Create alert
        alert_id = f"ALERT-SIM-{shipment.shipment_id}"
        existing_alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if not existing_alert:
            db.add(Alert(
                alert_id=alert_id,
                category="Cold Chain",
                severity="Critical",
                title=f"Temperature Excursion: {shipment.shipment_id}",
                message=(
                    f"Simulated critical temperature excursion on {shipment.shipment_id}. "
                    f"Current: {round(excursion_temp, 1)}°C. "
                    f"Allowed max: {shipment.required_max_temperature}°C."
                ),
                related_id=shipment.shipment_id,
                cargo_type=shipment.cargo_type,
                current_temperature=round(excursion_temp, 1),
                allowed_range=f"{shipment.required_min_temperature}°C to {shipment.required_max_temperature}°C",
                excursion_duration="Active (simulated)",
                recommended_action="Dispatch refrigeration intervention team immediately.",
                is_resolved=False,
            ))

        db.commit()

        return {
            "shipment_id": shipment.shipment_id,
            "cargo_type": shipment.cargo_type,
            "injected_temperature": round(excursion_temp, 1),
            "max_allowed": shipment.required_max_temperature,
            "status": "Critical excursion active",
        }

    @staticmethod
    def reset_simulation(db: Session) -> Dict[str, Any]:
        """Reset all disruption flags and restore baseline shipment states."""
        # Deactivate all disruptions
        disruptions = db.query(Disruption).all()
        for d in disruptions:
            d.is_active = False

        # Reset shipment risk scores
        shipments = db.query(Shipment).filter(Shipment.status != "Delivered").all()
        for s in shipments:
            s.current_risk_score = max(10.0, s.current_risk_score * 0.3)
            if s.current_risk_score < 35:
                s.risk_level = "Low"
            elif s.current_risk_score < 60:
                s.risk_level = "Medium"
            else:
                s.risk_level = "High"
            s.delay_hours = 0.0
            s.status = "In-Transit"
            s.disruption_exposure = "None"
            s.recommended_action = "Normal monitoring. No immediate action required."

        # Resolve simulated alerts
        sim_alerts = db.query(Alert).filter(Alert.alert_id.like("ALERT-SIM-%")).all()
        for a in sim_alerts:
            a.is_resolved = True

        # Clear redeployment recommendations
        db.query(RedeploymentRecommendation).delete()
        db.query(RouteAlternative).delete()

        db.commit()

        return {"message": "Simulation reset. All disruptions deactivated. Shipments returned to baseline."}
