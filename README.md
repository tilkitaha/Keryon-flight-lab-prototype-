# KERYON FLIGHT LAB

**3D UAV Flight, Autonomy, Digital-Twin & Disaster-Resilience Simulation Prototype**

KERYON Flight Lab is a browser-based research simulator for testing unmanned aircraft behavior in non-weaponized flight, autonomy, navigation, environmental resilience and disaster-response scenarios.

## KERYON ORACLE — Shadow Twin Autonomy Engine

The newest flagship R&D concept is **KERYON ORACLE**, a counterfactual autonomy-assurance layer.

Open `oracle.html` to run the prototype.

Instead of choosing a route only from a nominal prediction, ORACLE generates many uncertain futures for several candidate mission plans and compares them before execution. The prototype currently evaluates 1,536 synthetic counterfactual outcomes per decision (512 for each of three candidate plans).

It varies factors such as:

- Weather uncertainty
- GNSS outage probability
- Battery health
- Fleet size and redundancy

For each candidate plan, ORACLE estimates:

- Robust mission-success probability
- 5th-percentile energy reserve
- 5th-percentile link resilience
- Downside-loss score

It then selects the plan with the strongest combined robustness margin and explains why a faster or more energy-efficient alternative was rejected.

The prototype also includes **live Shadow Mode**. A simulated real mission is compared against the accepted digital-twin envelope. If reality divergence crosses the assurance threshold, ORACLE recommends re-planning rather than silently continuing with a stale plan.

This is a synthetic operational-concept prototype, not flight guidance. The long-term product direction is trusted autonomy: **simulate → compare → explain → shadow → adapt**.

## KERYON Rescue Grid — real problem focus

The project includes **KERYON Rescue Grid**, an operational-concept prototype focused on urban flash-flood response.

Open `rescue-grid.html` to test the workflow.

The problem it addresses is not simply drone flight. During fast-moving urban flooding, responders need a continuously updated answer to four questions:

1. Which road segments are becoming impassable?
2. Which blocks or critical facilities are at highest access risk?
3. Where should the UAV fleet scan next to reduce uncertainty?
4. What ground route remains usable for responders?

The current prototype uses synthetic incident data and demonstrates:

- Multi-UAV sector scanning
- Synthetic flood-depth estimation
- Passable / flooded / blocked road classification
- Continuously increasing observation confidence
- Priority scoring for incident zones
- Isolated-block estimation
- Automatic responder-route rerouting around blocked segments
- Explainable NOEMA decision stream
- Decision-latency and coverage KPIs

The intended future system would ingest authorized municipal GIS, weather, drainage, traffic and UAV sensor data. The current page is an operational concept, **not emergency guidance**.

## New York test environment

The current prototype opens in a **Manhattan digital test range**.

- Real Manhattan neighborhood geometry loaded from a published public GeoJSON source
- Attempts to load NYC Open Data Building Footprints for 3D urban detail
- Automatic procedural skyline fallback when building data cannot be reached
- Stylized Hudson / East River environment and Central Park reference area
- Synthetic research corridor and waypoints for visualization only
- Urban wind, GPS degradation, data-link shadow and propulsion-degradation scenarios

The displayed corridor is a simulation path and is **not real-world aviation guidance**.

## Aircraft research profiles

- Generic MALE-class UAV profile
- Generic heavy-endurance UAV profile
- Compact VTOL research profile

These profiles are broad public reference classes only. The simulator does not reproduce proprietary flight-control software, classified data or exact manufacturer performance models.

## Disaster & Resilience Mode

The v0.5 prototype adds a dedicated non-weaponized disaster-response layer:

- Humanitarian relief-drop visualization using inert emergency-supply packages
- Urban fire and smoke visibility events
- Lightning / severe-weather shock simulation
- Communications blackout and bounded autonomous hold behavior
- Synthetic debris-zone obstacle avoidance visualization
- Evacuation-corridor monitoring and communications-relay scenario
- Explainable NOEMA autonomy responses for each injected event
- Resilience score, event count and aid-drop counters
- Cinematic event replay

## Core prototype capabilities

- Browser-based Three.js 3D world
- Coordinated 1–6 UAV fleet
- Simplified flight physics and autopilot response
- Sensor-fusion overlays and LiDAR visualization
- Fleet trails and coverage heat field
- Cinematic camera director
- Day / night operations and atmospheric effects
- Wind / crosswind disturbance
- GPS degradation
- Data-link degradation
- Propulsion degradation
- Live telemetry and health indicators
- Explainable autonomy event stream
- Local AI-style command parser
- Pause / reset / scenario switching
- Responsive desktop/mobile UI

## Safety scope

The simulator is intentionally focused on flight dynamics, navigation, autonomy, mapping, reliability, environmental resilience, humanitarian logistics and disaster response. Weapon employment, strike planning, targeting, explosive delivery and offensive mission logic are not modeled.

## Run locally

```bash
python -m http.server 8080
```

Open:

- `http://localhost:8080` — Flight Lab
- `http://localhost:8080/rescue-grid.html` — Rescue Grid
- `http://localhost:8080/oracle.html` — ORACLE Shadow Twin

## Stack

- HTML / CSS / JavaScript
- Three.js
- Public Manhattan GeoJSON
- NYC Open Data Building Footprints (when reachable)
- Procedural geometry fallback

## Brand

**KERYON DYNAMICS**  
*Intelligence in Motion*
