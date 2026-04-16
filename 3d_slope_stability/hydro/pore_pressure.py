from ..domain.models import HydroState
from .groundwater import pore_pressure_from_head


def hydro_state_from_levels(
    water_level_z: float,
    base_level_z: float,
    water_unit_weight: float,
    base_dip_rad: float,
) -> HydroState:
    pore = pore_pressure_from_head(
        water_level_z=water_level_z,
        base_level_z=base_level_z,
        water_unit_weight=water_unit_weight,
        base_dip_rad=base_dip_rad,
    )
    head = 0.0 if water_unit_weight <= 0 else pore / water_unit_weight
    return HydroState(pressure_head=head, pore_pressure=pore)

