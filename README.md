# KERYON FLIGHT LAB

**3D UAV Flight, Autonomy, Digital-Twin & Disaster-Resilience Simulation Prototype**

KERYON Flight Lab is a browser-based research simulator for testing unmanned aircraft behavior in non-weaponized flight, autonomy, navigation, environmental resilience and disaster-response scenarios.

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

Open `http://localhost:8080`.

## Stack

- HTML / CSS / JavaScript
- Three.js
- Public Manhattan GeoJSON
- NYC Open Data Building Footprints (when reachable)
- Procedural geometry fallback

## Brand

**KERYON DYNAMICS**  
*Intelligence in Motion*
