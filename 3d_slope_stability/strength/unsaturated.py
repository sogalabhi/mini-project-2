import math


def unsaturated_shear_increment(
    phi_b_rad: float,
    air_entry_value: float,
    matric_suction: float,
    suction_cap: float,
) -> float:
    if matric_suction <= air_entry_value:
        return 0.0
    usable_suction = min(matric_suction - air_entry_value, max(0.0, suction_cap))
    return usable_suction * math.tan(phi_b_rad)

