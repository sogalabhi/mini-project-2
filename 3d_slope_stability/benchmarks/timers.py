from contextlib import contextmanager
from time import perf_counter
from typing import Dict, Mapping, Optional

from ..analysis.analysis_rows import build_analysis_rows, validate_analysis_rows
from ..config.method_options import MethodRunConfig
from ..config.schema import GridConfig, SlipSurfaceConfig
from ..domain.models import MaterialDefinition, SurfaceDataset
from ..geometry.grid import build_grid_axes
from ..geometry.interpolation import interpolate_surface_to_grid
from ..geometry.surfaces import intersect_columns_with_slip_surface, sample_slip_surface
from ..hydro.pore_pressure import hydro_state_from_levels
from ..pipeline.dispatcher import dispatch_method
from ..strength.resolver import resolve_strength_state


@contextmanager
def _timer(stage: str, store: Dict[str, float]):
    start = perf_counter()
    yield
    store[stage] = perf_counter() - start


def profile_pipeline_stages(
    *,
    method_config: MethodRunConfig,
    grid_config: GridConfig,
    slip_surface_config: SlipSurfaceConfig,
    materials: Mapping[str, MaterialDefinition],
    top_surface: SurfaceDataset,
    user_slip_surface: Optional[SurfaceDataset] = None,
    water_level_z: Optional[float] = None,
) -> Dict[str, float]:
    """
    Stage-level timing profile:
    interpolation, grid assembly, slip intersection, hydro/strength, solver core.
    """
    timings: Dict[str, float] = {}
    with _timer("grid_assembly", timings):
        axes = build_grid_axes(grid_config)
    with _timer("interpolation", timings):
        top_interp = interpolate_surface_to_grid(top_surface, axes.x_edges, axes.y_edges)
    with _timer("slip_intersection", timings):
        slip_sample = sample_slip_surface(slip_surface_config, axes, user_surface=user_slip_surface)
        intersections = intersect_columns_with_slip_surface(top_interp, slip_sample, z_min=grid_config.z_min)
    with _timer("hydro_strength", timings):
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
            effective_stress = max(
                0.0,
                first_material.unit_weight * max(0.0, z_top - inter.base_z)
                - hydro_lookup[inter.column_id].pore_pressure,
            )
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
    with _timer("solver_core", timings):
        _ = dispatch_method(rows, method_config)
    timings["total"] = sum(timings.values())
    return timings

