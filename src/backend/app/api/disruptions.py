from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.models import Disruption, Shipment
from app.schemas.schemas import DisruptionOut, ShipmentOut
from app.services.disruption_engine import DisruptionEngine

router = APIRouter(prefix="/disruptions", tags=["Disruptions"])

@router.get("", response_model=List[DisruptionOut])
def get_all_disruptions(db: Session = Depends(get_db)):
    disruptions = db.query(Disruption).all()
    all_shipments = db.query(Shipment).filter(Shipment.status != "Delivered").all()

    result = []
    for d in disruptions:
        # Check impacted shipments
        impacted = []
        if d.is_active:
            for s in all_shipments:
                is_imp, delay, _ = DisruptionEngine.is_shipment_impacted(s, d)
                if is_imp or d.name.lower() in (s.disruption_exposure or "").lower():
                    impacted.append(s)

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
        result.append(d_out)
    return result

@router.get("/{disruption_id}/impact")
def get_disruption_impact(disruption_id: str, db: Session = Depends(get_db)):
    disruption = db.query(Disruption).filter(Disruption.disruption_id == disruption_id).first()
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")

    all_shipments = db.query(Shipment).filter(Shipment.status != "Delivered").all()
    impacted_shipments = []
    
    for s in all_shipments:
        is_imp, delay, reason = DisruptionEngine.is_shipment_impacted(s, disruption)
        if is_imp:
            impacted_shipments.append({
                "shipment_id": s.shipment_id,
                "cargo_type": s.cargo_type,
                "origin": s.origin,
                "destination": s.destination,
                "carrier": s.carrier,
                "cargo_value": s.cargo_value,
                "priority": s.priority,
                "risk_level": s.risk_level,
                "risk_score": s.current_risk_score,
                "delay_hours": delay,
                "recommended_action": s.recommended_action,
                "reason": reason
            })

    return {
        "disruption": {
            "id": disruption.disruption_id,
            "name": disruption.name,
            "type": disruption.type,
            "location": disruption.location,
            "severity": disruption.severity,
            "is_active": disruption.is_active
        },
        "impact_summary": {
            "total_affected": len(impacted_shipments),
            "critical_count": sum(1 for s in impacted_shipments if s["risk_level"] == "Critical"),
            "high_risk_count": sum(1 for s in impacted_shipments if s["risk_level"] == "High"),
            "total_cargo_value_at_risk": sum(s["cargo_value"] for s in impacted_shipments),
            "average_delay_hours": round(sum(s["delay_hours"] for s in impacted_shipments) / max(1, len(impacted_shipments)), 1)
        },
        "affected_shipments": impacted_shipments
    }

@router.post("/{disruption_id}/toggle")
def toggle_disruption_status(disruption_id: str, db: Session = Depends(get_db)):
    disruption = db.query(Disruption).filter(Disruption.disruption_id == disruption_id).first()
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")

    disruption.is_active = not disruption.is_active
    db.commit()
    return {"status": "success", "disruption_id": disruption.disruption_id, "is_active": disruption.is_active}
