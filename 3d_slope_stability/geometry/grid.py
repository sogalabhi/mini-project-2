from typing import Tuple

import numpy as np

from ..config.schema import GridConfig
from ..domain.models import GridAxes
from ..io.validators import validate_grid_config


def _to_tuple(values: np.ndarray) -> Tuple[float, ...]:
    return tuple(float(v) for v in values.tolist())


def build_grid_axes(config: GridConfig) -> GridAxes:
    """
    Build deterministic edge/center coordinates using integer-indexed ordering.
    """
    validate_grid_config(config)
    x_edges = np.linspace(config.x_min, config.x_max, config.col_x_max + 1, dtype=float)
    y_edges = np.linspace(config.y_min, config.y_max, config.col_y_max + 1, dtype=float)
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2.0
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2.0
    return GridAxes(
        x_edges=_to_tuple(x_edges),
        y_edges=_to_tuple(y_edges),
        x_centers=_to_tuple(x_centers),
        y_centers=_to_tuple(y_centers),
    )

