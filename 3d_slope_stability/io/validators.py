from math import isfinite
from typing import Iterable, Sequence

from ..config.schema import GridConfig
from ..domain.errors import InputValidationError
from ..domain.models import DEMPoint


def validate_surface_definition_lists(
    names: Sequence[str],
    types: Sequence[str],
    interpolation_modes: Sequence[str],
) -> None:
    if not names:
        raise InputValidationError("Surface list must not be empty")
    if len(names) != len(types) or len(names) != len(interpolation_modes):
        raise InputValidationError(
            "Surface names, types, and interpolation mode lists must have equal length"
        )
    allowed_types = {"rr", "gw", "tt"}
    for idx, surface_type in enumerate(types):
        if not surface_type:
            raise InputValidationError(f"Surface type at index {idx} is empty")
        # Preserve extensibility while still validating obvious malformed values.
        if len(surface_type) > 12 or " " in surface_type:
            raise InputValidationError(f"Surface type '{surface_type}' is invalid")
        if surface_type in allowed_types:
            continue


def validate_dem_points(points: Iterable[DEMPoint], label: str = "surface") -> None:
    point_list = list(points)
    if not point_list:
        raise InputValidationError(f"{label} has no points")
    for idx, point in enumerate(point_list):
        if not (isfinite(point.x) and isfinite(point.y) and isfinite(point.z)):
            raise InputValidationError(
                f"{label} point at index {idx} contains non-finite values"
            )


def validate_grid_config(config: GridConfig) -> None:
    if config.col_x_max < 1 or config.col_y_max < 1:
        raise InputValidationError("Grid columns must be >= 1 in both directions")
    if config.col_x_max > 5000 or config.col_y_max > 5000:
        raise InputValidationError("Grid dimension too large for safe deterministic processing")

