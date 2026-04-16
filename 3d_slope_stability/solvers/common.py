import math
from typing import Optional, Tuple


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if abs(denominator) < 1e-12:
        return default
    return numerator / denominator


def clip_value(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def has_converged(current: float, previous: float, tolerance: float) -> bool:
    return abs(current - previous) <= tolerance


def apply_damping(new_value: float, old_value: float, damping: float) -> float:
    return old_value + damping * (new_value - old_value)


def decompose_force_2d(force: float, direction_rad: float) -> Tuple[float, float]:
    return force * math.cos(direction_rad), force * math.sin(direction_rad)

