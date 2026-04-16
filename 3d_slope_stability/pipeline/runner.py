from typing import Mapping, Optional, Sequence

from ..config.method_options import MethodRunConfig
from ..config.schema import GridConfig, SlipSurfaceConfig
from ..domain.models import AnalysisRow, MaterialDefinition, PipelineResult, SurfaceDataset
from ..io.csv_writer import write_rows_csv
from ..io.parsers import parse_surface_inputs
from .dispatcher import dispatch_method
from .preprocess import build_columns


def run_method(rows: list[AnalysisRow], method_config: MethodRunConfig):
    """Run one method on already-built canonical rows."""
    return dispatch_method(rows, method_config)


def run_pipeline(
    *,
    method_config: MethodRunConfig,
    grid_config: GridConfig,
    slip_surface_config: SlipSurfaceConfig,
    materials: Mapping[str, MaterialDefinition],
    top_surface: Optional[SurfaceDataset] = None,
    user_slip_surface: Optional[SurfaceDataset] = None,
    surface_paths: Optional[Sequence[str]] = None,
    surface_types: Optional[Sequence[str]] = None,
    interpolation_modes: Optional[Sequence[str]] = None,
    water_level_z: Optional[float] = None,
    export_rows_path: Optional[str] = None,
) -> PipelineResult:
    """
    End-to-end pipeline:
    parse -> validate -> interpolate -> grid -> intersect -> hydro/strength -> rows -> dispatch method
    """
    generated_files = []
    if top_surface is None:
        if not (surface_paths and surface_types and interpolation_modes):
            raise ValueError("Provide top_surface or surface_paths/surface_types/interpolation_modes")
        surfaces = parse_surface_inputs(surface_paths, surface_types, interpolation_modes)
        # pick first top tag if present, else first surface.
        top_surface = next((s for s in surfaces if s.label == "tt"), surfaces[0])
        if slip_surface_config.mode == "user_defined" and user_slip_surface is None:
            user_slip_surface = next((s for s in surfaces if s.path == slip_surface_config.user_defined_surface_path), None)

    rows, diagnostics = build_columns(
        top_surface=top_surface,
        grid_config=grid_config,
        slip_surface_config=slip_surface_config,
        materials=materials,
        user_slip_surface=user_slip_surface,
        water_level_z=water_level_z,
    )
    method_result = run_method(rows, method_config)

    if export_rows_path:
        export_payload = [
            {
                "column_id": r.column_id,
                "x": r.x,
                "y": r.y,
                "weight": r.column_state.weight,
                "pore_pressure": r.column_state.pore_pressure,
                "effective_normal_stress": r.column_state.effective_normal_stress,
            }
            for r in rows
        ]
        path = write_rows_csv(export_rows_path, export_payload)
        generated_files.append(str(path))

    return PipelineResult(
        column_count=len(rows),
        analysis_rows=rows,
        method_result=method_result,
        generated_files=generated_files,
        diagnostics=diagnostics,
    )

