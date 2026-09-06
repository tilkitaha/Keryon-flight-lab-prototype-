# KERYON FLIGHT LAB

**3D UAV Flight, Autonomy & Resilience Simulation Prototype**

KERYON Flight Lab is a browser-based research simulator for testing unmanned aircraft behavior in different non-weaponized scenarios.

## Prototype capabilities

- Procedural 3D test world
- Generic MALE-class UAV profile (TB2-scale reference class)
- Generic heavy UAV profile (Akıncı-scale reference class)
- Compact VTOL research profile
- Simplified flight physics and autopilot response
- Wind / crosswind disturbance
- GPS degradation
- Data-link degradation
- Propulsion degradation
- Mountain survey scenario
- Live telemetry: speed, altitude, heading, energy, link, propulsion and distance
- Waypoints and flight-path visualization
- Pause / reset / scenario switching
- Mobile-friendly browser UI

> Aircraft names/classes are used only as broad public reference categories. This prototype does not reproduce proprietary flight-control logic or exact performance data.

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
- Procedural geometry (no external 3D assets required)

## Brand

**KERYON DYNAMICS**  
*Intelligence in Motion*
