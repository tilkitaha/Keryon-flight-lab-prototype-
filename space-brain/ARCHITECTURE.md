# KERYON Space Brain — Flight Architecture Notes

## Design rule

**AI is advisory; survival control is deterministic.**

ORACLE may propose a mission plan, but the vehicle kernel owns actuator bounds, power limits, attitude constraints, safing and watchdog behavior. An ORACLE plan that violates a hard vehicle invariant is rejected.

## Hard invariants

- Battery critical threshold always overrides payload operation.
- Actuator commands are clamped to configured physical limits.
- Reaction wheels cannot be commanded deeper into saturation.
- Large attitude error is only a fault in closed-loop mission pointing; it is expected during acquisition/detumble.
- Safe mode is power-preserving and payload-off.
- Loss of ground contact does not stop onboard survival functions.
- Recovery from Safe requires sustained healthy margins, not a single good sample.

## State-machine intent

`BOOT`
: Initialize state, clocks, health monitors, command/telemetry and sensor interfaces.

`DETUMBLE`
: Use magnetorquer B-dot damping. Reaction wheels are not used as the primary deployment-rate sink.

`SUN_ACQUIRE`
: Acquire a power-positive Sun attitude using bounded reaction-wheel control.

`NOMINAL`
: Maintain mission pointing while respecting power and actuator margins.

`DOWNLINK`
: Entered automatically when the configured ground station is above the elevation mask.

`SAFE`
: Payload off, Sun-safe target, conservative load profile, health logging and predictable recovery behavior.

## FDIR separation

The flight implementation should keep FDIR sufficiently independent from the subsystem it monitors. In particular, a future attitude-fault monitor should not depend exclusively on the same estimator/sensor chain used to close the attitude-control loop.

## Validation ladder

1. Unit tests for math and state transitions.
2. Deterministic scenario regression.
3. Monte Carlo parameter/fault sweeps.
4. Cross-validation with GMAT/SPICE truth products.
5. Software-in-the-loop with the target flight framework.
6. Processor-in-the-loop on target-class CPU.
7. Hardware-in-the-loop with sensor/actuator simulators.
8. Long-duration fault campaigns, watchdog/reset testing and telemetry-loss recovery.
9. Requirements traceability and coverage appropriate to the mission assurance class.

## Framework mapping

NASA F´ and cFS are natural targets because both encourage modular components, command/telemetry interfaces, portability and testability. The present Python kernel is a reference model used to make the physics and invariants explicit before flight-framework porting.
