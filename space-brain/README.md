# KERYON ORACLE SPACE BRAIN

**Deterministic spacecraft autonomy reference kernel**

This module is the first step from KERYON's browser demos toward a real spacecraft-flight-software architecture. The design deliberately separates two layers:

- **Vehicle survival / control kernel:** deterministic physics, bounded actuators, state machines and fault rules.
- **ORACLE assurance layer:** counterfactual planning, shadow-twin divergence monitoring and replanning above the deterministic kernel.

The current implementation is a software-in-the-loop engineering reference, **not flight-certified software**.

## What is physically modeled now

`spacecraft_core.py` implements:

- Earth-centered inertial (ECI) orbital state
- Two-body Earth gravity plus **J2** oblateness perturbation
- Fourth-order Runge-Kutta orbit integration
- WGS-84 ground-station geometry
- Greenwich sidereal-time Earth rotation
- Ground-station elevation, slant range and one-way light time
- Low-precision solar ephemeris for autonomy simulation
- Cylindrical Earth eclipse detection
- Quaternion rigid-body attitude propagation
- Nadir-pointing and Sun-safe target attitudes
- 3-axis reaction-wheel PD attitude control with torque and momentum limits
- Centered-dipole Earth magnetic-field model
- Magnetorquer **B-dot detumble** logic
- Solar-array incidence and battery energy integration
- Mode-dependent spacecraft loads
- Deterministic mission modes: `BOOT → DETUMBLE → SUN_ACQUIRE → NOMINAL / DOWNLINK`
- Fault Detection, Isolation and Recovery (FDIR) transition to `SAFE`
- Autonomous Safe-mode recovery conditions
- Fault injection for star tracker, gyro, communications, power load and wheel degradation

## Safe-mode philosophy

The survival kernel follows a simple rule: mission objectives never outrank spacecraft survival.

`SAFE` disables the payload and commands a Sun-safe attitude. It is entered for conditions such as critically low battery, reaction-wheel saturation, sustained closed-loop pointing failure, or loss of attitude sensing combined with excessive body rate. Recovery is only allowed after health margins remain inside bounds for a sustained period.

The intended flight implementation should keep Safe-mode logic independent from higher-level AI/ORACLE planning.

## Run

```bash
python -m pip install -r requirements.txt
python run_simulation.py --duration 1800 --dt 1
```

The example run prints a telemetry JSON snapshot every 60 simulated seconds and injects/recoveries a star-tracker fault to exercise the health path.

## Tests

```bash
python -m unittest discover -s tests -v
```

The current suite validates gravity direction, quaternion normalization, LEO propagation bounds, low-battery safing, communications light time, eclipse typing, magnetic-field magnitude and sensor-fault injection.

## Flight-software architecture target

The next implementation stage is to port this reference logic into a component framework such as NASA **F´ (F Prime)** or **core Flight System (cFS)** rather than running Python onboard.

Suggested components:

| Component | Nominal rate | Responsibility |
|---|---:|---|
| TimeSvc | 10 Hz | Mission elapsed time / UTC correlation |
| SensorMgr | 100 Hz | Gyro, star tracker, Sun sensor, magnetometer ingest |
| AttitudeEstimator | 50 Hz | Quaternion state estimate and covariance |
| AdcsControl | 20 Hz | Mode-specific pointing / detumble control |
| OrbitNav | 1 Hz | ECI state, ephemeris and ground geometry |
| PowerMgr | 1 Hz | Array generation, loads, battery SoC |
| CommMgr | 1 Hz | Contact windows, link state and telemetry policy |
| FdirMgr | 10 Hz + events | Fault monitors, isolation, Safe-mode entry/recovery |
| MissionExec | 1–10 Hz | Sequencing under verified constraints |
| OracleAssurance | event-driven | Shadow twin, uncertainty analysis, replanning requests |

## Fidelity boundary

The code uses real equations but remains an engineering model. A flight program still requires validation against higher-fidelity tools and real hardware.

Planned upgrades:

1. Validate orbital propagation against NASA GMAT.
2. Replace low-precision Sun/geometry data with NAIF SPICE kernels where appropriate.
3. Add atmospheric drag, solar-radiation pressure and configurable force models.
4. Replace the simple attitude truth path with a MEKF estimator using gyro/star-tracker/Sun-sensor measurements.
5. Add IGRF-class geomagnetic field and reaction-wheel momentum unloading.
6. Port components to F´/cFS with real-time scheduling and watchdogs.
7. Add software-in-the-loop, processor-in-the-loop and hardware-in-the-loop test stages.
8. Add telemetry dictionaries, command authorization, parameter tables and persistent event logs.
9. Add Monte Carlo fault campaigns and requirements-based coverage reports.
10. Interface ORACLE v2 only through bounded commands and assurance gates.

## Scope

This project is for non-weaponized spacecraft autonomy: Earth observation, science, communications, inspection, search-and-rescue support and technology demonstration. It does not implement weapon targeting, offensive mission planning or re-entry targeting.
