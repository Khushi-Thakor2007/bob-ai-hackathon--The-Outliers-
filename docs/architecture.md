# Architecture Document: Supply Chain Control Tower

## System Overview
The platform is designed as an enterprise-grade **Supply Chain Disruption Assistant & Fleet Utilisation Optimizer**. It integrates spatial disruption detection, deterministic multi-factor risk scoring, route optimization, dynamic fleet redeployment, cold-chain IoT excursion classification, and a tool-calling AI assistant (Bob).

```
[Browser / Operator UI]
        │  (React 19, TypeScript, Tailwind CSS, Leaflet, SVG Visualizations)
        ▼
[FastAPI Gateway: Port 8000]
        │
        ├── /api/dashboard/summary
        ├── /api/shipments (CRUD, multi-filter, route authorization)
        ├── /api/disruptions (Spatial analysis, toggle, impact)
        ├── /api/fleet (Utilization, redeployment matchmaker)
        ├── /api/cold-chain (IoT telemetry, excursion detection)
        ├── /api/bob/query (Strict tool-calling orchestrator)
        └── /api/simulation (Port Strike, Temp Excursion, Reset)
        │
        ▼
[Domain Engines & Services]
  ├── DisruptionEngine (Haversine geodesic & corridor match)
  ├── RiskEngine (4-factor weighted scoring model)
  ├── RouteOptimizer (Multimodal bypass & carrier optimization)
  ├── FleetOptimizer (Capacity & proximity matching)
  ├── ColdChainEngine (IoT stream classification & duration detection)
  └── SimulationEngine (Scenario state orchestrator)
        │
        ▼
[Data Layer]
  └── SQLAlchemy 2.0 ORM -> SQLite / PostgreSQL
```

## Security & Reliability Principles
1. **Source of Truth**: The database and backend calculation engines are the sole authority for business figures. The LLM cannot invent numbers.
2. **Deterministic Fallbacks**: If external API keys are not supplied, Bob Assistant uses a built-in operational orchestrator that executes the exact same tools and returns structured analytical results.
3. **Graceful Degradation**: Dual database configuration uses local SQLite when `DATABASE_URL` is unset, and seamlessly connects to PostgreSQL in production environments.
