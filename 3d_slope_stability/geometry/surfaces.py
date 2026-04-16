import math
from collections import Counter
from typing import Optional

from ..config.schema import SlipSurfaceConfig
from ..domain.errors import GeometryError
from ..domain.models import (
    ColumnIntersectionState,
    ColumnIntersectionSummary,
    GridAxes,
    InterpolatedSurface,
    SlipSurfaceSample,
    SurfaceDataset,
)
from .interpolation import interpolate_surface_to_grid


def sample_slip_surface(
    config: SlipSurfaceConfig,
    axes: GridAxes,
    user_surface: Optional[SurfaceDataset] = None,
) -> SlipSurfaceSample:
    """
    Sample slip-surface Z at edge grid coordinates and build finite-value mask.
    """
    if config.mode == "ellipsoid":
        cx, cy, cz = config.ellipsoid_center or (0.0, 0.0, 0.0)
        rx, ry, rz = config.ellipsoid_radii or (1.0, 1.0, 1.0)
        z_grid = []
        mask = []
        for x in axes.x_edges:
            row_z = []
            row_m = []
            for y in axes.y_edges:
                term = 1.0 - ((x - cx) ** 2) / (rx**2) - ((y - cy) ** 2) / (ry**2)
                if term < 0.0:
                    row_z.append(float("nan"))
                    row_m.append(False)
                else:
                    z = cz - rz * math.sqrt(term)
                    row_z.append(float(z))
                    row_m.append(True)
            z_grid.append(tuple(row_z))
            mask.append(tuple(row_m))
        surface = InterpolatedSurface(
            label="slip_ellipsoid",
            x_values=axes.x_edges,
            y_values=axes.y_edges,
            z_grid=tuple(z_grid),
        )
        return SlipSurfaceSample(surface=surface, valid_mask=tuple(mask))

    if config.mode == "user_defined":
        if user_surface is None:
            raise GeometryError("User-defined slip surface mode requires user surface dataset")
        interp = interpolate_surface_to_grid(user_surface, axes.x_edges, axes.y_edges)
        mask = tuple(
            tuple(math.isfinite(z) for z in row)
            for row in interp.z_grid
        )
        return SlipSurfaceSample(surface=interp, valid_mask=mask)

    raise GeometryError(f"Unsupported slip surface mode: {config.mode}")


def intersect_columns_with_slip_surface(
    top_surface: InterpolatedSurface,
    slip_sample: SlipSurfaceSample,
    z_min: float,
) -> ColumnIntersectionSummary:
    """
    Determine valid columns by four-corner checks and compute effective base elevation.
    """
    z_top = top_surface.z_grid
    z_slip = slip_sample.surface.z_grid
    mask = slip_sample.valid_mask

    nx = len(z_slip)
    ny = len(z_slip[0]) if nx else 0
    if len(z_top) != nx or (ny and len(z_top[0]) != ny):
        raise GeometryError("Top surface and slip surface grid shapes do not match")

    intersections = []
    reasons = Counter()
    column_id = 1
    for ix in range(nx - 1):
        for iy in range(ny - 1):
            corners = [(ix, iy), (ix + 1, iy), (ix + 1, iy + 1), (ix, iy + 1)]
            if not all(mask[cx][cy] for cx, cy in corners):
                reason = "outside_slip_surface"
                intersections.append(
                    ColumnIntersectionState(column_id, ix, iy, False, None, reason)
                )
                reasons[reason] += 1
                column_id += 1
                continue

            slip_vals = [z_slip[cx][cy] for cx, cy in corners]
            top_vals = [z_top[cx][cy] for cx, cy in corners]

            if any(sv > tv for sv, tv in zip(slip_vals, top_vals)):
                reason = "slip_above_top_surface"
                intersections.append(
                    ColumnIntersectionState(column_id, ix, iy, False, None, reason)
                )
                reasons[reason] += 1
                column_id += 1
                continue

            base_z = sum(slip_vals) / 4.0
            if base_z < z_min:
                reason = "below_minimum_z"
                intersections.append(
                    ColumnIntersectionState(column_id, ix, iy, False, None, reason)
                )
                reasons[reason] += 1
                column_id += 1
                continue

            intersections.append(
                ColumnIntersectionState(column_id, ix, iy, True, float(base_z), "valid")
            )
            reasons["valid"] += 1
            column_id += 1

    valid_count = reasons.get("valid", 0)
    excluded_count = len(intersections) - valid_count
    return ColumnIntersectionSummary(
        intersections=tuple(intersections),
        valid_count=valid_count,
        excluded_count=excluded_count,
        reasons=dict(reasons),
    )

