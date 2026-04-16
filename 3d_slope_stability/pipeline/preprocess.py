from typing import Mapping, Optional, Sequence, Tuple

from ..analysis.analysis_rows import build_analysis_rows, validate_analysis_rows
from ..config.schema import GridConfig, SlipSurfaceConfig
from ..domain.models import AnalysisRow, MaterialDefinition, SurfaceDataset
from ..geometry.grid import build_grid_axes
from ..geometry.interpolation import interpolate_surface_to_grid
from ..geometry.surfaces import intersect_columns_with_slip_surface, sample_slip_surface
from ..hydro.pore_pressure import hydro_state_from_levels
from ..strength.resolver import resolve_strength_state


def build_columns(
    *,
    top_surface: SurfaceDataset,
    grid_config: GridConfig,
    slip_surface_config: SlipSurfaceConfig,
    materials: Mapping[str, MaterialDefinition],
    user_slip_surface: Optional[SurfaceDataset] = None,
    water_level_z: Optional[float] = None,
) -> Tuple[list[AnalysisRow], dict]:
    """
    Build canonical analysis rows from prevalidated inputs.
    """
    axes = build_grid_axes(grid_config)
    top_interp = interpolate_surface_to_grid(top_surface, axes.x_edges, axes.y_edges)
    slip_sample = sample_slip_surface(slip_surface_config, axes, user_surface=user_slip_surface)
    intersections = intersect_columns_with_slip_surface(top_interp, slip_sample, z_min=grid_config.z_min)

    first_material = next(iter(materials.values())) if materials else MaterialDefinition(
        name="default", model_type=1, model_parameters=(30.0, 0.0), unit_weight=18.0
    )
    material_lookup = {"default": first_material}
    hydro_lookup = {}
    strength_lookup = {}
    for inter in intersections.intersections:
        if not inter.valid or inter.base_z is None:
            continue
        z_top = (
            top_interp.z_grid[inter.ix][inter.iy]
            + top_interp.z_grid[inter.ix + 1][inter.iy]
            + top_interp.z_grid[inter.ix + 1][inter.iy + 1]
            + top_interp.z_grid[inter.ix][inter.iy + 1]
        ) / 4.0
        wl = z_top if water_level_z is None else water_level_z
        hydro_lookup[inter.column_id] = hydro_state_from_levels(
            water_level_z=wl,
            base_level_z=inter.base_z,
            water_unit_weight=9.81,
            base_dip_rad=0.0,
        )
        effective_stress = max(0.0, first_material.unit_weight * max(0.0, z_top - inter.base_z) - hydro_lookup[inter.column_id].pore_pressure)
        strength_lookup[inter.column_id] = resolve_strength_state(
            first_material,
            z=inter.base_z,
            z_top=z_top,
            effective_normal_stress=effective_stress,
        )

    rows = build_analysis_rows(
        top_surface=top_interp,
        intersections=intersections,
        material_lookup=material_lookup,
        hydro_lookup=hydro_lookup,
        strength_lookup=strength_lookup,
    )
    validate_analysis_rows(rows)

    diagnostics = {
        "column_count_total": len(intersections.intersections),
        "column_count_valid": intersections.valid_count,
        "column_count_excluded": intersections.excluded_count,
        "intersection_reasons": intersections.reasons,
    }
    return rows, diagnostics

