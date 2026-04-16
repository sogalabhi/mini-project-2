"""
Import-safe package root for the clean 3D LEM rewrite.

This package intentionally performs no file IO, no solver execution,
and no global runtime side effects at import time.
"""

from .config.settings import RuntimeSettings
from .domain.models import (
    AnalysisRow,
    ColumnState,
    DEMPoint,
    DirectionResult,
    MethodComputationResult,
    PipelineResult,
)
from .pipeline import build_columns, run_method, run_pipeline

__all__ = [
    "RuntimeSettings",
    "build_columns",
    "run_method",
    "run_pipeline",
    "DEMPoint",
    "ColumnState",
    "AnalysisRow",
    "DirectionResult",
    "MethodComputationResult",
    "PipelineResult",
]

