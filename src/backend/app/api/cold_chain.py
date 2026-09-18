from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.models import Shipment, SensorLog, Alert, ColdChainRule
from app.schemas.schemas import AlertOut, ShipmentOut
from app.services.cold_chain_engine import ColdChainEngine

router = APIRouter(prefix="/cold-chain", tags=["Cold Chain"])

@router.get("/alerts", response_model=List[AlertOut])
def get_cold_chain_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.category == "Cold Chain").order_by(Alert.detected_at.desc()).all()
    return alerts

@router.get("/shipments", response_model=List[ShipmentOut])
def get_cold_chain_shipments(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).filter(Shipment.is_cold_chain == True).all()
    return shipments

@router.get("/{shipment_id}/temperature")
def get_temperature_history(shipment_id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    sensor_logs = db.query(SensorLog).filter(SensorLog.shipment_id == shipment_id).order_by(SensorLog.timestamp.asc()).all()
    analysis = ColdChainEngine.analyze_sensor_stream(shipment, sensor_logs)

    telemetry = [
        {
            "id": log.id,
            "sensor_id": log.sensor_id,
            "timestamp": log.timestamp.strftime("%H:%M:%S"),
            "full_timestamp": log.timestamp.isoformat(),
            "temperature": log.temperature,
            "humidity": log.humidity,
            "battery_pct": log.battery_pct,
            "latitude": log.latitude,
            "longitude": log.longitude,
            "is_excursion": log.is_excursion
        }
        for log in sensor_logs
    ]

    return {
        "shipment": {
            "shipment_id": shipment.shipment_id,
            "cargo_type": shipment.cargo_type,
            "origin": shipment.origin,
            "destination": shipment.destination,
            "current_location": shipment.current_location,
            "carrier": shipment.carrier,
            "status": shipment.status,
            "required_min": shipment.required_min_temperature,
            "required_max": shipment.required_max_temperature,
            "current_temp": shipment.current_temperature
        },
        "analysis": analysis,
        "telemetry_points": telemetry
    }
