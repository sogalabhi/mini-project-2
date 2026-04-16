from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SolverConfig:
    """Generic solver iteration controls."""

    max_iterations: int = 200
    tol_fs: float = 1e-3
    damping: float = 1.0

    def __post_init__(self) -> None:
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be > 0")
        if self.tol_fs <= 0:
            raise ValueError("tol_fs must be > 0")
        if not (0 < self.damping <= 1.0):
            raise ValueError("damping must be in (0, 1]")


@dataclass(frozen=True)
class DirectionSearchConfig:
    """Direction search settings in degrees at API boundary."""

    spacing_deg: float = 0.5
    tolerance_deg: float = 10.0
    user_direction_deg: Optional[float] = None

    def __post_init__(self) -> None:
        if self.spacing_deg <= 0:
            raise ValueError("spacing_deg must be > 0")
        if self.tolerance_deg < 0:
            raise ValueError("tolerance_deg must be >= 0")
        if self.user_direction_deg is not None and not (0.0 <= self.user_direction_deg <= 360.0):
            raise ValueError("user_direction_deg must be in [0, 360]")


@dataclass(frozen=True)
class MethodRunConfig:
    """Combined options used by one method run."""

    method_id: int
    solver: SolverConfig = SolverConfig()
    direction: DirectionSearchConfig = DirectionSearchConfig()
    use_side_resistance: bool = True

    def __post_init__(self) -> None:
        if self.method_id not in {1, 2, 3, 4, 5, 6, 7}:
            raise ValueError("method_id must be one of {1,2,3,4,5,6,7}")

