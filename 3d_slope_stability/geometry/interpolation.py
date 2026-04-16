from typing import Iterable, Tuple

import numpy as np

from ..domain.errors import InterpolationError
from ..domain.models import DEMPoint, InterpolatedSurface, SurfaceDataset


def _points_to_arrays(points: Iterable[DEMPoint]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = []
    y = []
    z = []
    for point in points:
        x.append(point.x)
        y.append(point.y)
        z.append(point.z)
    if not x:
        raise InterpolationError("No points supplied for interpolation")
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float), np.asarray(z, dtype=float)


def _idw_predict(
    x_src: np.ndarray,
    y_src: np.ndarray,
    z_src: np.ndarray,
    x_targets: np.ndarray,
    y_targets: np.ndarray,
    power: float = 2.0,
) -> np.ndarray:
    """
    Deterministic inverse distance weighting interpolation.

    This is used as stable fallback and default for linear-like mode in Phase 3.
    """
    z_grid = np.zeros((len(x_targets), len(y_targets)), dtype=float)
    for i, x_t in enumerate(x_targets):
        dx = x_src - x_t
        for j, y_t in enumerate(y_targets):
            dy = y_src - y_t
            dist2 = dx * dx + dy * dy
            exact_idx = np.where(dist2 == 0.0)[0]
            if exact_idx.size > 0:
                z_grid[i, j] = float(z_src[exact_idx[0]])
                continue
            weights = 1.0 / np.power(dist2, power / 2.0)
            z_grid[i, j] = float(np.sum(weights * z_src) / np.sum(weights))
    return z_grid


def interpolate_surface_to_grid(
    surface: SurfaceDataset,
    x_values: Tuple[float, ...],
    y_values: Tuple[float, ...],
) -> InterpolatedSurface:
    """
    Interpolate a surface onto target axes with deterministic output ordering.

    Supported behavior in Phase 3:
    - `a1`: deterministic IDW interpolation (linear-like fallback).
    - `b*`/`c*`: currently fallback to deterministic IDW while preserving mode metadata.
      (kriging backends can be added behind this API in later phases).
    """
    if not x_values or not y_values:
        raise InterpolationError("x_values and y_values must not be empty")

    x_src, y_src, z_src = _points_to_arrays(surface.points)
    x_targets = np.asarray(x_values, dtype=float)
    y_targets = np.asarray(y_values, dtype=float)

    mode = surface.interpolation_mode
    if not mode:
        raise InterpolationError("Surface interpolation mode is empty")

    z_grid = _idw_predict(x_src, y_src, z_src, x_targets, y_targets)
    z_tuple = tuple(tuple(float(v) for v in row.tolist()) for row in z_grid)
    return InterpolatedSurface(
        label=surface.label,
        x_values=tuple(float(v) for v in x_targets.tolist()),
        y_values=tuple(float(v) for v in y_targets.tolist()),
        z_grid=z_tuple,
    )

