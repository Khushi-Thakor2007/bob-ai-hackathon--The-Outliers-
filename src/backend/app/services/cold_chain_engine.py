from typing import List, Dict, Any, Optional
from app.models.models import Shipment, SensorLog


CARGO_TEMP_RULES = {
    "Vaccines": {"min": 2.0, "max": 8.0, "max_excursion_min": 30},
    "Pharmaceuticals": {"min": 2.0, "max": 15.0, "max_excursion_min": 60},
    "Medical Devices": {"min": -5.0, "max": 25.0, "max_excursion_min": 120},
    "Perishables": {"min": 0.0, "max": 6.0, "max_excursion_min": 45},
    "Frozen Goods": {"min": -25.0, "max": -15.0, "max_excursion_min": 20},
    "Chemicals": {"min": 5.0, "max": 30.0, "max_excursion_min": 90},
}


class ColdChainEngine:
    @staticmethod
    def get_temp_rule(cargo_type: str) -> Dict[str, Any]:
        return CARGO_TEMP_RULES.get(cargo_type, {"min": 0.0, "max": 25.0, "max_excursion_min": 60})

    @staticmethod
    def analyze_sensor_stream(shipment: Shipment, logs: List[SensorLog]) -> Dict[str, Any]:
        """
        Analyze a stream of sensor readings for excursions.
        Returns a structured analysis dict.
        """
        if not logs:
            return {
                "has_excursion": False,
                "excursion_count": 0,
                "current_temperature": shipment.current_temperature,
                "min_allowed": shipment.required_min_temperature,
                "max_allowed": shipment.required_max_temperature,
                "severity": "Nominal",
                "excursion_detail": "No sensor data available.",
            }

        rule = ColdChainEngine.get_temp_rule(shipment.cargo_type or "")
        min_t = shipment.required_min_temperature or rule["min"]
        max_t = shipment.required_max_temperature or rule["max"]
        current_temp = logs[-1].temperature if logs else shipment.current_temperature

        excursion_logs = [l for l in logs if l.is_excursion]
        has_excursion = len(excursion_logs) > 0

        # Severity determination
        if has_excursion:
            max_deviation = max(
                abs(l.temperature - max_t) if l.temperature > max_t else abs(min_t - l.temperature)
                for l in excursion_logs
            )
            if max_deviation > 5.0:
                severity = "Critical"
            elif max_deviation > 2.0:
                severity = "High"
            else:
                severity = "Medium"
        else:
            severity = "Nominal"

        excursion_minutes = len(excursion_logs) * 5  # each log = ~5 min interval

        return {
            "has_excursion": has_excursion,
            "excursion_count": len(excursion_logs),
            "excursion_minutes": excursion_minutes,
            "current_temperature": round(current_temp, 2) if current_temp is not None else None,
            "min_allowed": min_t,
            "max_allowed": max_t,
            "severity": severity,
            "excursion_detail": (
                f"{len(excursion_logs)} readings out of range ({excursion_minutes} min total)."
                if has_excursion else "All readings within specification."
            ),
        }

    @staticmethod
    def classify_excursion(temperature: float, cargo_type: str) -> str:
        """Return a human-readable excursion classification."""
        rule = ColdChainEngine.get_temp_rule(cargo_type)
        if temperature > rule["max"]:
            deviation = temperature - rule["max"]
        elif temperature < rule["min"]:
            deviation = rule["min"] - temperature
        else:
            return "Nominal"

        if deviation > 5.0:
            return "Critical Excursion"
        elif deviation > 2.0:
            return "High Excursion"
        else:
            return "Minor Excursion"
