# KERYON FLIGHT LAB

**3D UAV Flight, Autonomy & Resilience Simulation Prototype**

KERYON Flight Lab is a browser-based research simulator for testing unmanned aircraft behavior in non-weaponized flight, autonomy, navigation and resilience scenarios.

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

- Generic MALE-class UAV profile (TB2-scale reference class)
- Generic heavy UAV profile (Akıncı-scale reference class)
- Compact VTOL research profile

These profiles are broad public reference classes only. The simulator does not reproduce proprietary flight-control software, classified data or exact manufacturer performance models.

## Prototype capabilities

- Browser-based Three.js 3D world
- Simplified flight physics and autopilot response
- Wind / crosswind disturbance
- GPS degradation
- Data-link degradation
- Propulsion degradation
- Live telemetry: speed, altitude, heading, energy, link, propulsion and distance
- Waypoints and flight-path visualization
- Pause / reset / scenario switching
- Responsive desktop/mobile UI

## Safety scope

The simulator is intentionally focused on flight dynamics, navigation, autonomy, reliability, environmental resilience and research. Weapon employment, strike planning, targeting and offensive mission logic are not modeled.

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