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
run_hungr_bishop = importlib.import_module(
    "3d_slope_stability.solvers.hungr_bishop"
).run_hungr_bishop


def _row(column_id: int, cohesion: float, dip_deg: float = 25.0, dip_dir_deg: float = 180.0) -> AnalysisRow:
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


def test_hungr_bishop_converges_on_deterministic_fixture() -> None:
    rows = [_row(1, 8.0), _row(2, 8.0), _row(3, 8.0)]
    config = MethodRunConfig(
        method_id=1,
        solver=SolverConfig(max_iterations=100, tol_fs=1e-4, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
    )
    result = run_hungr_bishop(rows, config)
    assert result.converged is True
    assert result.fs_min is not None
    assert result.fs_min > 0.0
    assert len(result.direction_results) >= 3


def test_hungr_bishop_trend_higher_cohesion_higher_fs() -> None:
    low_rows = [_row(1, 2.0), _row(2, 2.0), _row(3, 2.0)]
    high_rows = [_row(1, 12.0), _row(2, 12.0), _row(3, 12.0)]
    config = MethodRunConfig(
        method_id=1,
        solver=SolverConfig(max_iterations=100, tol_fs=1e-4, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=0.0),
    )
    low = run_hungr_bishop(low_rows, config)
    high = run_hungr_bishop(high_rows, config)
    assert low.fs_min is not None and high.fs_min is not None
    assert high.fs_min > low.fs_min

