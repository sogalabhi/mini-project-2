import importlib
import math
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

from fastapi import HTTPException

from ..schemas.analysis_3d import Analyze3DRequest

_method_options = importlib.import_module("3d_slope_stability.config.method_options")
_schema = importlib.import_module("3d_slope_stability.config.schema")
_errors = importlib.import_module("3d_slope_stability.domain.errors")
_models = importlib.import_module("3d_slope_stability.domain.models")

DirectionSearchConfig = _method_options.DirectionSearchConfig
MethodRunConfig = _method_options.MethodRunConfig
ReinforcementConfig = _method_options.ReinforcementConfig
SolverConfig = _method_options.SolverConfig
GridConfig = _schema.GridConfig
SlipSurfaceConfig = _schema.SlipSurfaceConfig
ThreeDLEMError = _errors.ThreeDLEMError
DEMPoint = _models.DEMPoint
MaterialDefinition = _models.MaterialDefinition
SurfaceDataset = _models.SurfaceDataset


ALLOWED_METHOD_IDS = {1, 2, 3, 4, 5, 6, 7}
MAX_DEBUG_ROWS = 20000


def _bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail={"code": "invalid_3d_payload", "message": message})


def _surface_from_input(surface_input: Any) -> SurfaceDataset:
    return SurfaceDataset(
        label=surface_input.label,
        path=surface_input.path,
        interpolation_mode=surface_input.interpolation_mode,
        points=tuple(DEMPoint(x=p.x, y=p.y, z=p.z) for p in surface_input.points),
    )


def build_pipeline_kwargs(payload: Analyze3DRequest) -> Dict[str, Any]:
    if payload.method_config.method_id not in ALLOWED_METHOD_IDS:
        raise _bad_request("method_id must be one of {1,2,3,4,5,6,7}")

    projected_rows = payload.grid_config.col_x_max * payload.grid_config.col_y_max
    if payload.debug.include_analysis_rows and projected_rows > MAX_DEBUG_ROWS:
        raise _bad_request(
            f"debug.include_analysis_rows=true exceeds row safety limit ({projected_rows} > {MAX_DEBUG_ROWS})"
        )

    try:
        method_config = MethodRunConfig(
            method_id=payload.method_config.method_id,
            solver=SolverConfig(
                max_iterations=payload.method_config.solver.max_iterations,
                tol_fs=payload.method_config.solver.tol_fs,
                damping=payload.method_config.solver.damping,
            ),
            direction=DirectionSearchConfig(
                spacing_deg=payload.method_config.direction.spacing_deg,
                tolerance_deg=payload.method_config.direction.tolerance_deg,
                user_direction_deg=payload.method_config.direction.user_direction_deg,
            ),
            use_side_resistance=payload.method_config.use_side_resistance,
            reinforcement=ReinforcementConfig(
                enabled=payload.reinforcement.enabled,
                diameter=payload.reinforcement.diameter,
                length_embed=payload.reinforcement.length_embed,
                spacing_x=payload.reinforcement.spacing_x,
                spacing_y=payload.reinforcement.spacing_y,
                steel_area=payload.reinforcement.steel_area,
                yield_strength=payload.reinforcement.yield_strength,
                bond_strength=payload.reinforcement.bond_strength,
                inclination_deg=payload.reinforcement.inclination_deg,
                include_vertical_component=payload.reinforcement.include_vertical_component,
            ),
        )
        grid_config = GridConfig(**payload.grid_config.model_dump())
        slip_surface_config = SlipSurfaceConfig(**payload.slip_surface_config.model_dump())
    except (ValueError, TypeError) as exc:
        raise _bad_request(str(exc)) from exc

    materials: Dict[str, MaterialDefinition] = {}
    for material_key, material_value in payload.materials.items():
        try:
            materials[material_key] = MaterialDefinition(
                name=material_value.name,
                model_type=material_value.model_type,
                model_parameters=tuple(material_value.model_parameters),
                unit_weight=material_value.unit_weight,
            )
        except (ValueError, TypeError) as exc:
            raise _bad_request(f"invalid material '{material_key}': {exc}") from exc

    top_surface = _surface_from_input(payload.top_surface) if payload.top_surface is not None else None
    user_slip_surface = _surface_from_input(payload.user_slip_surface) if payload.user_slip_surface is not None else None

    return {
        "method_config": method_config,
        "grid_config": grid_config,
        "slip_surface_config": slip_surface_config,
        "materials": materials,
        "top_surface": top_surface,
        "user_slip_surface": user_slip_surface,
        "surface_paths": payload.surface_paths,
        "surface_types": payload.surface_types,
        "interpolation_modes": payload.interpolation_modes,
        "water_level_z": payload.water_level_z,
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(out):
        return default
    return out


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(max(0, min(len(ordered) - 1, round((len(ordered) - 1) * q))))
    return ordered[idx]


def _build_render_data(
    result: Any,
    request_payload: Optional[Analyze3DRequest],
) -> Dict[str, Any]:
    rows = list(result.analysis_rows or [])
    columns = []
    fs_by_column: Dict[str, float] = {}
    morphology = {"method": "quantile_z", "confidence": 0.55, "crest_ids": [], "face_ids": [], "toe_ids": []}

    top_points: List[Dict[str, float]] = []
    if request_payload and request_payload.top_surface is not None:
        for point in request_payload.top_surface.points:
            top_points.append({"x": _safe_float(point.x), "y": _safe_float(point.y), "z": _safe_float(point.z)})

    if top_points:
        z_vals = [_safe_float(p["z"]) for p in top_points]
        crest_cut = _quantile(z_vals, 0.8)
        toe_cut = _quantile(z_vals, 0.2)
        for index, point in enumerate(top_points):
            if point["z"] >= crest_cut:
                morphology["crest_ids"].append(index)
            elif point["z"] <= toe_cut:
                morphology["toe_ids"].append(index)
            else:
                morphology["face_ids"].append(index)

    for row in rows:
        state = row.column_state
        phi = _safe_float(getattr(state, "friction_angle_rad", 0.0))
        cohesion = _safe_float(getattr(state, "cohesion", 0.0))
        eff_n = _safe_float(getattr(state, "effective_normal_stress", 0.0))
        weight = max(1e-9, _safe_float(getattr(state, "weight", 0.0)))
        dip = _safe_float(getattr(state, "base_dip_rad", 0.0))
        resist_proxy = cohesion + eff_n * math.tan(max(-1.3, min(1.3, phi)))
        drive_proxy = max(1e-6, weight * abs(math.sin(dip)))
        local_fs = max(0.0, min(5.0, resist_proxy / drive_proxy))
        fs_by_column[str(row.column_id)] = local_fs
        columns.append(
            {
                "column_id": int(row.column_id),
                "x_center": _safe_float(state.center_x),
                "y_center": _safe_float(state.center_y),
                "z_top": _safe_float(state.z_top),
                "z_base": _safe_float(state.z_bottom),
                "thickness": max(0.0, _safe_float(state.z_top) - _safe_float(state.z_bottom)),
                "is_active": True,
            }
        )

    fs_values = list(fs_by_column.values())
    fs_min = min(fs_values) if fs_values else None
    fs_max = max(fs_values) if fs_values else None

    return {
        "top_surface_points": top_points,
        "columns": columns,
        "fs_field": {
            "scalar_by_column_id": fs_by_column,
            "min": fs_min,
            "max": fs_max,
            "units": "proxy",
            "mapping_mode": "local_fs_proxy",
        },
        "morphology": morphology,
    }


def normalize_pipeline_result(
    result: Any,
    include_rows: bool,
    include_render_geometry: bool = True,
    request_payload: Optional[Analyze3DRequest] = None,
) -> Dict[str, Any]:
    method = result.method_result
    direction_results = []
    if method is not None:
        for d in method.direction_results:
            direction_results.append(
                {
                    "direction_rad": d.direction_rad,
                    "converged": d.converged,
                    "fs_value": d.fs_value,
                    "iterations": d.iterations,
                    "method_terms": d.method_terms,
                    "failure_reason": d.failure_reason,
                }
            )

    payload: Dict[str, Any] = {
        "column_count": result.column_count,
        "fs_min": None if method is None else method.fs_min,
        "critical_direction_rad": None if method is None else method.critical_direction_rad,
        "converged": False if method is None else method.converged,
        "method_id": None if method is None else int(method.method_id),
        "direction_results": direction_results,
        "diagnostics": {
            "pipeline": result.diagnostics,
            "method": {} if method is None else method.diagnostics,
        },
        "generated_files": result.generated_files,
    }
    if include_rows:
        payload["analysis_rows"] = [asdict(row) for row in result.analysis_rows]
    if include_render_geometry:
        payload["render_data"] = _build_render_data(result, request_payload=request_payload)
    return payload


def normalize_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, (ValueError, TypeError, ThreeDLEMError)):
        return _bad_request(str(exc))
    return HTTPException(status_code=500, detail={"code": "internal_3d_error", "message": str(exc)})

