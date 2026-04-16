"""Deterministic geometry and interpolation engine."""

from .grid import build_grid_axes
from .interpolation import interpolate_surface_to_grid
from .primitives import (
    area_3d_polygon,
    dip_and_direction_from_points,
    rad_to_deg,
    tetra_volume,
)
from .surfaces import intersect_columns_with_slip_surface, sample_slip_surface

__all__ = [
    "build_grid_axes",
    "interpolate_surface_to_grid",
    "sample_slip_surface",
    "intersect_columns_with_slip_surface",
    "area_3d_polygon",
    "tetra_volume",
    "dip_and_direction_from_points",
    "rad_to_deg",
]

