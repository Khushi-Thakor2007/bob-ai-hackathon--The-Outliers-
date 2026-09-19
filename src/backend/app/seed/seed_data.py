"""
Seed data for Supply Chain Disruption Assistant & Fleet Utilisation Optimizer.
Generates realistic demo data for the Indian logistics corridor.
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import (
    Disruption, Shipment, FleetAsset, SensorLog,
    Alert, ColdChainRule, RouteAlternative, RedeploymentRecommendation
)
from app.services.risk_engine import RiskEngine
from app.services.disruption_engine import DisruptionEngine


# ------------------------------------------------------------------
# Seed guard: run only if fewer than 50 shipments exist
# ------------------------------------------------------------------
def seed_database(db: Session):
    if db.query(Shipment).count() >= 50:
        print("Database already seeded. Skipping.")
        return

    print("Seeding database with demo data...")
    _clear_all(db)
    _seed_cold_chain_rules(db)
    disruptions = _seed_disruptions(db)
    shipments = _seed_shipments(db, disruptions)
    _seed_fleet(db)
    _seed_sensor_logs(db, shipments)
    _seed_alerts(db, shipments)
    db.commit()
    print(f"Seeded: {len(shipments)} shipments, {len(disruptions)} disruptions.")


def _clear_all(db: Session):
    db.query(Alert).delete()
    db.query(SensorLog).delete()
    db.query(RouteAlternative).delete()
    db.query(RedeploymentRecommendation).delete()
    db.query(Shipment).delete()
    db.query(FleetAsset).delete()
    db.query(Disruption).delete()
    db.query(ColdChainRule).delete()
    db.commit()


def _seed_cold_chain_rules(db: Session):
    rules = [
        ColdChainRule(cargo_type="Vaccines", min_temperature=2.0, max_temperature=8.0,
                      max_excursion_minutes=30, description="WHO cold-chain protocol for biological vaccines"),
        ColdChainRule(cargo_type="Pharmaceuticals", min_temperature=2.0, max_temperature=15.0,
                      max_excursion_minutes=60, description="Standard pharma cold-chain GMP requirement"),
        ColdChainRule(cargo_type="Perishables", min_temperature=0.0, max_temperature=6.0,
                      max_excursion_minutes=45, description="Fresh produce / food logistics"),
        ColdChainRule(cargo_type="Frozen Goods", min_temperature=-25.0, max_temperature=-15.0,
                      max_excursion_minutes=20, description="Frozen food and ice cream"),
        ColdChainRule(cargo_type="Medical Devices", min_temperature=-5.0, max_temperature=25.0,
                      max_excursion_minutes=120, description="Temperature-sensitive medical equipment"),
    ]
    db.add_all(rules)
    db.commit()


def _seed_disruptions(db: Session):
    now = datetime.utcnow()
    disruptions_data = [
        dict(disruption_id="DISRUPT-001", type="Port Strike", name="JNPT Port Strike",
             location="Nhava Sheva, Mumbai", latitude=18.954, longitude=72.952,
             severity="Critical", start_time=now - timedelta(hours=18),
             expected_duration="72-96 hours", affected_area="Mumbai Port Zone, JNPT Container Terminal",
             radius_km=250.0,
             description="Industrial action by dock workers union at Jawaharlal Nehru Port Trust. "
                         "All container handling operations suspended. 3 vessels at anchor.",
             is_active=True),
        dict(disruption_id="DISRUPT-002", type="Weather Event", name="Cyclone Biparjoy Aftermath",
             location="Kutch, Gujarat", latitude=23.25, longitude=69.67,
             severity="High", start_time=now - timedelta(hours=6),
             expected_duration="24-36 hours", affected_area="Kutch, Mundra Port, Kandla Port",
             radius_km=180.0,
             description="Post-cyclone road damage on NH-41 affecting Mundra port access. "
                         "Significant flooding reported near Anjar junction.",
             is_active=True),
        dict(disruption_id="DISRUPT-003", type="Customs Delay", name="Chennai Customs Inspection Backlog",
             location="Chennai Port, Tamil Nadu", latitude=13.09, longitude=80.29,
             severity="Medium", start_time=now - timedelta(hours=30),
             expected_duration="48 hours", affected_area="Chennai Port Container Terminal",
             radius_km=80.0,
             description="Enhanced scanning protocols due to contraband detection alert. "
                         "All import containers subject to 100% physical verification.",
             is_active=True),
        dict(disruption_id="DISRUPT-004", type="Infrastructure", name="NH-48 Bridge Closure",
             location="Pune, Maharashtra", latitude=18.52, longitude=73.86,
             severity="Medium", start_time=now - timedelta(hours=12),
             expected_duration="36 hours", affected_area="NH-48 Mumbai-Pune section",
             radius_km=100.0,
             description="Emergency structural inspection of Khopoli viaduct. "
                         "HCV traffic diverted via Tamhini Ghat (adds 90 min transit time).",
             is_active=False),
        dict(disruption_id="DISRUPT-005", type="Labour Unrest", name="Trucker Strike — Rajasthan",
             location="Jaipur, Rajasthan", latitude=26.91, longitude=75.79,
             severity="Low", start_time=now - timedelta(hours=48),
             expected_duration="Resolved", affected_area="Rajasthan state highways",
             radius_km=150.0,
             description="All-India transport union strike in Rajasthan. Strike called off "
                         "after government fuel subsidy announcement.",
             is_active=False),
    ]
    objs = [Disruption(**d) for d in disruptions_data]
    db.add_all(objs)
    db.commit()
    return objs


CARRIERS = [
    "BlueDart Express", "DHL Supply Chain", "Gati KWE", "FedEx Freight",
    "Maersk India", "TCI Express", "XPO Logistics", "DB Schenker",
    "Safexpress", "DTDC Freight", "Delhivery", "Rivigo"
]

CARGO_TYPES = [
    ("Vaccines", True, 2.0, 8.0),
    ("Pharmaceuticals", True, 2.0, 15.0),
    ("Electronics", False, None, None),
    ("Semiconductors", False, None, None),
    ("Automotive Parts", False, None, None),
    ("Perishables", True, 0.0, 6.0),
    ("Industrial Machinery", False, None, None),
    ("Chemicals", False, None, None),
    ("Textile", False, None, None),
    ("Medical Devices", True, -5.0, 25.0),
    ("General Cargo", False, None, None),
    ("Furniture", False, None, None),
]

LOCATIONS = [
    ("Mumbai", 19.076, 72.877),
    ("Delhi", 28.704, 77.102),
    ("Ahmedabad", 23.022, 72.571),
    ("Chennai", 13.082, 80.27),
    ("Kolkata", 22.572, 88.363),
    ("Bengaluru", 12.971, 77.594),
    ("Hyderabad", 17.385, 78.486),
    ("Pune", 18.520, 73.856),
    ("Surat", 21.170, 72.831),
    ("Jaipur", 26.913, 75.787),
    ("Mundra", 22.839, 69.726),
    ("Vadodara", 22.307, 73.181),
    ("Nagpur", 21.145, 79.082),
    ("Ludhiana", 30.900, 75.857),
    ("Kochi", 9.939, 76.27),
    ("Visakhapatnam", 17.686, 83.218),
    ("Bhopal", 23.259, 77.411),
    ("Chandigarh", 30.733, 76.779),
]

PRIORITIES = ["Critical", "High", "Normal", "Low"]
MODES = ["Road", "Air", "Sea", "Multimodal"]
STATUSES = ["In-Transit", "In-Transit", "In-Transit", "In-Transit", "Delayed", "At-Risk", "Delivered"]


def _make_shipment(idx: int, disruptions: list, rng: random.Random) -> dict:
    num = 100 + idx
    cargo_info = rng.choice(CARGO_TYPES)
    cargo_type, is_cold, min_t, max_t = cargo_info

    origin_t = rng.choice(LOCATIONS)
    dest_t = rng.choice([l for l in LOCATIONS if l[0] != origin_t[0]])
    current_t = rng.choice(LOCATIONS)

    carrier = rng.choice(CARRIERS)
    mode = rng.choice(MODES)
    priority = rng.choice(PRIORITIES)
    status = rng.choice(STATUSES)
    cargo_value = round(rng.uniform(50_000, 2_000_000), 2)
    weight_kg = round(rng.uniform(500, 25_000), 1)
    eta_offset = rng.randint(1, 14)
    eta_dt = datetime.utcnow() + timedelta(days=eta_offset)
    eta_str = eta_dt.strftime("%Y-%m-%d %H:%M UTC")

    delay = 0.0
    disruption_exp = "None"

    # Check against active disruptions
    active = [d for d in disruptions if d.is_active]
    if active and rng.random() < 0.55:
        chosen_d = rng.choice(active)
        # Roughly 60% chance it's in the affected corridor
        if rng.random() < 0.6:
            disruption_exp = chosen_d.name
            sev_delay = {"Critical": 48.0, "High": 32.0, "Medium": 18.0, "Low": 8.0}
            delay = sev_delay.get(chosen_d.severity, 16.0) * rng.uniform(0.5, 1.5)
            delay = round(delay, 1)
            status = "At-Risk" if status == "In-Transit" else status

    risk_data = RiskEngine.compute_risk_score(
        type("MockShipment", (), {"cargo_type": cargo_type, "priority": priority, "mode": mode})(),
        disruption_exp if disruption_exp != "None" else None,
        delay
    )
    risk_score = risk_data["risk_score"]
    risk_level = risk_data["risk_level"]

    current_temp = None
    if is_cold:
        base = (min_t + max_t) / 2 if min_t is not None and max_t is not None else 5.0
        current_temp = round(base + rng.uniform(-1.0, 1.5), 1)

    rec_action = RiskEngine.get_recommended_action(risk_level, cargo_type, mode)
    expl = (
        f"Shipment SHP-{num} ({cargo_type}) has {risk_level.lower()} risk. "
        f"{'Disruption: ' + disruption_exp + '. ' if disruption_exp != 'None' else ''}"
        f"{'Delay: ' + str(delay) + 'h. ' if delay > 0 else ''}"
        f"Cargo value: ${cargo_value:,.0f}."
    )

    return dict(
        shipment_id=f"SHP-{num}",
        origin=origin_t[0],
        destination=dest_t[0],
        current_location=current_t[0],
        carrier=carrier,
        mode=mode,
        cargo_type=cargo_type,
        cargo_value=cargo_value,
        weight_kg=weight_kg,
        status=status,
        priority=priority,
        eta=eta_str,
        delay_hours=delay,
        risk_level=risk_level,
        current_risk_score=risk_score,
        disruption_exposure=disruption_exp,
        recommended_action=rec_action,
        explanation=expl,
        is_cold_chain=is_cold,
        required_min_temperature=min_t,
        required_max_temperature=max_t,
        current_temperature=current_temp,
        origin_lat=origin_t[1],
        origin_lon=origin_t[2],
        dest_lat=dest_t[1],
        dest_lon=dest_t[2],
        current_lat=current_t[1],
        current_lon=current_t[2],
    )


def _seed_shipments(db: Session, disruptions: list) -> list:
    rng = random.Random(42)
    shipments = []
    for i in range(56):
        data = _make_shipment(i, disruptions, rng)
        s = Shipment(**data)
        s.route_alternatives = []
        s.sensor_history = []
        db.add(s)
        shipments.append(s)
    db.commit()
    return shipments


def _seed_fleet(db: Session):
    rng = random.Random(99)
    fleet_data = [
        dict(asset_id="TRK-001", type="Truck", license_plate="GJ01AB1234",
             location="Ahmedabad", latitude=23.022, longitude=72.571,
             status="Idle", availability="Available", capacity=25.0, capacity_unit="tonnes",
             utilization=12.0, current_route=None),
        dict(asset_id="TRK-002", type="Truck", license_plate="MH02CD5678",
             location="Mumbai", latitude=19.076, longitude=72.877,
             status="In-Use", availability="Dispatched", capacity=20.0, capacity_unit="tonnes",
             utilization=85.0, current_route="Mumbai-Pune Expressway"),
        dict(asset_id="TRK-003", type="Reefer Truck", license_plate="GJ05EF9012",
             location="Vadodara", latitude=22.307, longitude=73.181,
             status="Idle", availability="Available", capacity=15.0, capacity_unit="tonnes",
             utilization=8.0, current_route=None),
        dict(asset_id="TRK-004", type="Truck", license_plate="DL03GH3456",
             location="Delhi", latitude=28.704, longitude=77.102,
             status="In-Use", availability="Dispatched", capacity=30.0, capacity_unit="tonnes",
             utilization=92.0, current_route="Delhi-Jaipur Highway"),
        dict(asset_id="TRK-005", type="Reefer Truck", license_plate="TN01IJ7890",
             location="Chennai", latitude=13.082, longitude=80.27,
             status="Idle", availability="Available", capacity=12.0, capacity_unit="tonnes",
             utilization=5.0, current_route=None),
        dict(asset_id="TRK-006", type="Truck", license_plate="KA02KL2345",
             location="Bengaluru", latitude=12.971, longitude=77.594,
             status="Maintenance", availability="Unavailable", capacity=28.0, capacity_unit="tonnes",
             utilization=0.0, current_route=None),
        dict(asset_id="TRK-007", type="Truck", license_plate="GJ15MN6789",
             location="Surat", latitude=21.170, longitude=72.831,
             status="Idle", availability="Available", capacity=22.0, capacity_unit="tonnes",
             utilization=18.0, current_route=None),
        dict(asset_id="TRK-008", type="Truck", license_plate="MH14OP1234",
             location="Pune", latitude=18.520, longitude=73.856,
             status="In-Use", availability="Dispatched", capacity=25.0, capacity_unit="tonnes",
             utilization=78.0, current_route="Pune-Hyderabad NH-65"),
        dict(asset_id="CTR-001", type="Container", license_plate=None,
             location="Mundra Port", latitude=22.839, longitude=69.726,
             status="Idle", availability="Available", capacity=30.0, capacity_unit="tonnes",
             utilization=0.0, current_route=None),
        dict(asset_id="CTR-002", type="Container", license_plate=None,
             location="JNPT, Mumbai", latitude=18.954, longitude=72.952,
             status="In-Use", availability="Dispatched", capacity=30.0, capacity_unit="tonnes",
             utilization=100.0, current_route="JNPT-Kolkata Sea Lane"),
        dict(asset_id="CTR-003", type="Container", license_plate=None,
             location="Chennai Port", latitude=13.09, longitude=80.29,
             status="Idle", availability="Available", capacity=30.0, capacity_unit="tonnes",
             utilization=15.0, current_route=None),
        dict(asset_id="CTR-004", type="Reefer Container", license_plate=None,
             location="Kochi Port", latitude=9.939, longitude=76.27,
             status="Idle", availability="Available", capacity=25.0, capacity_unit="tonnes",
             utilization=0.0, current_route=None),
        dict(asset_id="VES-001", type="Vessel", license_plate=None,
             location="Arabian Sea (en route Mumbai)", latitude=18.5, longitude=70.8,
             status="In-Use", availability="Dispatched", capacity=2000.0, capacity_unit="tonnes",
             utilization=75.0, current_route="Dubai-Mumbai JNPT"),
        dict(asset_id="VES-002", type="Vessel", license_plate=None,
             location="Bay of Bengal", latitude=14.0, longitude=82.0,
             status="In-Use", availability="Dispatched", capacity=1800.0, capacity_unit="tonnes",
             utilization=88.0, current_route="Singapore-Chennai"),
        dict(asset_id="TRK-009", type="Truck", license_plate="WB02QR4567",
             location="Kolkata", latitude=22.572, longitude=88.363,
             status="Idle", availability="Available", capacity=20.0, capacity_unit="tonnes",
             utilization=22.0, current_route=None),
        dict(asset_id="TRK-010", type="Reefer Truck", license_plate="RJ14ST8901",
             location="Jaipur", latitude=26.913, longitude=75.787,
             status="Idle", availability="Available", capacity=18.0, capacity_unit="tonnes",
             utilization=10.0, current_route=None),
        dict(asset_id="TRK-011", type="Truck", license_plate="AP09UV2345",
             location="Hyderabad", latitude=17.385, longitude=78.486,
             status="In-Use", availability="Dispatched", capacity=24.0, capacity_unit="tonnes",
             utilization=68.0, current_route="Hyderabad-Bengaluru NH-44"),
        dict(asset_id="TRK-012", type="Truck", license_plate="MP07WX6789",
             location="Bhopal", latitude=23.259, longitude=77.411,
             status="Maintenance", availability="Unavailable", capacity=20.0, capacity_unit="tonnes",
             utilization=0.0, current_route=None),
    ]
    db.add_all([FleetAsset(**d) for d in fleet_data])
    db.commit()


def _seed_sensor_logs(db: Session, shipments: list):
    rng = random.Random(77)
    cold_chain = [s for s in shipments if s.is_cold_chain]
    now = datetime.utcnow()
    logs = []
    for s in cold_chain:
        min_t = s.required_min_temperature or 2.0
        max_t = s.required_max_temperature or 8.0
        mid = (min_t + max_t) / 2
        # Generate 8 readings per cold-chain shipment
        for reading_idx in range(8):
            ts = now - timedelta(hours=(7 - reading_idx) * 2)
            # Occasionally inject a minor excursion
            if reading_idx == 5 and rng.random() < 0.25:
                temp = round(max_t + rng.uniform(0.1, 1.5), 2)
                is_exc = True
            else:
                temp = round(mid + rng.uniform(-1.0, 1.0), 2)
                is_exc = temp > max_t or temp < min_t

            logs.append(SensorLog(
                shipment_id=s.shipment_id,
                sensor_id=f"SENS-{s.shipment_id}-{reading_idx:02d}",
                timestamp=ts,
                temperature=temp,
                humidity=round(rng.uniform(60.0, 80.0), 1),
                battery_pct=round(rng.uniform(70.0, 100.0), 1),
                latitude=s.current_lat,
                longitude=s.current_lon,
                is_excursion=is_exc,
            ))
    db.add_all(logs)
    db.commit()


def _seed_alerts(db: Session, shipments: list):
    rng = random.Random(55)
    now = datetime.utcnow()
    alerts = []
    cold_shipments = [s for s in shipments if s.is_cold_chain and s.risk_level in ("High", "Critical")]
    for i, s in enumerate(cold_shipments[:3]):
        alerts.append(Alert(
            alert_id=f"ALERT-CC-{i+1:03d}",
            category="Cold Chain",
            severity=s.risk_level,
            title=f"Temperature Alert: {s.shipment_id}",
            message=(
                f"Shipment {s.shipment_id} ({s.cargo_type}) temperature at "
                f"{s.current_temperature}°C. Allowed: "
                f"{s.required_min_temperature}–{s.required_max_temperature}°C."
            ),
            related_id=s.shipment_id,
            cargo_type=s.cargo_type,
            current_temperature=s.current_temperature,
            allowed_range=f"{s.required_min_temperature}°C to {s.required_max_temperature}°C",
            excursion_duration=f"{rng.randint(5, 45)} minutes",
            recommended_action="Initiate cooling intervention and notify quality team.",
            is_resolved=False,
            detected_at=now - timedelta(minutes=rng.randint(5, 120)),
        ))

    # Add a couple of disruption alerts
    at_risk = [s for s in shipments if s.risk_level == "Critical"][:2]
    for i, s in enumerate(at_risk):
        alerts.append(Alert(
            alert_id=f"ALERT-RISK-{i+1:03d}",
            category="Disruption",
            severity="Critical",
            title=f"Critical Risk: {s.shipment_id}",
            message=s.explanation or f"Shipment {s.shipment_id} is at critical risk due to active disruption.",
            related_id=s.shipment_id,
            is_resolved=False,
            detected_at=now - timedelta(minutes=rng.randint(10, 60)),
        ))

    db.add_all(alerts)
    db.commit()
