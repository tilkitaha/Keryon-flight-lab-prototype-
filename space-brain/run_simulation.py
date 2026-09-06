import argparse
import json
from spacecraft_core import SpaceBrain


def main():
    parser = argparse.ArgumentParser(description="Run KERYON Space Brain deterministic reference simulation")
    parser.add_argument("--duration", type=int, default=1800, help="simulation duration in seconds")
    parser.add_argument("--dt", type=float, default=1.0, help="integration step in seconds")
    args = parser.parse_args()

    brain = SpaceBrain()
    next_print = 0.0
    fault_on = False

    for _ in range(int(args.duration / args.dt)):
        t = brain.state.sim_time_s
        if t >= 900 and not fault_on:
            brain.inject_fault("star_tracker", True)
            fault_on = True
        if t >= 1050 and fault_on:
            brain.inject_fault("star_tracker", False)
            fault_on = False

        telemetry = brain.step(args.dt)
        if brain.state.sim_time_s >= next_print:
            print(json.dumps(telemetry, sort_keys=True))
            next_print += 60.0

    if brain.events:
        print("\nEVENTS")
        for event in brain.events:
            print("-", event)


if __name__ == "__main__":
    main()
