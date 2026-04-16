import math
from typing import Sequence, Tuple


def mohr_coulomb_shear_strength(
    effective_normal_stress: float,
    friction_angle_rad: float,
    cohesion: float,
) -> float:
    return cohesion + max(0.0, effective_normal_stress) * math.tan(friction_angle_rad)


def undrained_depth_cohesion(
    z: float,
    z_top: float,
    su_top: float,
    su_gradient: float,
    su_min: float,
    su_max: float,
) -> float:
    su = su_top + su_gradient * (z_top - z)
    return max(su_min, min(su_max, su))


def undrained_datum_cohesion(
    z: float,
    z_datum: float,
    su_datum: float,
    su_gradient: float,
    su_min: float,
    su_max: float,
) -> float:
    su = su_datum + su_gradient * abs(z_datum - z)
    return max(su_min, min(su_max, su))


def power_curve_shear_strength(
    effective_normal_stress: float,
    p_atm: float,
    a_param: float,
    b_param: float,
) -> float:
    sigma = max(1e-9, effective_normal_stress)
    return p_atm * a_param * (sigma / p_atm) ** b_param


def user_curve_shear_strength(
    effective_normal_stress: float,
    curve_points: Sequence[Tuple[float, float]],
) -> float:
    """
    Piecewise linear interpolation for user-defined shear-normal curve.
    curve_points are (normal_stress, shear_strength).
    """
    pts = sorted((float(x), float(y)) for x, y in curve_points)
    x = float(effective_normal_stress)
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for idx in range(len(pts) - 1):
        x1, y1 = pts[idx]
        x2, y2 = pts[idx + 1]
        if x1 <= x <= x2:
            ratio = 0.0 if x2 == x1 else (x - x1) / (x2 - x1)
            return y1 + ratio * (y2 - y1)
    return pts[-1][1]

