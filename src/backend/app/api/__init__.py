from app.api.dashboard import router as dashboard_router
from app.api.shipments import router as shipments_router
from app.api.disruptions import router as disruptions_router
from app.api.fleet import router as fleet_router
from app.api.cold_chain import router as cold_chain_router
from app.api.bob import router as bob_router
from app.api.simulation import router as simulation_router

__all__ = [
    "dashboard_router",
    "shipments_router",
    "disruptions_router",
    "fleet_router",
    "cold_chain_router",
    "bob_router",
    "simulation_router"
]
