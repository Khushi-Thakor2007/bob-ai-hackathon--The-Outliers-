from typing import List, Dict, Any
from app.models.models import Shipment
from datetime import datetime, timedelta
import random


class RouteOptimizer:
    """
    Generates 3-4 alternative route options for a disrupted shipment.
    Each option has: route_name, carrier_name, mode, distance_km,
    estimated_eta, delay_hours, cost_delta_pct, risk_level,
    recommendation_score, is_recommended, explanation.
    """

    ROUTES = [
        {
            "route_name": "Alternate Route A (Express Highway)",
            "mode": "Road",
            "distance_multiplier": 1.10,
            "delay_hours": 12.0,
            "cost_delta_pct": 8.0,
            "risk_level": "Medium",
            "recommendation_score": 72.0,
            "is_recommended": False,
            "explanation": "Express toll highway via NH-48 bypasses port congestion with +10% distance but faster clearance. Delay +12h vs baseline.",
        },
        {
            "route_name": "Alternate Route B (Multimodal Rail Bypass)",
            "mode": "Multimodal",
            "distance_multiplier": 1.05,
            "delay_hours": 8.0,
            "cost_delta_pct": 5.0,
            "risk_level": "Low",
            "recommendation_score": 91.0,
            "is_recommended": True,
            "explanation": "Rail-road intermodal shifts cargo to western dedicated freight corridor, cutting maritime congestion exposure. Optimal cost/delay balance.",
        },
        {
            "route_name": "Emergency Air Freight",
            "mode": "Air",
            "distance_multiplier": 0.30,
            "delay_hours": 2.0,
            "cost_delta_pct": 340.0,
            "risk_level": "Low",
            "recommendation_score": 55.0,
            "is_recommended": False,
            "explanation": "Direct air cargo from nearest hub. Eliminates port delay but cost premium is 340%. Suitable only for Critical priority pharma/electronics.",
        },
        {
            "route_name": "Secondary Port Diversion (Mundra)",
            "mode": "Sea",
            "distance_multiplier": 1.15,
            "delay_hours": 24.0,
            "cost_delta_pct": 12.0,
            "risk_level": "Medium",
            "recommendation_score": 62.0,
            "is_recommended": False,
            "explanation": "Divert container vessel to Mundra Port (alternate Gujarat gateway). Adds 24h transit but avoids JNPT strike entirely.",
        },
    ]

    CARRIERS = [
        "BlueDart Express", "DHL Supply Chain", "Gati KWE", "FedEx Freight",
        "Maersk Logistics", "TCI Express", "XPO Logistics", "DB Schenker"
    ]

    @staticmethod
    def generate_alternatives_for_shipment(shipment: Shipment) -> List[Dict[str, Any]]:
        """Return route alternatives for a given shipment."""
        base_distance = 800.0  # fallback km
        seed = sum(ord(c) for c in shipment.shipment_id)
        rng = random.Random(seed)

        results = []
        for route in RouteOptimizer.ROUTES:
            eta_dt = datetime.utcnow() + timedelta(hours=route["delay_hours"] + 24)
            eta_str = eta_dt.strftime("%Y-%m-%d %H:%M UTC")
            carrier = rng.choice(RouteOptimizer.CARRIERS)
            distance = round(base_distance * route["distance_multiplier"], 0)

            results.append({
                "route_name": route["route_name"],
                "carrier_name": carrier,
                "mode": route["mode"],
                "distance_km": distance,
                "estimated_eta": eta_str,
                "delay_hours": route["delay_hours"],
                "cost_delta_pct": route["cost_delta_pct"],
                "risk_level": route["risk_level"],
                "recommendation_score": route["recommendation_score"],
                "is_recommended": route["is_recommended"],
                "explanation": route["explanation"],
            })

        return results
