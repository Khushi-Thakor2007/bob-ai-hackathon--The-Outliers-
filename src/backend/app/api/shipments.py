from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Shipment, RouteAlternative, SensorLog
from app.schemas.schemas import ShipmentOut, RouteAlternativeOut
from app.services.route_optimizer import RouteOptimizer

router = APIRouter(prefix="/shipments", tags=["Shipments"])

@router.get("", response_model=List[ShipmentOut])
def get_shipments(
    search: Optional[str] = Query(None, description="Search by ID, origin, destination, cargo"),
    status: Optional[str] = Query(None, description="Filter by status (In-Transit, At-Risk, Delayed, Delivered)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk (Low, Medium, High, Critical)"),
    cargo_type: Optional[str] = Query(None, description="Filter by cargo type"),
    carrier: Optional[str] = Query(None, description="Filter by carrier"),
    is_cold_chain: Optional[bool] = Query(None, description="Filter cold-chain only"),
    sort_by: Optional[str] = Query("risk_score", description="Sort by: risk_score, value, eta"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    db: Session = Depends(get_db)
):
    query = db.query(Shipment)

    if search:
        s_term = f"%{search}%"
        query = query.filter(
            (Shipment.shipment_id.ilike(s_term)) |
            (Shipment.origin.ilike(s_term)) |
            (Shipment.destination.ilike(s_term)) |
            (Shipment.cargo_type.ilike(s_term)) |
            (Shipment.carrier.ilike(s_term))
        )

    if status:
        query = query.filter(Shipment.status == status)
    if risk_level:
        query = query.filter(Shipment.risk_level == risk_level)
    if cargo_type:
        query = query.filter(Shipment.cargo_type == cargo_type)
    if carrier:
        query = query.filter(Shipment.carrier == carrier)
    if is_cold_chain is not None:
        query = query.filter(Shipment.is_cold_chain == is_cold_chain)

    # Sorting
    if sort_by == "value":
        query = query.order_by(Shipment.cargo_value.desc() if sort_order == "desc" else Shipment.cargo_value.asc())
    elif sort_by == "delay":
        query = query.order_by(Shipment.delay_hours.desc() if sort_order == "desc" else Shipment.delay_hours.asc())
    else: # default risk_score
        query = query.order_by(Shipment.current_risk_score.desc() if sort_order == "desc" else Shipment.current_risk_score.asc())

    shipments = query.all()
    return shipments

@router.get("/{shipment_id}", response_model=ShipmentOut)
def get_shipment_by_id(shipment_id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")

    # Fetch route alternatives
    alts = db.query(RouteAlternative).filter(RouteAlternative.shipment_id == shipment.shipment_id).all()
    if not alts:
        # Generate on the fly if none stored
        raw_alts = RouteOptimizer.generate_alternatives_for_shipment(shipment)
        for idx, ra in enumerate(raw_alts):
            alt_obj = RouteAlternative(
                id=idx + 1,
                shipment_id=shipment.shipment_id,
                **ra
            )
            alts.append(alt_obj)

    shipment.route_alternatives = alts

    # Fetch IoT telemetry
    if shipment.is_cold_chain:
        logs = db.query(SensorLog).filter(SensorLog.shipment_id == shipment.shipment_id).order_by(SensorLog.timestamp.desc()).limit(20).all()
        shipment.sensor_history = [
            {"timestamp": l.timestamp, "temperature": l.temperature, "humidity": l.humidity, "is_excursion": l.is_excursion}
            for l in reversed(logs)
        ]

    return shipment

@router.get("/{shipment_id}/routes", response_model=List[RouteAlternativeOut])
def get_shipment_routes(shipment_id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    alts = db.query(RouteAlternative).filter(RouteAlternative.shipment_id == shipment_id).all()
    if not alts:
        raw_alts = RouteOptimizer.generate_alternatives_for_shipment(shipment)
        return raw_alts
    return alts

@router.post("/{shipment_id}/apply-route")
def apply_mitigation_route(
    shipment_id: str,
    route_name: str = Query(..., description="Route name to apply"),
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Update shipment with mitigated values
    shipment.recommended_action = f"Applied: {route_name}"
    shipment.risk_level = "Low"
    shipment.current_risk_score = 25.0
    shipment.delay_hours = 8.0
    shipment.status = "In-Transit"
    shipment.explanation = f"Mitigation route '{route_name}' executed. Congestion bypassed; revised delay +8h."
    
    db.commit()
    return {"status": "success", "message": f"Route '{route_name}' successfully authorized for {shipment_id}."}
