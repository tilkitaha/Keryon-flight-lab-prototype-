# KERYON SPACE BRAIN v2 — Mission Control

The browser demo lives in `../space-brain-mission-control.html` and visualizes the deterministic Space Brain reference architecture together with the ORACLE supervisory Shadow Twin.

## Added in v2

- 3D Earth, star field and spacecraft visualization
- Sun direction and eclipse state
- Solar-array visualization and power telemetry
- Reaction-wheel assembly visualization
- Live ECI orbit propagation with J2 perturbation in the browser demo
- Live latitude / longitude ground track
- Selectable Poznań and Ankara ground stations
- Ground-station elevation, slant range and one-way light time
- Earth-fixed ground-station markers and visual link line
- Deterministic state machine: `BOOT → DETUMBLE → SUN_ACQUIRE → NOMINAL / DOWNLINK → SAFE`
- Fault injection for star tracker, gyro, communications, power load and wheel degradation
- ORACLE Shadow Twin divergence estimate with `NOMINAL / CAUTION / HOLD`
- FDIR and Safe Mode remain authoritative over the assurance layer

## Live demo

Production alias:

`https://keryon-space-brain-v2-8q6z7hkpr5-8939.vercel.app`

## Important boundary

This is a software-in-the-loop engineering demo, not flight-certified software or operational spacecraft guidance. The Python kernel in `space-brain/spacecraft_core.py` remains the more detailed engineering reference. The next fidelity steps are GMAT/SPICE validation, sensor-estimator work, higher-fidelity force models and eventual componentization in a flight-software framework such as F´ or cFS.
