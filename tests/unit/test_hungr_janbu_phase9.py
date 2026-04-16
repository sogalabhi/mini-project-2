import importlib
import math

MethodRunConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).MethodRunConfig
SolverConfig = importlib.import_module("3d_slope_stability.config.method_options").SolverConfig
DirectionSearchConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).DirectionSearchConfig
models = importlib.import_module("3d_slope_stability.domain.models")
AnalysisRow = models.AnalysisRow
ColumnState = models.ColumnState

janbu = importlib.import_module("3d_slope_stability.solvers.hungr_janbu")
run_hungr_janbu_simplified = janbu.run_hungr_janbu_simplified
run_hungr_janbu_corrected = janbu.run_hungr_janbu_corrected


def _row(column_id: int, cohesion: float, dip_deg: float = 24.0, dip_dir_deg: float = 180.0) -> AnalysisRow:
    state = ColumnState(
        column_id=column_id,
        center_x=float(column_id),
        center_y=float(column_id),
        z_top=10.0,
        z_bottom=8.0,
        base_area=1.0,
        side_areas=(1.0, 1.0, 1.0, 1.0),
        volume=2.0,
        weight=36.0,
        base_dip_rad=math.radians(dip_deg),
        base_dip_direction_rad=math.radians(dip_dir_deg),
        pore_pressure=5.0,
        effective_normal_stress=30.0,
        cohesion=cohesion,
        friction_angle_rad=math.radians(28.0),
        shear_model_type=1,
        material_name="m1",
        diagnostics={},
    )
    return AnalysisRow(column_id=column_id, x=state.center_x, y=state.center_y, column_state=state)


def test_janbu_simplified_converges() -> None:
    rows = [_row(1, 6.0), _row(2, 6.0), _row(3, 6.0)]
    cfg = MethodRunConfig(
        method_id=2,
        solver=SolverConfig(max_iterations=100, tol_fs=1e-4, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
    )
    result = run_hungr_janbu_simplified(rows, cfg)
    assert result.converged is True
    assert result.fs_min is not None
    assert result.fs_min > 0.0
    assert len(result.direction_results) >= 3


def test_janbu_corrected_converges_and_is_not_lower_than_simplified() -> None:
    rows = [_row(1, 6.0), _row(2, 6.0), _row(3, 6.0)]
    cfg_simple = MethodRunConfig(
        method_id=2,
        solver=SolverConfig(max_iterations=100, tol_fs=1e-4, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=2.0),
    )
    cfg_corrected = MethodRunConfig(
        method_id=3,
        solver=SolverConfig(max_iterations=100, tol_fs=1e-4, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=2.0),
    )
    simple = run_hungr_janbu_simplified(rows, cfg_simple)
    corrected = run_hungr_janbu_corrected(rows, cfg_corrected)
    assert corrected.converged is True
    assert simple.fs_min is not None and corrected.fs_min is not None
    assert corrected.fs_min >= simple.fs_min


def test_janbu_interface_matches_bishop_style_result_shape() -> None:
    rows = [_row(1, 8.0), _row(2, 8.0)]
    cfg = MethodRunConfig(
        method_id=2,
        solver=SolverConfig(max_iterations=80, tol_fs=1e-4, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=1.0, tolerance_deg=0.0),
    )
    result = run_hungr_janbu_simplified(rows, cfg)
    # Shared MethodComputationResult interface checks
    assert hasattr(result, "method_id")
    assert hasattr(result, "fs_min")
    assert hasattr(result, "critical_direction_rad")
    assert hasattr(result, "direction_results")
    assert isinstance(result.direction_results, list)

