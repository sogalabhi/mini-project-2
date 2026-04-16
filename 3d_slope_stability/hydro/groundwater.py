import math


def pore_pressure_from_head(
    water_level_z: float,
    base_level_z: float,
    water_unit_weight: float,
    base_dip_rad: float = 0.0,
) -> float:
    """
    Compute pore pressure from pressure head with radian-safe dip correction.
    """
    head_vertical = max(0.0, water_level_z - base_level_z)
    cos_term = max(1e-6, abs(math.cos(base_dip_rad)))
    pressure_head = head_vertical / cos_term
    return max(0.0, water_unit_weight * pressure_head)

