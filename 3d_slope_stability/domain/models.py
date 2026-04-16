from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .enums import MethodId


@dataclass(frozen=True)
class DEMPoint:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class SurfaceDataset:
    """Named XYZ surface samples loaded from input files."""

    label: str
    path: str
    points: Tuple[DEMPoint, ...]
    interpolation_mode: str


@dataclass(frozen=True)
class MaterialDefinition:
    """Material definition for strength/weight modeling."""

    name: str
    model_type: int
    model_parameters: Tuple[float, ...]
    unit_weight: float


@dataclass(frozen=True)
class GridAxes:
    """Deterministic grid axes in world coordinates."""

    x_edges: Tuple[float, ...]
    y_edges: Tuple[float, ...]
    x_centers: Tuple[float, ...]
    y_centers: Tuple[float, ...]


@dataclass(frozen=True)
class InterpolatedSurface:
    """Interpolated Z grid for a surface on target axes."""

    label: str
    x_values: Tuple[float, ...]
    y_values: Tuple[float, ...]
    z_grid: Tuple[Tuple[float, ...], ...]


@dataclass(frozen=True)
class SlipSurfaceSample:
    """Slip surface sample with deterministic validity mask."""

    surface: InterpolatedSurface
    valid_mask: Tuple[Tuple[bool, ...], ...]


@dataclass(frozen=True)
class ColumnIntersectionState:
    """Per-column intersection result for slip/base selection."""

    column_id: int
    ix: int
    iy: int
    valid: bool
    base_z: Optional[float]
    reason: str


@dataclass(frozen=True)
class ColumnIntersectionSummary:
    """Aggregated intersection output with summary counters."""

    intersections: Tuple[ColumnIntersectionState, ...]
    valid_count: int
    excluded_count: int
    reasons: Dict[str, int]


@dataclass(frozen=True)
class HydroState:
    """Hydraulic state derived for a column/base point."""

    pressure_head: float
    pore_pressure: float


@dataclass(frozen=True)
class StrengthState:
    """Resolved shear strength state for a location/material."""

    friction_angle_rad: float
    cohesion: float
    shear_strength: float
    model_name: str
    diagnostics: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ColumnState:
    """
    Canonical per-column state with named fields.

    Internal angle convention in Phase 1:
    - `base_dip_rad` and `base_dip_direction_rad` are radians.
    """

    column_id: int
    center_x: float
    center_y: float
    z_top: float
    z_bottom: float
    base_area: float
    side_areas: Tuple[float, float, float, float]
    volume: float
    weight: float
    base_dip_rad: float
    base_dip_direction_rad: float
    pore_pressure: float
    effective_normal_stress: float
    cohesion: float
    friction_angle_rad: float
    shear_model_type: int
    material_name: str
    diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalysisRow:
    """
    Solver-ready canonical row representation.

    This replaces legacy positional CSV indices.
    """

    column_id: int
    x: float
    y: float
    column_state: ColumnState


@dataclass(frozen=True)
class DirectionResult:
    direction_rad: float
    converged: bool
    fs_value: Optional[float]
    iterations: int
    method_terms: Dict[str, float] = field(default_factory=dict)
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class MethodComputationResult:
    method_id: MethodId
    fs_min: Optional[float]
    critical_direction_rad: Optional[float]
    converged: bool
    direction_results: List[DirectionResult] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineResult:
    """
    End-to-end result container for preprocess + solve stages.
    """

    column_count: int
    analysis_rows: List[AnalysisRow]
    method_result: Optional[MethodComputationResult] = None
    generated_files: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)

