import importlib
import math

MethodRunConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).MethodRunConfig
SolverConfig = importlib.import_module("3d_slope_stability.config.method_options").SolverConfig
DirectionSearchConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).DirectionSearchConfig
ReinforcementConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).ReinforcementConfig
models = importlib.import_module("3d_slope_stability.domain.models")
AnalysisRow = models.AnalysisRow
ColumnState = models.ColumnState
run_cheng_yip = importlib.import_module("3d_slope_stability.solvers.cheng_yip").run_cheng_yip
update_lambda_bidirectional = importlib.import_module(
    "3d_slope_stability.solvers.lambda_update"
).update_lambda_bidirectional


def _row(column_id: int, cohesion: float = 8.0, dip_deg: float = 24.0, dip_dir_deg: float = 180.0) -> AnalysisRow:
    s = ColumnState(
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
    return AnalysisRow(column_id=column_id, x=s.center_x, y=s.center_y, column_state=s)


def test_lambda_update_bidirectional_and_safeguards() -> None:
    # Initial positive mismatch should reduce lambda.
    out1 = update_lambda_bidirectional(
        current_lambda=0.0,
        mismatch=0.2,
        prev_mismatch=None,
        prev_sign=None,
        step=0.2,
    )
    assert out1.lambda_value < 0.0

    # Sign flip triggers oscillation handling and step reduction.
    out2 = update_lambda_bidirectional(
        current_lambda=out1.lambda_value,
        mismatch=-0.1,
        prev_mismatch=0.2,
        prev_sign=1,
        step=out1.step,
    )
    assert out2.step <= out1.step


def test_cheng_yip_variants_converge_and_emit_diagnostics() -> None:
    rows = [_row(1), _row(2), _row(3), _row(4)]
    base_solver = SolverConfig(max_iterations=150, tol_fs=1e-4, damping=1.0)
    direction = DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0)

    for method_id in (4, 5, 6, 7):
        cfg = MethodRunConfig(method_id=method_id, solver=base_solver, direction=direction)
        result = run_cheng_yip(rows, cfg)
        assert result.converged is True
        assert result.fs_min is not None and result.fs_min > 0.0
        assert result.critical_direction_rad is not None
        assert len(result.direction_results) >= 3
        assert "variant" in result.diagnostics
        assert "max_mismatch_abs" in result.diagnostics


def test_cheng_yip_corrected_janbu_not_lower_than_simplified() -> None:
    rows = [_row(1, cohesion=6.0), _row(2, cohesion=6.0), _row(3, cohesion=6.0)]
    solver = SolverConfig(max_iterations=150, tol_fs=1e-4, damping=1.0)
    direction = DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=2.0)

    simple = run_cheng_yip(rows, MethodRunConfig(method_id=5, solver=solver, direction=direction))
    corrected = run_cheng_yip(rows, MethodRunConfig(method_id=6, solver=solver, direction=direction))

    assert simple.fs_min is not None and corrected.fs_min is not None
    assert corrected.fs_min >= simple.fs_min


def test_cheng_yip_reinforcement_increases_fs() -> None:
    rows = [_row(1, cohesion=6.0), _row(2, cohesion=6.0), _row(3, cohesion=6.0)]
    solver = SolverConfig(max_iterations=150, tol_fs=1e-4, damping=1.0)
    direction = DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=0.0)
    off = run_cheng_yip(
        rows,
        MethodRunConfig(
            method_id=4,
            solver=solver,
            direction=direction,
            reinforcement=ReinforcementConfig(enabled=False),
        ),
    )
    on = run_cheng_yip(
        rows,
        MethodRunConfig(
            method_id=4,
            solver=solver,
            direction=direction,
            reinforcement=ReinforcementConfig(
                enabled=True, steel_area=4e-4, yield_strength=200000.0, spacing_x=2.0, spacing_y=2.0
            ),
        ),
    )
    assert off.fs_min is not None and on.fs_min is not None
    assert on.fs_min >= off.fs_min

