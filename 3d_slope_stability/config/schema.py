from dataclasses import dataclass
from typing import Literal, Optional, Tuple


InterpolationMode = Literal[
    "a1",
    "b1",
    "b2",
    "b3",
    "b4",
    "b5",
    "b6",
    "c1",
    "c2",
    "c3",
    "c4",
    "c5",
    "c6",
]
ALLOWED_INTERPOLATION_MODES = {
    "a1",
    "b1",
    "b2",
    "b3",
    "b4",
    "b5",
    "b6",
    "c1",
    "c2",
    "c3",
    "c4",
    "c5",
    "c6",
}

SlipSurfaceMode = Literal["ellipsoid", "user_defined"]


@dataclass(frozen=True)
class GridConfig:
    """Grid/canvas bounds in canonical coordinate system."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    col_x_max: int
    col_y_max: int

    def __post_init__(self) -> None:
        if not (self.x_min < self.x_max and self.y_min < self.y_max and self.z_min < self.z_max):
            raise ValueError("Grid bounds must be strictly increasing")
        if self.col_x_max <= 0 or self.col_y_max <= 0:
            raise ValueError("col_x_max and col_y_max must be > 0")


@dataclass(frozen=True)
class InterpolationConfig:
    """Interpolation policy for one surface input."""

    mode: InterpolationMode = "a1"
    std_max: float = 150.0

    def __post_init__(self) -> None:
        if self.mode not in ALLOWED_INTERPOLATION_MODES:
            raise ValueError(f"Unsupported interpolation mode: {self.mode}")
        if self.std_max <= 0:
            raise ValueError("std_max must be > 0")


@dataclass(frozen=True)
class SlipSurfaceConfig:
    """Slip surface definition, either ellipsoid or user-defined DEM."""

    mode: SlipSurfaceMode
    ellipsoid_center: Optional[Tuple[float, float, float]] = None
    ellipsoid_radii: Optional[Tuple[float, float, float]] = None
    user_defined_surface_path: Optional[str] = None
    user_defined_interpolation: InterpolationMode = "a1"

    def __post_init__(self) -> None:
        if self.mode == "ellipsoid":
            if self.ellipsoid_center is None or self.ellipsoid_radii is None:
                raise ValueError("Ellipsoid mode requires center and radii")
            if any(v <= 0 for v in self.ellipsoid_radii):
                raise ValueError("Ellipsoid radii must be > 0")
        elif self.mode == "user_defined":
            if not self.user_defined_surface_path:
                raise ValueError("User-defined mode requires surface file path")
        else:
            raise ValueError("Unsupported slip surface mode")

