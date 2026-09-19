from typing import Dict, Any
from app.models.models import Shipment


class RiskEngine:
    """
    Composite risk scoring: 4 factors each 0-100, weighted average -> final score 0-100.
    Factor weights:
      - Disruption Severity   35%
      - Cargo Sensitivity     25%
      - Delay Factor          25%
      - Priority Urgency      15%
    """

    SEVERITY_SCORE = {"Critical": 100, "High": 75, "Medium": 50, "Low": 25, None: 0}
    PRIORITY_SCORE = {"Critical": 100, "High": 75, "Normal": 40, "Low": 15}
    CARGO_SENSITIVITY = {
        "Vaccines": 95, "Pharmaceuticals": 90, "Medical Devices": 85,
        "Electronics": 80, "Semiconductors": 85, "Perishables": 75,
        "Automotive Parts": 60, "Industrial Machinery": 50, "Chemicals": 65,
        "Textile": 30, "Furniture": 25, "General Cargo": 20,
    }

    @staticmethod
    def compute_risk_score(shipment: Shipment, disruption_severity: str = None, delay_hours: float = 0.0) -> Dict[str, Any]:
        """Compute a composite risk score 0-100 for a shipment."""
        # Factor 1: Disruption severity
        f1 = RiskEngine.SEVERITY_SCORE.get(disruption_severity, 0)

        # Factor 2: Cargo sensitivity
        f2 = RiskEngine.CARGO_SENSITIVITY.get(shipment.cargo_type, 40)

        # Factor 3: Delay factor (normalized to 0-100, max at 72+ hours)
        f3 = min(100.0, (delay_hours / 72.0) * 100.0)

        # Factor 4: Priority urgency
        f4 = RiskEngine.PRIORITY_SCORE.get(shipment.priority, 40)

        # Weighted composite
        score = (f1 * 0.35) + (f2 * 0.25) + (f3 * 0.25) + (f4 * 0.15)
        score = round(min(100.0, max(0.0, score)), 1)

        # Map score to level
        if score >= 80:
            level = "Critical"
        elif score >= 60:
            level = "High"
        elif score >= 35:
            level = "Medium"
        else:
            level = "Low"

        return {
            "risk_score": score,
            "risk_level": level,
            "factors": {
                "disruption_severity_score": f1,
                "cargo_sensitivity_score": f2,
                "delay_factor_score": round(f3, 1),
                "priority_urgency_score": f4,
            }
        }

    @staticmethod
    def get_recommended_action(risk_level: str, cargo_type: str, mode: str) -> str:
        """Generate an operational recommendation string based on risk level."""
        if risk_level == "Critical":
            if cargo_type in ["Vaccines", "Pharmaceuticals", "Medical Devices"]:
                return "IMMEDIATE: Expedite via air freight. Preserve cold-chain integrity. Notify consignee."
            return "IMMEDIATE: Activate Alternate Route B (Multimodal Rail Bypass) or emergency air bridge."
        elif risk_level == "High":
            return "Reroute via Alternate Route A (Express Highway) or switch to secondary carrier."
        elif risk_level == "Medium":
            return "Monitor closely. Prepare contingency route. Notify carrier of possible delay."
        else:
            return "Normal monitoring. No immediate action required."

    @staticmethod
    def get_explanation(shipment: Shipment, risk_level: str, disruption_name: str, delay_hours: float) -> str:
        """Generate a human-readable explanation of the risk assessment."""
        if risk_level in ["Critical", "High"] and disruption_name and disruption_name != "None":
            return (
                f"Shipment {shipment.shipment_id} ({shipment.cargo_type}) is {risk_level.lower()} risk "
                f"due to active disruption '{disruption_name}'. Estimated delay: {delay_hours:.0f} hours. "
                f"Cargo value ${shipment.cargo_value:,.0f} is exposed. "
                f"Priority: {shipment.priority}. Immediate rerouting recommended."
            )
        elif risk_level in ["Critical", "High"]:
            return (
                f"Shipment {shipment.shipment_id} ({shipment.cargo_type}) has elevated risk from corridor congestion "
                f"and {delay_hours:.0f}h delay. Cargo value ${shipment.cargo_value:,.0f}."
            )
        return (
            f"Shipment {shipment.shipment_id} ({shipment.cargo_type}) is on schedule with {risk_level.lower()} risk. "
            f"No immediate action required."
        )
