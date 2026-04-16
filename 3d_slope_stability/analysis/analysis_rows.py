import math
from typing import Dict, Iterable, List, Mapping, Tuple

from ..domain.errors import InputValidationError
from ..domain.models import (
    AnalysisRow,
    ColumnIntersectionSummary,
    ColumnState,
    HydroState,
    InterpolatedSurface,
    MaterialDefinition,
    StrengthState,
)


def _mean_corner_value(grid: Tuple[Tuple[float, ...], ...], ix: int, iy: int) -> float:
    corners = (
        grid[ix][iy],
        grid[ix + 1][iy],
        grid[ix + 1][iy + 1],
        grid[ix][iy + 1],
    )
    return float(sum(corners) / 4.0)


def _cell_dip_and_direction(
    x_values: Tuple[float, ...],
    y_values: Tuple[float, ...],
    z_grid: Tuple[Tuple[float, ...], ...],
    ix: int,
    iy: int,
) -> Tuple[float, float]:
    # Bilinear cell-gradient approximation from corner values.
    dx = max(1e-9, x_values[ix + 1] - x_values[ix])
    dy = max(1e-9, y_values[iy + 1] - y_values[iy])

    z00 = z_grid[ix][iy]
    z10 = z_grid[ix + 1][iy]
    z11 = z_grid[ix + 1][iy + 1]
    z01 = z_grid[ix][iy + 1]

    dzdx = ((z10 - z00) + (z11 - z01)) / (2.0 * dx)
    dzdy = ((z01 - z00) + (z11 - z10)) / (2.0 * dy)
    slope_mag = math.sqrt(dzdx * dzdx + dzdy * dzdy)
    dip = math.atan(slope_mag)

    # Direction of steepest descent.
    if slope_mag <= 1e-12:
        direction = 0.0
    else:
        direction = math.atan2(-dzdx, -dzdy) % (2.0 * math.pi)
    return float(dip), float(direction)


def build_analysis_rows(
    top_surface: InterpolatedSurface,
    intersections: ColumnIntersectionSummary,
    material_lookup: Mapping[str, MaterialDefinition],
    hydro_lookup: Mapping[int, HydroState],
    strength_lookup: Mapping[int, StrengthState],
    base_area_default: float = 1.0,
) -> List[AnalysisRow]:
    """
    Build canonical per-column analysis rows with named fields.
    """
    rows: List[AnalysisRow] = []
    x_values = top_surface.x_values
    y_values = top_surface.y_values
    z_grid = top_surface.z_grid

    for item in intersections.intersections:
        if not item.valid or item.base_z is None:
            continue
        center_x = float((x_values[item.ix] + x_values[item.ix + 1]) / 2.0)
        center_y = float((y_values[item.iy] + y_values[item.iy + 1]) / 2.0)
        z_top = _mean_corner_value(z_grid, item.ix, item.iy)
        z_bottom = float(item.base_z)
        thickness = max(0.0, z_top - z_bottom)

        material_name = "default"
        if material_lookup:
            material_name = next(iter(material_lookup.keys()))
        material = material_lookup.get(material_name)
        unit_weight = material.unit_weight if material else 18.0

        volume = base_area_default * thickness
        weight = volume * unit_weight

        hydro = hydro_lookup.get(item.column_id, HydroState(pressure_head=0.0, pore_pressure=0.0))
        strength = strength_lookup.get(
            item.column_id,
            StrengthState(
                friction_angle_rad=0.0,
                cohesion=0.0,
                shear_strength=0.0,
                model_name="unknown",
                diagnostics={},
            ),
        )
        effective_normal_stress = max(0.0, (weight / max(base_area_default, 1e-9)) - hydro.pore_pressure)
        dip_rad, dip_dir_rad = _cell_dip_and_direction(x_values, y_values, z_grid, item.ix, item.iy)

        state = ColumnState(
            column_id=item.column_id,
            center_x=center_x,
            center_y=center_y,
            z_top=z_top,
            z_bottom=z_bottom,
            base_area=base_area_default,
            side_areas=(1.0, 1.0, 1.0, 1.0),
            volume=volume,
            weight=weight,
            base_dip_rad=dip_rad,
            base_dip_direction_rad=dip_dir_rad,
            pore_pressure=hydro.pore_pressure,
            effective_normal_stress=effective_normal_stress,
            cohesion=strength.cohesion,
            friction_angle_rad=strength.friction_angle_rad,
            shear_model_type=material.model_type if material else 1,
            material_name=material_name,
            diagnostics={
                "strength_model": strength.model_name,
                "shear_strength": strength.shear_strength,
                **strength.diagnostics,
            },
        )
        rows.append(
            AnalysisRow(
                column_id=item.column_id,
                x=center_x,
                y=center_y,
                column_state=state,
            )
        )
    return rows


def validate_analysis_rows(rows: Iterable[AnalysisRow]) -> None:
    required = (
        "column_id",
        "x",
        "y",
        "z_top",
        "z_bottom",
        "base_area",
        "volume",
        "weight",
        "effective_normal_stress",
    )
    for row in rows:
        state = row.column_state
        row_map = {
            "column_id": row.column_id,
            "x": row.x,
            "y": row.y,
            "z_top": state.z_top,
            "z_bottom": state.z_bottom,
            "base_area": state.base_area,
            "volume": state.volume,
            "weight": state.weight,
            "effective_normal_stress": state.effective_normal_stress,
        }
        for key in required:
            value = row_map[key]
            if value is None:
                raise InputValidationError(f"Missing required field '{key}' for column {row.column_id}")
        if state.z_top < state.z_bottom:
            raise InputValidationError(f"Invalid geometry z_top < z_bottom for column {row.column_id}")
        if state.base_area <= 0:
            raise InputValidationError(f"base_area must be > 0 for column {row.column_id}")


def build_legacy_comparison_rows(rows: Iterable[AnalysisRow]) -> List[Dict[str, float]]:
    """
    Optional legacy-like flat export map for side-by-side comparison.
    """
    out: List[Dict[str, float]] = []
    for row in rows:
        s = row.column_state
        out.append(
            {
                "column_id": float(row.column_id),
                "x": float(row.x),
                "y": float(row.y),
                "pore_pressure": float(s.pore_pressure),
                "effective_normal_stress": float(s.effective_normal_stress),
                "cohesion": float(s.cohesion),
                "friction_angle_rad": float(s.friction_angle_rad),
                "weight": float(s.weight),
                "volume": float(s.volume),
                "z_top": float(s.z_top),
                "z_bottom": float(s.z_bottom),
            }
        )
    return out

