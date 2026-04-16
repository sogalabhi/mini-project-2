import importlib
import math
import pytest

GridConfig = importlib.import_module("3d_slope_stability.config.schema").GridConfig
SlipSurfaceConfig = importlib.import_module("3d_slope_stability.config.schema").SlipSurfaceConfig
MethodRunConfig = importlib.import_module("3d_slope_stability.config.method_options").MethodRunConfig
SolverConfig = importlib.import_module("3d_slope_stability.config.method_options").SolverConfig
DirectionSearchConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).DirectionSearchConfig
InputValidationError = importlib.import_module("3d_slope_stability.domain.errors").InputValidationError
parse_surface_inputs = importlib.import_module("3d_slope_stability.io.parsers").parse_surface_inputs
models = importlib.import_module("3d_slope_stability.domain.models")
MaterialDefinition = models.MaterialDefinition
AnalysisRow = models.AnalysisRow
ColumnState = models.ColumnState
resolve_strength_state = importlib.import_module("3d_slope_stability.strength.resolver").resolve_strength_state
run_cheng_yip = importlib.import_module("3d_slope_stability.solvers.cheng_yip").run_cheng_yip


def test_missing_dem_file_raises() -> None:
    with pytest.raises(InputValidationError):
        parse_surface_inputs(
            names=["does_not_exist.csv"],
            types=["tt"],
            interpolation_modes=["a1"],
        )


def test_invalid_interpolation_mode_raises() -> None:
    with pytest.raises(ValueError):
        parse_surface_inputs(
            names=["does_not_exist.csv"],
            types=["tt"],
            interpolation_modes=["z9"],
        )


def test_invalid_material_params_raises() -> None:
    bad_material = MaterialDefinition(name="bad", model_type=1, model_parameters=(30.0,), unit_weight=18.0)
    with pytest.raises(InputValidationError):
        resolve_strength_state(
            bad_material,
            z=8.0,
            z_top=10.0,
            effective_normal_stress=100.0,
        )


def test_non_convergence_handling() -> None:
    row = AnalysisRow(
        column_id=1,
        x=0.0,
        y=0.0,
        column_state=ColumnState(
            column_id=1,
            center_x=0.0,
            center_y=0.0,
            z_top=10.0,
            z_bottom=8.0,
            base_area=1.0,
            side_areas=(1.0, 1.0, 1.0, 1.0),
            volume=2.0,
            weight=36.0,
            base_dip_rad=math.radians(24.0),
            base_dip_direction_rad=math.radians(180.0),
            pore_pressure=5.0,
            effective_normal_stress=30.0,
            cohesion=8.0,
            friction_angle_rad=math.radians(28.0),
            shear_model_type=1,
            material_name="m1",
            diagnostics={},
        ),
    )
    cfg = MethodRunConfig(
        method_id=7,
        solver=SolverConfig(max_iterations=1, tol_fs=1e-12, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=0.0),
    )
    result = run_cheng_yip([row], cfg)
    assert result.converged is False
    assert result.fs_min is None

