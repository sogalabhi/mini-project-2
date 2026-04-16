"""Canonical analysis row builder and export helpers."""

from .analysis_rows import (
    build_analysis_rows,
    build_legacy_comparison_rows,
    validate_analysis_rows,
)

__all__ = [
    "build_analysis_rows",
    "validate_analysis_rows",
    "build_legacy_comparison_rows",
]

