import os
import sys
import unittest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from spacecraft_core import (
    SpaceBrain,
    Mode,
    accel_eci_km_s2,
    orbital_state_from_elements,
    quat_normalize,
    sun_vector_eci,
    in_cylindrical_eclipse,
    earth_dipole_field_eci_t,
)


class SpaceBrainTests(unittest.TestCase):
    def test_gravity_points_inward(self):
        r, _ = orbital_state_from_elements(550, 97.6)
        a = accel_eci_km_s2(r)
        self.assertLess(float(np.dot(r, a)), 0.0)

    def test_quaternion_normalization(self):
        q = quat_normalize(np.array([1.0, 2.0, 3.0, 4.0]))
        self.assertAlmostEqual(float(np.linalg.norm(q)), 1.0, places=12)

    def test_orbit_altitude_remains_leo_over_ten_minutes(self):
        brain = SpaceBrain()
        alts = []
        for _ in range(600):
            telemetry = brain.step(1.0)
            alts.append(telemetry["altitude_km"])
        self.assertGreater(min(alts), 500.0)
        self.assertLess(max(alts), 600.0)

    def test_low_battery_drives_safe_mode(self):
        brain = SpaceBrain()
        brain.state.battery_wh = brain.cfg.battery_capacity_wh * 0.10
        telemetry = brain.step(1.0)
        self.assertEqual(telemetry["mode"], Mode.SAFE.value)
        self.assertIn("LOW_BATTERY", telemetry["safe_reason"])

    def test_comm_light_time_is_physical(self):
        brain = SpaceBrain()
        telemetry = brain.step(1.0)
        self.assertGreater(telemetry["slant_range_km"], 0.0)
        self.assertGreater(telemetry["one_way_light_time_ms"], 0.0)
        self.assertLess(telemetry["one_way_light_time_ms"], 100.0)

    def test_earth_dipole_field_is_plausible(self):
        r, _ = orbital_state_from_elements(550, 97.6)
        field = earth_dipole_field_eci_t(r)
        self.assertGreater(float(np.linalg.norm(field)), 1e-6)
        self.assertLess(float(np.linalg.norm(field)), 1e-4)

    def test_eclipse_function_returns_bool(self):
        brain = SpaceBrain()
        sun = sun_vector_eci(brain.now)
        self.assertIsInstance(in_cylindrical_eclipse(brain.state.r_eci_km, sun), bool)

    def test_fault_injection_star_tracker(self):
        brain = SpaceBrain()
        brain.inject_fault("star_tracker", True)
        telemetry = brain.step(1.0)
        self.assertFalse(telemetry["star_tracker_valid"])
        brain.inject_fault("star_tracker", False)
        telemetry = brain.step(1.0)
        self.assertTrue(telemetry["star_tracker_valid"])


if __name__ == "__main__":
    unittest.main()
