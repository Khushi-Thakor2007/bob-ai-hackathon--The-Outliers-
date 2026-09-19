import math
from typing import Tuple
from app.models.models import Shipment, Disruption

# Known route corridors with their key waypoints/locations
CORRIDOR_KEYWORDS = {
    "JNPT": ["mumbai", "jnpt", "nhava sheva", "navi mumbai"],
    "Mundra": ["mundra", "gujarat", "kandla"],
    "Ahmedabad": ["ahmedabad", "gujarat"],
    "Surat": ["surat", "south gujarat"],
    "Delhi": ["delhi", "ncr", "gurgaon", "noida", "faridabad"],
    "Chennai": ["chennai", "madras", "tamil nadu"],
    "Bangalore": ["bangalore", "bengaluru", "karnataka"],
    "Hyderabad": ["hyderabad", "telangana"],
    "Kolkata": ["kolkata", "calcutta", "west bengal", "haldia"],
}

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in km between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class DisruptionEngine:
    @staticmethod
    def is_shipment_impacted(shipment: Shipment, disruption: Disruption) -> Tuple[bool, float, str]:
        """
        Determines whether a shipment is affected by a disruption.
        Returns (is_impacted, delay_hours_added, reason_string)
        """
        if not disruption.is_active:
            return False, 0.0, ""

        # Severity-based delay lookup
        severity_delay = {
            "Critical": 48.0,
            "High": 32.0,
            "Medium": 18.0,
            "Low": 8.0,
        }
        base_delay = severity_delay.get(disruption.severity, 16.0)

        # --- Method 1: Geospatial proximity check ---
        geo_impact = False
        geo_reason = ""
        if (disruption.latitude and disruption.longitude):
            check_points = []
            if shipment.origin_lat and shipment.origin_lon:
                check_points.append(("origin", shipment.origin_lat, shipment.origin_lon))
            if shipment.dest_lat and shipment.dest_lon:
                check_points.append(("destination", shipment.dest_lat, shipment.dest_lon))
            if shipment.current_lat and shipment.current_lon:
                check_points.append(("current location", shipment.current_lat, shipment.current_lon))

            radius = disruption.radius_km or 200.0
            for point_name, lat, lon in check_points:
                dist = haversine_km(lat, lon, disruption.latitude, disruption.longitude)
                if dist <= radius:
                    geo_impact = True
                    geo_reason = (
                        f"Shipment {point_name} ({lat:.2f},{lon:.2f}) is within "
                        f"{dist:.0f} km of disruption epicentre ({disruption.name}) — radius {radius:.0f} km."
                    )
                    break

        # --- Method 2: Corridor keyword match ---
        kw_impact = False
        kw_reason = ""
        disruption_loc_lower = (disruption.location or "").lower()
        disruption_name_lower = (disruption.name or "").lower()
        shipment_fields = " ".join(filter(None, [
            shipment.origin, shipment.destination,
            shipment.current_location, shipment.carrier,
            shipment.disruption_exposure
        ])).lower()

        for hub, keywords in CORRIDOR_KEYWORDS.items():
            hub_in_disruption = any(kw in disruption_loc_lower or kw in disruption_name_lower for kw in keywords)
            hub_in_shipment = any(kw in shipment_fields for kw in keywords)
            if hub_in_disruption and hub_in_shipment:
                kw_impact = True
                kw_reason = f"Shipment passes through {hub} corridor which is affected by {disruption.name}."
                break

        is_impacted = geo_impact or kw_impact
        reason = geo_reason or kw_reason

        if is_impacted:
            # Mode-based delay multiplier
            mode_mult = {"Air": 0.5, "Sea": 1.2, "Road": 1.0, "Multimodal": 0.9}.get(
                shipment.mode or "Road", 1.0
            )
            final_delay = round(base_delay * mode_mult, 1)
            return True, final_delay, reason

        return False, 0.0, ""
