from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Disruption(Base):
    __tablename__ = "disruptions"

    id = Column(Integer, primary_key=True, index=True)
    disruption_id = Column(String, unique=True, index=True)
    type = Column(String)           # Port Strike, Weather, Customs Delay, etc.
    name = Column(String)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    severity = Column(String)       # Low, Medium, High, Critical
    start_time = Column(DateTime, default=datetime.utcnow)
    expected_duration = Column(String)
    affected_area = Column(String)
    radius_km = Column(Float, default=200.0)
    description = Column(Text)
    is_active = Column(Boolean, default=True)


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, unique=True, index=True)
    origin = Column(String)
    destination = Column(String)
    current_location = Column(String)
    carrier = Column(String)
    mode = Column(String)           # Road, Air, Sea, Multimodal
    cargo_type = Column(String)
    cargo_value = Column(Float)
    weight_kg = Column(Float)
    status = Column(String)         # In-Transit, At-Risk, Delayed, Delivered
    priority = Column(String)       # Critical, High, Normal, Low
    eta = Column(String)
    delay_hours = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")       # Low, Medium, High, Critical
    current_risk_score = Column(Float, default=0.0)  # 0-100
    disruption_exposure = Column(String, default="None")
    recommended_action = Column(String)
    explanation = Column(Text)

    # Cold chain
    is_cold_chain = Column(Boolean, default=False)
    required_min_temperature = Column(Float, nullable=True)
    required_max_temperature = Column(Float, nullable=True)
    current_temperature = Column(Float, nullable=True)

    # Geo
    origin_lat = Column(Float, nullable=True)
    origin_lon = Column(Float, nullable=True)
    dest_lat = Column(Float, nullable=True)
    dest_lon = Column(Float, nullable=True)
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)

    # Relationships (eager-loadable, not FK constrained in demo)
    route_alternatives = []
    sensor_history = []


class RouteAlternative(Base):
    __tablename__ = "route_alternatives"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, index=True)
    route_name = Column(String)
    carrier_name = Column(String)
    mode = Column(String)
    distance_km = Column(Float)
    estimated_eta = Column(String)
    delay_hours = Column(Float)
    cost_delta_pct = Column(Float)   # % cost change vs original
    risk_level = Column(String)
    recommendation_score = Column(Float)  # 0-100
    is_recommended = Column(Boolean, default=False)
    explanation = Column(Text)


class FleetAsset(Base):
    __tablename__ = "fleet_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String, unique=True, index=True)
    type = Column(String)            # Truck, Container, Reefer Truck, Vessel
    license_plate = Column(String, nullable=True)
    location = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String)          # Idle, In-Use, Maintenance
    availability = Column(String)    # Available, Dispatched, Unavailable
    capacity = Column(Float)
    capacity_unit = Column(String, default="tonnes")
    utilization = Column(Float, default=0.0)   # 0-100 %
    current_route = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


class RedeploymentRecommendation(Base):
    __tablename__ = "redeployment_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String, index=True)
    asset_type = Column(String)
    location = Column(String)
    capacity = Column(String)
    affected_corridor = Column(String)
    required_capacity = Column(String)
    utilization_pct = Column(Float)
    recommendation = Column(String)
    reason = Column(Text)
    status = Column(String, default="Pending")    # Pending, Redeployed, Cancelled


class SensorLog(Base):
    __tablename__ = "sensor_logs"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, index=True)
    sensor_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)
    humidity = Column(Float, nullable=True)
    battery_pct = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_excursion = Column(Boolean, default=False)


class ColdChainRule(Base):
    __tablename__ = "cold_chain_rules"

    id = Column(Integer, primary_key=True, index=True)
    cargo_type = Column(String, unique=True)
    min_temperature = Column(Float)
    max_temperature = Column(Float)
    max_excursion_minutes = Column(Integer, default=30)
    description = Column(Text)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)
    category = Column(String)        # Cold Chain, Disruption, Fleet, Risk
    severity = Column(String)        # Low, Medium, High, Critical
    title = Column(String)
    message = Column(Text)
    related_id = Column(String)      # shipment_id or asset_id
    cargo_type = Column(String, nullable=True)
    current_temperature = Column(Float, nullable=True)
    allowed_range = Column(String, nullable=True)
    excursion_duration = Column(String, nullable=True)
    recommended_action = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
