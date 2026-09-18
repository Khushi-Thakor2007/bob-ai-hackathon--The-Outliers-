from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.schemas import SimulationResponse
from app.services.simulation_engine import SimulationEngine

router = APIRouter(prefix="/simulation", tags=["Demo Simulation"])

@router.post("/port-strike", response_model=SimulationResponse)
def trigger_port_strike_simulation(db: Session = Depends(get_db)):
    result = SimulationEngine.simulate_port_strike(db)
    return SimulationResponse(
        status="success",
        scenario="port_strike",
        message="JNPT Port Strike activated. 17 shipments impacted, $3.8M cargo value exposed. Fleet redeployments and route alternatives generated.",
        impact_summary=result
    )

@router.post("/temperature-excursion", response_model=SimulationResponse)
def trigger_temperature_excursion_simulation(
    shipment_id: Optional[str] = Query("SHP-221", description="Target cold-chain shipment"),
    db: Session = Depends(get_db)
):
    result = SimulationEngine.simulate_temperature_excursion(db, target_shipment_id=shipment_id)
    return SimulationResponse(
        status="success",
        scenario="temperature_excursion",
        message=f"Critical temperature excursion injected into {shipment_id}. Current temp: 10.1°C (Allowed max: 8.0°C).",
        impact_summary=result
    )

@router.post("/reset", response_model=SimulationResponse)
def reset_simulation(db: Session = Depends(get_db)):
    result = SimulationEngine.reset_simulation(db)
    return SimulationResponse(
        status="success",
        scenario="reset",
        message=result["message"],
        impact_summary={"status": "baseline"}
    )
