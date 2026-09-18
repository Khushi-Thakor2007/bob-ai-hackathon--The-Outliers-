# Technical Documentation: Supply Chain Disruption Assistant & Fleet Utilisation Optimizer

## 1. System Architecture Overview

The platform is designed as an event-driven **Supply Chain Control Tower** built upon a high-performance decoupled architecture:

```
+-------------------------------------------------------------------------+
|                           FRONTEND CONTROL TOWER                        |
|   (React 19 + TypeScript + Tailwind CSS + Leaflet GIS + Lucide Icons)   |
+--------------------+---------------------+--------------------+---------+
                     |                     |                    |
             REST API Calls        WebSocket / Polling   AI Assistant Chat
                     |                     |                    |
+--------------------v---------------------v--------------------v---------+
|                               FASTAPI GATEWAY                           |
|                       (Pydantic V2 Request Validation)                  |
+-------------------------------------------------------------------------+
|                            BACKEND DOMAIN SERVICES                      |
|                                                                         |
|  +---------------------+   +---------------------+   +---------------+  |
|  |  Disruption Engine  |   |     Risk Engine     |   | Route Opt Eng |  |
|  |  (Haversine/Corridor)   | (4-Factor Weighted) |   | (Multi-modal) |  |
|  +---------------------+   +---------------------+   +---------------+  |
|                                                                         |
|  +---------------------+   +---------------------+   +---------------+  |
|  | Fleet Util Optimizer|   |  Cold-Chain Engine  |   | Simulation Eng|  |
|  | (Capacity Match)    |   |  (IoT Time-Series)  |   | (Port Strike) |  |
|  +---------------------+   +---------------------+   +---------------+  |
+-------------------------------------------------------------------------+
|                             BOB AI ORCHESTRATOR                         |
|      - Strict Tool-Calling Architecture (Zero Hallucination)            |
|      - Backend Services as Deterministic Source of Truth                |
+-------------------------------------------------------------------------+
|                               DATA ACCESS LAYER                         |
|                    SQLAlchemy 2.0 ORM (PostgreSQL & SQLite)             |
+-------------------------------------------------------------------------+
```

---

## 2. Algorithmic Methodologies & Mathematical Models

### 2.1 Spatial Disruption Impact Detection (`disruption_engine.py`)
Impact detection calculates the geodesic distance from the disruption epicenter \((lat_d, lon_d)\) to the shipment's current coordinate \((lat_s, lon_s)\), origin, and destination using the spherical Haversine formula:

\[
a = \sin^2\left(\frac{\Delta lat}{2}\right) + \cos(lat_d)\cos(lat_s)\sin^2\left(\frac{\Delta lon}{2}\right)
\]
\[
d = 2 R \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right) \quad (\text{where } R = 6371\text{ km})
\]

A shipment is flagged as impacted if:
1. \(\min(d_{\text{current}}, d_{\text{origin}}, d_{\text{dest}}) \le \text{radius}_{km}\), OR
2. Transit corridor waypoints intersect named disruption nodes (e.g. `JNPT Port`, `NH-348`, `Western Corridor`).

Estimated schedule delay \(\Delta t_{\text{delay}}\) is dynamically assigned based on disruption severity:
- Critical: +36 hours (+12h if proximity < 50 km)
- High: +24 hours
- Medium: +12 hours
- Low: +6 hours

---

### 2.2 Composite 4-Factor Risk Scoring (`risk_engine.py`)
The risk score \(R \in [0, 100]\) is calculated deterministically via a weighted multi-attribute model:

\[
R = \min\left(100, W_{\text{sev}} \cdot S + W_{\text{delay}} \cdot D + W_{\text{cargo}} \cdot (P + V) + W_{\text{sens}} \cdot C\right)
\]

1. **Disruption Severity Factor (\(S \in [0, 30]\))**:
   - Critical = 30 pts, High = 22 pts, Medium = 14 pts, Low = 5 pts.
2. **Estimated Delay Factor (\(D \in [0, 25]\))**:
   - \(\ge 36\text{h}\) delay = 25 pts; \(\ge 24\text{h}\) = 18 pts; \(\ge 12\text{h}\) = 12 pts; \(>0\text{h}\) = 6 pts.
3. **Cargo Priority & Economic Value (\(P + V \in [0, 25]\))**:
   - Priority: Critical = 15 pts, High = 11 pts, Medium = 7 pts, Low = 3 pts.
   - Value: \(\ge \$1\text{M}\) = 10 pts; \(\ge \$500\text{k}\) = 7 pts; \(\ge \$100\text{k}\) = 4 pts.
4. **Cargo Sensitivity Factor (\(C \in [0, 20]\))**:
   - Cold-chain biologics/vaccines = +12 pts (+8 pts compound risk if delayed \(\ge 6\text{h}\)).
   - High-grade electronics / chemicals = +8 pts; General dry freight = 3 pts.

**Classification Levels**:
- **Critical**: \(R \ge 80\)
- **High**: \(60 \le R < 80\)
- **Medium**: \(35 \le R < 60\)
- **Low**: \(R < 35\)

---

### 2.3 Multi-Modal Route & Carrier Optimization (`route_optimizer.py`)
For affected shipments, alternative transit corridors are generated and ranked using an optimization utility score:

\[
\operatorname{Score}(opt) = (100 - R_{opt}) \times 0.40 + (100 - \text{Penalty}_{\text{delay}}) \times 0.35 + (100 - \text{Penalty}_{\text{cost}}) \times 0.25
\]

Four strategic alternatives are evaluated:
1. **Current Route**: Impacts persistent delay (+36h), 0% cost delta, High/Critical risk.
2. **Alternate Route A (Express Bypass)**: Fast highway bypass / air hybrid, +8h delay, +10% cost premium, Low risk.
3. **Alternate Route B (Multi-Modal Rail Bypass)**: Dedicated freight rail corridor, +12h delay, +5% cost delta, Low risk (balanced winner for dry cargo).
4. **Alternate Carrier (Specialized Reroute)**: Direct transfer to alternate carrier fleet (e.g. BlueDart or Mahindra Logistics) with pre-allocated slots.

---

### 2.4 Dynamic Fleet Redeployment Matching (`fleet_optimizer.py`)
Matches idle and underutilized assets (\(\text{utilization} < 35\%\)) to overloaded freight corridors:

\[
\operatorname{MatchScore}(asset, req) = S_{\text{type}} + S_{\text{capacity}} + S_{\text{proximity}} + S_{\text{status}}
\]

- Type compatibility: Exact match required (e.g., Reefer for cold-chain, Container for port diversion).
- Capacity constraint: \(Capacity_{asset} \ge 0.80 \times RequiredCapacity\).
- Proximity bonus: +40 pts if asset is located in the affected corridor's origin hub (e.g. Ahmedabad Freight Hub for the Ahmedabad → Mumbai corridor).

---

### 2.5 Cold-Chain IoT Excursion Classification (`cold_chain_engine.py`)
An excursion is detected when:
\[
T(t) < T_{\min} \quad \text{or} \quad T(t) > T_{\max}
\]

Metrics computed over the excursion interval \([t_{\text{start}}, t_{\text{end}}]\):
- **Duration**: \(\Delta t = t_{\text{end}} - t_{\text{start}}\) (minutes)
- **Peak Deviation**: \(\Delta T_{\max} = \max_{t} |T(t) - T_{\text{threshold}}|\)
- **Mean Excursion Temp**: \(\bar{T} = \frac{1}{N} \sum_{i=1}^{N} T_i\)

**Classification Rules**:
- **Critical**: \(\Delta T_{\max} \ge 3.0^\circ\text{C}\) or \(\Delta t \ge 60\text{ min}\), or any deviation \(\ge 2.0^\circ\text{C}\) on Vaccines.
- **Moderate**: \(1.5^\circ\text{C} \le \Delta T_{\max} < 3.0^\circ\text{C}\) or \(30\text{ min} \le \Delta t < 60\text{ min}\).
- **Minor**: \(\Delta T_{\max} < 1.5^\circ\text{C}\) and \(\Delta t < 30\text{ min}\).

*Compliant Handling Advisory*: The system issues guidance to inspect reefer compressor units and quarantine cargo for inspection according to handling protocol, adhering to strict medical device and pharmaceutical compliance standards.

---

## 3. Bob AI Assistant: Tool-Calling Architecture

Bob does **NOT** hallucinate calculations. When a user submits a query:
1. Intent analysis maps the natural language question to required backend tools.
2. Tools are executed against the database and domain engines:
   - `get_control_tower_summary()`
   - `get_active_disruptions()`
   - `get_affected_shipments()`
   - `get_shipment_risk(shipment_id)`
   - `get_route_alternatives(shipment_id)`
   - `get_idle_fleet()`
   - `get_redeployment_recommendations()`
   - `get_cold_chain_alerts()`
   - `get_temperature_history(shipment_id)`
3. Bob synthesizes structured response blocks:
   - **Direct Answer**: Concise, factual operational summary.
   - **Key Numbers**: Dynamic database values.
   - **Reasoning**: Root-cause analysis.
   - **Actionable Checklist**: Direct next steps.
   - **Tool Trace Inspector**: Allows operators to review raw tool invocations and returned payloads.
