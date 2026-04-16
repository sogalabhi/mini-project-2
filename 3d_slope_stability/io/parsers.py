from typing import Sequence, Tuple

from ..config.schema import InterpolationConfig
from ..domain.models import SurfaceDataset
from .csv_reader import read_xyz_csv
from .validators import validate_surface_definition_lists


def parse_surface_inputs(
    names: Sequence[str],
    types: Sequence[str],
    interpolation_modes: Sequence[str],
    std_max: float = 150.0,
) -> Tuple[SurfaceDataset, ...]:
    """
    Parse and validate surface definitions into typed immutable objects.
    """
    validate_surface_definition_lists(names, types, interpolation_modes)

    surfaces = []
    for idx, name in enumerate(names):
        mode = interpolation_modes[idx]
        _ = InterpolationConfig(mode=mode, std_max=std_max)
        points = tuple(read_xyz_csv(name))
        surfaces.append(
            SurfaceDataset(
                label=types[idx],
                path=name,
                points=points,
                interpolation_mode=mode,
            )
        )
    return tuple(surfaces)

