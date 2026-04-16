import importlib
import math

DirectionSearchConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).DirectionSearchConfig
MethodId = importlib.import_module("3d_slope_stability.domain.enums").MethodId
models = importlib.import_module("3d_slope_stability.domain.models")
ColumnState = models.ColumnState
AnalysisRow = models.AnalysisRow
DirectionResult = models.DirectionResult

common = importlib.import_module("3d_slope_stability.solvers.common")
direction_search = importlib.import_module("3d_slope_stability.solvers.direction_search")
results_mod = importlib.import_module("3d_slope_stability.solvers.results")


def test_common_solver_utilities() -> None:
    assert common.safe_divide(10.0, 2.0) == 5.0
    assert common.safe_divide(10.0, 0.0, default=-1.0) == -1.0
    assert common.clip_value(5.0, 0.0, 3.0) == 3.0
    assert common.has_converged(1.0001, 1.0002, 0.001)
    x, y = common.decompose_force_2d(10.0, math.pi / 2.0)
    assert round(x, 6) == 0.0
    assert round(y, 6) == 10.0


def test_direction_search_engine() -> None:
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
            base_dip_rad=0.1,
            base_dip_direction_rad=math.pi / 2.0,
            pore_pressure=0.0,
            effective_normal_stress=30.0,
            cohesion=5.0,
            friction_angle_rad=0.5,
            shear_model_type=1,
            material_name="m1",
            diagnostics={},
        ),
    )
    init = direction_search.estimate_initial_direction([row])
    cfg = DirectionSearchConfig(spacing_deg=1.0, tolerance_deg=2.0)
    cands = direction_search.build_direction_candidates(init, cfg)
    assert len(cands) >= 3


def test_result_aggregation() -> None:
    packed = results_mod.aggregate_method_result(
        MethodId.HUNGR_BISHOP,
        [
            DirectionResult(0.0, True, 1.5, 10, {}, None),
            DirectionResult(1.0, True, 1.2, 12, {}, None),
            DirectionResult(2.0, False, None, 200, {}, "non_converged"),
        ],
    )
    assert packed.converged is True
    assert packed.fs_min == 1.2

