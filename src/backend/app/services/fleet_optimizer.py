from typing import List, Dict, Any
from app.models.models import FleetAsset


class FleetOptimizer:
    UNDERUTILIZED_THRESHOLD = 35.0  # % utilization below which asset is "underutilized"

    CORRIDOR_DEMAND = [
        {
            "corridor": "Ahmedabad-Mumbai Expressway",
            "required_capacity": "20-30 tonnes",
            "asset_types": ["Truck", "Reefer Truck"],
        },
        {
            "corridor": "Mundra-Delhi Freight Highway",
            "required_capacity": "25-40 tonnes",
            "asset_types": ["Truck", "Container"],
        },
        {
            "corridor": "Surat-Pune Industrial Corridor",
            "required_capacity": "15-25 tonnes",
            "asset_types": ["Truck"],
        },
        {
            "corridor": "Chennai-Bengaluru Express",
            "required_capacity": "20-35 tonnes",
            "asset_types": ["Truck", "Container"],
        },
    ]

    @staticmethod
    def calculate_utilization_summary(assets: List[FleetAsset]) -> Dict[str, Any]:
        """Calculate fleet utilization KPIs."""
        total = len(assets)
        if total == 0:
            return {
                "total_assets": 0, "in_use_assets": 0, "idle_assets": 0,
                "maintenance_assets": 0, "average_utilization": 0.0,
                "underutilized_assets_count": 0,
            }

        in_use = sum(1 for a in assets if a.status == "In-Use")
        idle = sum(1 for a in assets if a.status == "Idle")
        maintenance = sum(1 for a in assets if a.status == "Maintenance")
        avg_util = round(sum(a.utilization for a in assets) / total, 1)
        underutilized = sum(1 for a in assets if a.utilization < FleetOptimizer.UNDERUTILIZED_THRESHOLD)

        return {
            "total_assets": total,
            "in_use_assets": in_use,
            "idle_assets": idle,
            "maintenance_assets": maintenance,
            "average_utilization": avg_util,
            "underutilized_assets_count": underutilized,
        }

    @staticmethod
    def generate_redeployment_recommendations(assets: List[FleetAsset]) -> List[Dict[str, Any]]:
        """Match idle/underutilized assets to high-demand corridors."""
        idle_assets = [a for a in assets if a.status == "Idle" and a.availability == "Available"]
        recommendations = []

        for i, asset in enumerate(idle_assets[:len(FleetOptimizer.CORRIDOR_DEMAND)]):
            corridor_info = FleetOptimizer.CORRIDOR_DEMAND[i % len(FleetOptimizer.CORRIDOR_DEMAND)]
            recommendations.append({
                "asset_id": asset.asset_id,
                "asset_type": asset.type,
                "location": asset.location,
                "capacity": f"{asset.capacity} {asset.capacity_unit}",
                "affected_corridor": corridor_info["corridor"],
                "required_capacity": corridor_info["required_capacity"],
                "utilization_pct": asset.utilization,
                "recommendation": f"Redeploy {asset.type} {asset.asset_id} from {asset.location} to {corridor_info['corridor']}",
                "reason": (
                    f"Asset is idle at {asset.utilization:.0f}% utilization. "
                    f"{corridor_info['corridor']} has high demand ({corridor_info['required_capacity']}) "
                    f"due to active disruptions diverting freight to land routes."
                ),
                "status": "Pending",
            })

        return recommendations
