import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed.seed_data import seed_database
from app.api import (
    dashboard_router,
    shipments_router,
    disruptions_router,
    fleet_router,
    cold_chain_router,
    bob_router,
    simulation_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables are created and seed realistic demo data
    print("Initializing Database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
        
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Supply Chain Disruption Assistant & Fleet Utilisation Optimizer API Control Tower",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for hackathon local dev & testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(shipments_router, prefix=settings.API_V1_STR)
app.include_router(disruptions_router, prefix=settings.API_V1_STR)
app.include_router(fleet_router, prefix=settings.API_V1_STR)
app.include_router(cold_chain_router, prefix=settings.API_V1_STR)
app.include_router(bob_router, prefix=settings.API_V1_STR)
app.include_router(simulation_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to Supply Chain Disruption Assistant & Fleet Utilisation Optimizer Control Tower API",
        "docs": "/docs",
        "health": "/health"
    }
