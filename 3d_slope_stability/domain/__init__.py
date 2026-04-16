"""Typed domain models and errors for 3D LEM rewrite."""

from .enums import InterpolationType, MethodId, ShearModelType, SlipSurfaceType
from .errors import (
    ConvergenceError,
    GeometryError,
    InputValidationError,
    InterpolationError,
    MethodNotSupportedError,
)
from .models import (
    AnalysisRow,
    ColumnIntersectionState,
    ColumnIntersectionSummary,
    ColumnState,
    DEMPoint,
    DirectionResult,
    GridAxes,
    HydroState,
    InterpolatedSurface,
    MaterialDefinition,
    MethodComputationResult,
    PipelineResult,
    SlipSurfaceSample,
    StrengthState,
    SurfaceDataset,
)

__all__ = [
    "MethodId",
    "InterpolationType",
    "SlipSurfaceType",
    "ShearModelType",
    "InputValidationError",
    "InterpolationError",
    "GeometryError",
    "ConvergenceError",
    "MethodNotSupportedError",
    "DEMPoint",
    "SlipSurfaceSample",
    "ColumnIntersectionState",
    "ColumnIntersectionSummary",
    "HydroState",
    "StrengthState",
    "ColumnState",
    "AnalysisRow",
    "DirectionResult",
    "SurfaceDataset",
    "MaterialDefinition",
    "GridAxes",
    "InterpolatedSurface",
    "MethodComputationResult",
    "PipelineResult",
]

