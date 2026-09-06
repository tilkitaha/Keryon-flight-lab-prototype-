from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import math
from typing import Dict, List, Tuple

import numpy as np

MU_EARTH_KM3_S2 = 398600.4418
R_EARTH_KM = 6378.137
J2 = 1.08262668e-3
C_KM_S = 299792.458


def norm(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))


def unit(v: np.ndarray) -> np.ndarray:
    n = norm(v)
    if n < 1e-12:
        raise ValueError("zero-length vector")
    return v / n


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def julian_date(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    y, m = dt.year, dt.month
    d = dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond / 1e6) / 60.0) / 60.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5


def gmst_rad(dt: datetime) -> float:
    jd = julian_date(dt)
    t = (jd - 2451545.0) / 36525.0
    theta_deg = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - t * t * t / 38710000.0
    )
    return math.radians(theta_deg % 360.0)


def sun_vector_eci(dt: datetime) -> np.ndarray:
    """Low-precision Sun direction for autonomy simulation.

    Flight validation should replace this approximation with SPICE ephemerides.
    """
    n = julian_date(dt) - 2451545.0
    L = math.radians((280.460 + 0.9856474 * n) % 360.0)
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2.0 * g)
    eps = math.radians(23.439 - 0.0000004 * n)
    return unit(
        np.array(
            [
                math.cos(lam),
                math.cos(eps) * math.sin(lam),
                math.sin(eps) * math.sin(lam),
            ],
            dtype=float,
        )
    )


def in_cylindrical_eclipse(r_eci_km: np.ndarray, sun_hat_eci: np.ndarray) -> bool:
    along = float(np.dot(r_eci_km, sun_hat_eci))
    if along >= 0.0:
        return False
    perpendicular = r_eci_km - along * sun_hat_eci
    return norm(perpendicular) < R_EARTH_KM


def earth_dipole_field_eci_t(r_eci_km: np.ndarray) -> np.ndarray:
    """Centered Earth magnetic dipole model in tesla.

    This preserves the real magnetic torque geometry for B-dot detumble. A flight
    implementation should replace it with an IGRF-class model.
    """
    r = norm(r_eci_km)
    rhat = r_eci_km / r
    mhat = np.array([0.0, 0.0, 1.0])
    b_eq = 3.12e-5
    return b_eq * (R_EARTH_KM / r) ** 3 * (3.0 * np.dot(mhat, rhat) * rhat - mhat)


def accel_eci_km_s2(r_eci_km: np.ndarray) -> np.ndarray:
    """Two-body gravity plus J2 perturbation."""
    x, y, z = r_eci_km
    r = norm(r_eci_km)
    if r <= R_EARTH_KM:
        raise ValueError("spacecraft radius is at/below Earth surface")
    r2 = r * r
    z2_r2 = (z * z) / r2
    factor = -MU_EARTH_KM3_S2 / (r ** 3)
    k = 1.5 * J2 * (R_EARTH_KM / r) ** 2
    ax = factor * x * (1.0 - k * (5.0 * z2_r2 - 1.0))
    ay = factor * y * (1.0 - k * (5.0 * z2_r2 - 1.0))
    az = factor * z * (1.0 - k * (5.0 * z2_r2 - 3.0))
    return np.array([ax, ay, az], dtype=float)


def rk4_orbit_step(r: np.ndarray, v: np.ndarray, dt_s: float) -> Tuple[np.ndarray, np.ndarray]:
    def f(y: np.ndarray) -> np.ndarray:
        rr = y[:3]
        vv = y[3:]
        return np.hstack((vv, accel_eci_km_s2(rr)))

    y = np.hstack((r, v))
    k1 = f(y)
    k2 = f(y + 0.5 * dt_s * k1)
    k3 = f(y + 0.5 * dt_s * k2)
    k4 = f(y + dt_s * k3)
    out = y + (dt_s / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    return out[:3], out[3:]


def quat_normalize(q: np.ndarray) -> np.ndarray:
    return q / np.linalg.norm(q)


def quat_conj(q: np.ndarray) -> np.ndarray:
    return np.array([q[0], -q[1], -q[2], -q[3]], dtype=float)


def quat_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array(
        [
            aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
        ],
        dtype=float,
    )


def quat_to_dcm(q: np.ndarray) -> np.ndarray:
    q = quat_normalize(q)
    w, x, y, z = q
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=float,
    )


def dcm_to_quat(C: np.ndarray) -> np.ndarray:
    tr = float(np.trace(C))
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2.0
        q = np.array([0.25 * s, (C[2, 1] - C[1, 2]) / s, (C[0, 2] - C[2, 0]) / s, (C[1, 0] - C[0, 1]) / s])
    else:
        i = int(np.argmax(np.diag(C)))
        if i == 0:
            s = math.sqrt(1.0 + C[0, 0] - C[1, 1] - C[2, 2]) * 2.0
            q = np.array([(C[2, 1] - C[1, 2]) / s, 0.25 * s, (C[0, 1] + C[1, 0]) / s, (C[0, 2] + C[2, 0]) / s])
        elif i == 1:
            s = math.sqrt(1.0 + C[1, 1] - C[0, 0] - C[2, 2]) * 2.0
            q = np.array([(C[0, 2] - C[2, 0]) / s, (C[0, 1] + C[1, 0]) / s, 0.25 * s, (C[1, 2] + C[2, 1]) / s])
        else:
            s = math.sqrt(1.0 + C[2, 2] - C[0, 0] - C[1, 1]) * 2.0
            q = np.array([(C[1, 0] - C[0, 1]) / s, (C[0, 2] + C[2, 0]) / s, (C[1, 2] + C[2, 1]) / s, 0.25 * s])
    return quat_normalize(q)


def quat_error_angle_deg(q_target: np.ndarray, q_current: np.ndarray) -> float:
    qe = quat_mul(quat_conj(q_current), q_target)
    qe = quat_normalize(qe)
    w = clamp(abs(float(qe[0])), -1.0, 1.0)
    return math.degrees(2.0 * math.acos(w))


def integrate_quaternion(q: np.ndarray, omega_body_rad_s: np.ndarray, dt_s: float) -> np.ndarray:
    omega_q = np.array([0.0, *omega_body_rad_s], dtype=float)
    qdot = 0.5 * quat_mul(q, omega_q)
    return quat_normalize(q + qdot * dt_s)


def orbital_state_from_elements(
    altitude_km: float,
    inclination_deg: float,
    raan_deg: float = 0.0,
    true_anomaly_deg: float = 0.0,
) -> Tuple[np.ndarray, np.ndarray]:
    a = R_EARTH_KM + altitude_km
    inc = math.radians(inclination_deg)
    raan = math.radians(raan_deg)
    nu = math.radians(true_anomaly_deg)
    r_pf = np.array([a * math.cos(nu), a * math.sin(nu), 0.0])
    vmag = math.sqrt(MU_EARTH_KM3_S2 / a)
    v_pf = np.array([-vmag * math.sin(nu), vmag * math.cos(nu), 0.0])
    cO, sO, ci, si = math.cos(raan), math.sin(raan), math.cos(inc), math.sin(inc)
    R = np.array([[cO, -sO * ci, sO * si], [sO, cO * ci, -cO * si], [0, si, ci]], dtype=float)
    return R @ r_pf, R @ v_pf


def ecef_from_geodetic(lat_deg: float, lon_deg: float, alt_km: float) -> np.ndarray:
    a = 6378.137
    f = 1.0 / 298.257223563
    e2 = f * (2.0 - f)
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    s = math.sin(lat)
    N = a / math.sqrt(1.0 - e2 * s * s)
    return np.array(
        [
            (N + alt_km) * math.cos(lat) * math.cos(lon),
            (N + alt_km) * math.cos(lat) * math.sin(lon),
            (N * (1.0 - e2) + alt_km) * math.sin(lat),
        ]
    )


def eci_to_ecef(r_eci: np.ndarray, dt: datetime) -> np.ndarray:
    th = gmst_rad(dt)
    c, s = math.cos(th), math.sin(th)
    R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]], dtype=float)
    return R @ r_eci


def ground_station_elevation_deg(
    r_eci: np.ndarray,
    dt: datetime,
    lat_deg: float,
    lon_deg: float,
    alt_km: float,
) -> Tuple[float, float]:
    r_sc = eci_to_ecef(r_eci, dt)
    r_gs = ecef_from_geodetic(lat_deg, lon_deg, alt_km)
    rho = r_sc - r_gs
    rng = norm(rho)
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    east = np.array([-math.sin(lon), math.cos(lon), 0.0])
    north = np.array([-math.sin(lat) * math.cos(lon), -math.sin(lat) * math.sin(lon), math.cos(lat)])
    up = np.array([math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)])
    e, n, u = float(np.dot(rho, east)), float(np.dot(rho, north)), float(np.dot(rho, up))
    elev = math.degrees(math.atan2(u, math.hypot(e, n)))
    return elev, rng


class Mode(str, Enum):
    BOOT = "BOOT"
    DETUMBLE = "DETUMBLE"
    SUN_ACQUIRE = "SUN_ACQUIRE"
    NOMINAL = "NOMINAL"
    DOWNLINK = "DOWNLINK"
    SAFE = "SAFE"


@dataclass
class SpacecraftConfig:
    mass_kg: float = 28.0
    inertia_kg_m2: np.ndarray = field(default_factory=lambda: np.diag([0.48, 0.52, 0.34]))
    wheel_torque_max_nm: float = 0.008
    wheel_momentum_max_nms: float = 0.150
    magnetorquer_max_dipole_am2: float = 0.25
    bdot_gain_am2_s_t: float = 85000.0
    battery_capacity_wh: float = 220.0
    solar_array_w: float = 95.0
    load_nominal_w: float = 42.0
    load_downlink_w: float = 58.0
    load_safe_w: float = 22.0
    kp: float = 0.018
    kd: float = 0.055
    ground_lat_deg: float = 52.4064
    ground_lon_deg: float = 16.9252
    ground_alt_km: float = 0.09
    min_elevation_deg: float = 10.0


@dataclass
class SpacecraftState:
    epoch: datetime
    r_eci_km: np.ndarray
    v_eci_km_s: np.ndarray
    q_body_to_eci: np.ndarray
    omega_body_rad_s: np.ndarray
    wheel_momentum_nms: np.ndarray
    battery_wh: float
    mode: Mode = Mode.BOOT
    sim_time_s: float = 0.0
    eclipse: bool = False
    comm_visible: bool = False
    comm_elevation_deg: float = -90.0
    slant_range_km: float = 0.0
    star_tracker_valid: bool = True
    gyro_valid: bool = True
    payload_enabled: bool = False
    safe_reason: str = ""


class SpaceBrain:
    """Deterministic spacecraft autonomy reference kernel.

    ORACLE may plan above this layer, but vehicle survival uses explicit physics,
    actuator limits and state rules rather than an opaque ML controller.
    """

    def __init__(self, config: SpacecraftConfig | None = None, epoch: datetime | None = None):
        self.cfg = config or SpacecraftConfig()
        epoch = epoch or datetime(2026, 9, 6, 20, 0, tzinfo=timezone.utc)
        r, v = orbital_state_from_elements(550.0, 97.6, raan_deg=30.0, true_anomaly_deg=10.0)
        self.state = SpacecraftState(
            epoch=epoch,
            r_eci_km=r,
            v_eci_km_s=v,
            q_body_to_eci=np.array([1.0, 0.0, 0.0, 0.0]),
            omega_body_rad_s=np.array([0.003, -0.002, 0.0015]),
            wheel_momentum_nms=np.zeros(3),
            battery_wh=self.cfg.battery_capacity_wh * 0.82,
        )
        self.events: List[str] = []
        self._attitude_bad_s = 0.0
        self._safe_recovery_s = 0.0
        self._forced_comm_loss = False
        self._power_fault_w = 0.0
        self._wheel_scale = 1.0
        self._last_b_body_t: np.ndarray | None = None

    @property
    def now(self) -> datetime:
        return self.state.epoch + timedelta(seconds=self.state.sim_time_s)

    def inject_fault(self, fault: str, active: bool = True) -> None:
        fault = fault.lower()
        if fault == "star_tracker":
            self.state.star_tracker_valid = not active
        elif fault == "gyro":
            self.state.gyro_valid = not active
        elif fault == "comm":
            self._forced_comm_loss = active
        elif fault == "power_load":
            self._power_fault_w = 38.0 if active else 0.0
        elif fault == "wheel_degrade":
            self._wheel_scale = 0.45 if active else 1.0
        else:
            raise ValueError(f"unknown fault: {fault}")
        self.events.append(f"FAULT {'ON' if active else 'OFF'}: {fault}")

    def _nadir_target_quat(self) -> np.ndarray:
        z_b_eci = -unit(self.state.r_eci_km)
        x_guess = unit(self.state.v_eci_km_s)
        x_b_eci = unit(x_guess - np.dot(x_guess, z_b_eci) * z_b_eci)
        y_b_eci = unit(np.cross(z_b_eci, x_b_eci))
        x_b_eci = unit(np.cross(y_b_eci, z_b_eci))
        return dcm_to_quat(np.column_stack((x_b_eci, y_b_eci, z_b_eci)))

    def _sun_safe_target_quat(self, sun_hat: np.ndarray) -> np.ndarray:
        x_b_eci = unit(sun_hat)
        nadir = -unit(self.state.r_eci_km)
        z_guess = nadir - np.dot(nadir, x_b_eci) * x_b_eci
        if norm(z_guess) < 1e-6:
            fallback = np.array([0.0, 0.0, 1.0])
            z_guess = fallback - np.dot(fallback, x_b_eci) * x_b_eci
        z_b_eci = unit(z_guess)
        y_b_eci = unit(np.cross(z_b_eci, x_b_eci))
        z_b_eci = unit(np.cross(x_b_eci, y_b_eci))
        return dcm_to_quat(np.column_stack((x_b_eci, y_b_eci, z_b_eci)))

    def _attitude_step(self, q_target: np.ndarray, dt_s: float) -> float:
        s = self.state
        qe = quat_normalize(quat_mul(quat_conj(s.q_body_to_eci), q_target))
        if qe[0] < 0:
            qe = -qe
        err_vec = qe[1:]
        omega_meas = s.omega_body_rad_s.copy() if s.gyro_valid else np.zeros(3)

        C_b2i = quat_to_dcm(s.q_body_to_eci)
        b_eci = earth_dipole_field_eci_t(s.r_eci_km)
        b_body = C_b2i.T @ b_eci
        mag_torque = np.zeros(3)
        rw_torque = np.zeros(3)

        if s.mode in (Mode.BOOT, Mode.DETUMBLE):
            if self._last_b_body_t is not None:
                bdot = (b_body - self._last_b_body_t) / dt_s
                dipole = -self.cfg.bdot_gain_am2_s_t * bdot
                dipole = np.clip(
                    dipole,
                    -self.cfg.magnetorquer_max_dipole_am2,
                    self.cfg.magnetorquer_max_dipole_am2,
                )
                mag_torque = np.cross(dipole, b_body)
        else:
            rw_torque = 2.0 * self.cfg.kp * err_vec - self.cfg.kd * omega_meas
            max_t = self.cfg.wheel_torque_max_nm * self._wheel_scale
            rw_torque = np.clip(rw_torque, -max_t, max_t)
            for i in range(3):
                h = s.wheel_momentum_nms[i]
                if abs(h) >= self.cfg.wheel_momentum_max_nms and (-rw_torque[i]) * h > 0:
                    rw_torque[i] = 0.0

        self._last_b_body_t = b_body.copy()
        total_torque = rw_torque + mag_torque
        I = self.cfg.inertia_kg_m2
        H_body = I @ s.omega_body_rad_s
        omega_dot = np.linalg.solve(I, total_torque - np.cross(s.omega_body_rad_s, H_body))
        s.omega_body_rad_s = s.omega_body_rad_s + omega_dot * dt_s
        s.q_body_to_eci = integrate_quaternion(s.q_body_to_eci, s.omega_body_rad_s, dt_s)
        s.wheel_momentum_nms = np.clip(
            s.wheel_momentum_nms - rw_torque * dt_s,
            -self.cfg.wheel_momentum_max_nms,
            self.cfg.wheel_momentum_max_nms,
        )
        return quat_error_angle_deg(q_target, s.q_body_to_eci)

    def _power_step(self, sun_hat: np.ndarray, dt_s: float) -> Tuple[float, float]:
        s = self.state
        C = quat_to_dcm(s.q_body_to_eci)
        panel_normal_eci = C[:, 0]
        incidence = max(0.0, float(np.dot(panel_normal_eci, sun_hat)))
        solar_w = 0.0 if s.eclipse else self.cfg.solar_array_w * incidence
        if s.mode == Mode.SAFE:
            load_w = self.cfg.load_safe_w
        elif s.mode == Mode.DOWNLINK:
            load_w = self.cfg.load_downlink_w
        else:
            load_w = self.cfg.load_nominal_w + (18.0 if s.payload_enabled else 0.0)
        load_w += self._power_fault_w
        s.battery_wh = clamp(
            s.battery_wh + (solar_w - load_w) * dt_s / 3600.0,
            0.0,
            self.cfg.battery_capacity_wh,
        )
        return solar_w, load_w

    def _update_comms(self) -> None:
        elev, rng = ground_station_elevation_deg(
            self.state.r_eci_km,
            self.now,
            self.cfg.ground_lat_deg,
            self.cfg.ground_lon_deg,
            self.cfg.ground_alt_km,
        )
        self.state.comm_elevation_deg = elev
        self.state.slant_range_km = rng
        self.state.comm_visible = elev >= self.cfg.min_elevation_deg and not self._forced_comm_loss

    def _fdir_and_mode(self, att_err_deg: float, dt_s: float) -> None:
        s = self.state
        soc = 100.0 * s.battery_wh / self.cfg.battery_capacity_wh
        wheel_sat = 100.0 * float(np.max(np.abs(s.wheel_momentum_nms))) / self.cfg.wheel_momentum_max_nms
        rate_deg_s = math.degrees(norm(s.omega_body_rad_s))

        if s.mode in (Mode.NOMINAL, Mode.DOWNLINK) and att_err_deg > 35.0:
            self._attitude_bad_s += dt_s
        else:
            self._attitude_bad_s = max(0.0, self._attitude_bad_s - 2.0 * dt_s)

        critical = None
        if soc < 18.0:
            critical = f"LOW_BATTERY_{soc:.1f}%"
        elif wheel_sat > 97.0:
            critical = f"WHEEL_SATURATION_{wheel_sat:.0f}%"
        elif self._attitude_bad_s > 20.0:
            critical = f"ATTITUDE_ERROR_{att_err_deg:.1f}deg"
        elif not s.star_tracker_valid and rate_deg_s > 2.0:
            critical = "STAR_TRACKER_LOSS_HIGH_RATE"

        if critical and s.mode != Mode.SAFE:
            s.mode = Mode.SAFE
            s.safe_reason = critical
            s.payload_enabled = False
            self.events.append(f"FDIR -> SAFE: {critical}")

        if s.mode == Mode.SAFE:
            recovery_ok = (
                soc > 35.0
                and wheel_sat < 85.0
                and att_err_deg < 10.0
                and s.star_tracker_valid
                and s.gyro_valid
            )
            self._safe_recovery_s = self._safe_recovery_s + dt_s if recovery_ok else 0.0
            if self._safe_recovery_s >= 60.0:
                s.mode = Mode.SUN_ACQUIRE
                s.safe_reason = ""
                self._safe_recovery_s = 0.0
                self.events.append("FDIR SAFE RECOVERY -> SUN_ACQUIRE")
            return

        if s.mode == Mode.BOOT and s.sim_time_s >= 5.0:
            s.mode = Mode.DETUMBLE
            self.events.append("MODE -> DETUMBLE")
        elif s.mode == Mode.DETUMBLE and rate_deg_s < 0.35:
            s.mode = Mode.SUN_ACQUIRE
            self.events.append("MODE -> SUN_ACQUIRE")
        elif s.mode == Mode.SUN_ACQUIRE and att_err_deg < 5.0 and soc > 30.0:
            s.mode = Mode.NOMINAL
            self.events.append("MODE -> NOMINAL")
        elif s.mode in (Mode.NOMINAL, Mode.DOWNLINK):
            s.mode = Mode.DOWNLINK if s.comm_visible else Mode.NOMINAL

        s.payload_enabled = (
            s.mode == Mode.NOMINAL
            and soc > 45.0
            and not s.eclipse
            and att_err_deg < 3.0
        )

    def step(self, dt_s: float = 1.0) -> Dict[str, float | str | bool]:
        if dt_s <= 0 or dt_s > 10:
            raise ValueError("dt_s must be >0 and <=10 seconds")

        s = self.state
        s.r_eci_km, s.v_eci_km_s = rk4_orbit_step(s.r_eci_km, s.v_eci_km_s, dt_s)
        s.sim_time_s += dt_s

        sun_hat = sun_vector_eci(self.now)
        s.eclipse = in_cylindrical_eclipse(s.r_eci_km, sun_hat)
        self._update_comms()

        q_target = (
            self._sun_safe_target_quat(sun_hat)
            if s.mode in (Mode.BOOT, Mode.DETUMBLE, Mode.SUN_ACQUIRE, Mode.SAFE)
            else self._nadir_target_quat()
        )
        att_err = self._attitude_step(q_target, dt_s)
        solar_w, load_w = self._power_step(sun_hat, dt_s)
        self._fdir_and_mode(att_err, dt_s)

        soc = 100.0 * s.battery_wh / self.cfg.battery_capacity_wh
        wheel_sat = 100.0 * float(np.max(np.abs(s.wheel_momentum_nms))) / self.cfg.wheel_momentum_max_nms
        altitude = norm(s.r_eci_km) - R_EARTH_KM
        one_way_ms = 1000.0 * s.slant_range_km / C_KM_S

        return {
            "utc": self.now.isoformat(),
            "mode": s.mode.value,
            "altitude_km": altitude,
            "speed_km_s": norm(s.v_eci_km_s),
            "attitude_error_deg": att_err,
            "body_rate_deg_s": math.degrees(norm(s.omega_body_rad_s)),
            "wheel_saturation_pct": wheel_sat,
            "battery_soc_pct": soc,
            "solar_w": solar_w,
            "load_w": load_w,
            "eclipse": s.eclipse,
            "comm_visible": s.comm_visible,
            "ground_elevation_deg": s.comm_elevation_deg,
            "slant_range_km": s.slant_range_km,
            "one_way_light_time_ms": one_way_ms,
            "star_tracker_valid": s.star_tracker_valid,
            "gyro_valid": s.gyro_valid,
            "payload_enabled": s.payload_enabled,
            "safe_reason": s.safe_reason,
        }
