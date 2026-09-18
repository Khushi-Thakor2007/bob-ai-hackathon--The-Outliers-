from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import FleetAsset, RedeploymentRecommendation
from app.schemas.schemas import FleetAssetOut, RedeploymentRecommendationOut, FleetUtilisationSummary
from app.services.fleet_optimizer import FleetOptimizer

router = APIRouter(prefix="/fleet", tags=["Fleet"])

@router.get("", response_model=List[FleetAssetOut])
def get_fleet_assets(
    asset_type: Optional[str] = Query(None, description="Filter by type (Truck, Container, Reefer, Vessel)"),
    status: Optional[str] = Query(None, description="Filter by status (Idle, In-Use, Maintenance)"),
    db: Session = Depends(get_db)
):
    query = db.query(FleetAsset)
    if asset_type:
        query = query.filter(FleetAsset.type.ilike(f"%{asset_type}%"))
    if status:
        query = query.filter(FleetAsset.status == status)
    return query.all()

@router.get("/summary", response_model=FleetUtilisationSummary)
def get_fleet_summary(db: Session = Depends(get_db)):
    assets = db.query(FleetAsset).all()
    metrics = FleetOptimizer.calculate_utilization_summary(assets)
    recs = db.query(RedeploymentRecommendation).all()

    return FleetUtilisationSummary(
        total_assets=metrics["total_assets"],
        in_use_assets=metrics["in_use_assets"],
        idle_assets=metrics["idle_assets"],
        maintenance_assets=metrics["maintenance_assets"],
        average_utilization=metrics["average_utilization"],
        underutilized_assets_count=metrics["underutilized_assets_count"],
        assets=assets,
        redeployment_recommendations=recs
    )

@router.get("/redeployment", response_model=List[RedeploymentRecommendationOut])
def get_redeployment_recommendations(db: Session = Depends(get_db)):
    recs = db.query(RedeploymentRecommendation).all()
    if not recs:
        assets = db.query(FleetAsset).all()
        fresh = FleetOptimizer.generate_redeployment_recommendations(assets)
        for r in fresh:
            db.add(RedeploymentRecommendation(**r))
        db.commit()
        return db.query(RedeploymentRecommendation).all()
    return recs

@router.post("/redeploy/{asset_id}")
def redeploy_asset(asset_id: str, corridor: Optional[str] = None, db: Session = Depends(get_db)):
    asset = db.query(FleetAsset).filter(FleetAsset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Fleet asset {asset_id} not found")

    rec = db.query(RedeploymentRecommendation).filter(RedeploymentRecommendation.asset_id == asset_id).first()
    target_corr = corridor or (rec.affected_corridor if rec else "Emergency Relief Corridor")

    asset.status = "In-Use"
    asset.availability = "Dispatched"
    asset.current_route = target_corr
    asset.utilization = 85.0

    if rec:
        rec.status = "Redeployed"

    db.commit()

    return {
        "status": "success",
        "message": f"Asset {asset_id} successfully redeployed to {target_corr}. Status changed to In-Use (85% utilization)."
    }
