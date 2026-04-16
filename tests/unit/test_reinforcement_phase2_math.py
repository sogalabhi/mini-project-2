import importlib
import math

models = importlib.import_module("3d_slope_stability.domain.models")
AnalysisRow = models.AnalysisRow
ColumnState = models.ColumnState
ReinforcementConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).ReinforcementConfig
reinforcement_mod = importlib.import_module("3d_slope_stability.strength.reinforcement")
compute_reinforcement_contribution = reinforcement_mod.compute_reinforcement_contribution


def _row(column_id: int, base_area: float = 1.0) -> AnalysisRow:
    state = ColumnState(
        column_id=column_id,
        center_x=float(column_id),
        center_y=float(column_id),
        z_top=10.0,
        z_bottom=8.0,
        base_area=base_area,
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
    )
    return AnalysisRow(column_id=column_id, x=state.center_x, y=state.center_y, column_state=state)


def test_reinforcement_formula_and_per_column_area_scaling() -> None:
    rows = [_row(1, 1.0), _row(2, 2.0)]
    cfg = ReinforcementConfig(
        enabled=True,
        diameter=0.025,
        length_embed=6.0,
        spacing_x=2.0,
        spacing_y=2.0,
        steel_area=5e-4,
        yield_strength=200000.0,
        bond_strength=150.0,
    )
    out = compute_reinforcement_contribution(rows, cfg)
    expected_t_y = cfg.steel_area * cfg.yield_strength
    expected_t_bond = math.pi * cfg.diameter * cfg.length_embed * cfg.bond_strength
    expected_t_max = min(expected_t_y, expected_t_bond)
    expected_q = expected_t_max / (cfg.spacing_x * cfg.spacing_y)
    assert out.tensile_capacity == expected_t_y
    assert math.isclose(out.bond_capacity, expected_t_bond, rel_tol=1e-9)
    assert out.t_max == expected_t_max
    assert out.q_nail == expected_q
    assert math.isclose(out.per_column[2], 2.0 * out.per_column[1], rel_tol=1e-9)


def test_yield_controlled_branch_and_bond_controlled_branch() -> None:
    rows = [_row(1)]
    yield_controlled = ReinforcementConfig(
        enabled=True,
        diameter=0.025,
        length_embed=6.0,
        spacing_x=2.0,
        spacing_y=2.0,
        steel_area=5e-4,
        yield_strength=1000.0,
        bond_strength=150.0,
    )
    bond_controlled = ReinforcementConfig(
        enabled=True,
        diameter=0.025,
        length_embed=1.0,
        spacing_x=2.0,
        spacing_y=2.0,
        steel_area=5e-3,
        yield_strength=2_000_000.0,
        bond_strength=1.0,
    )
    out_y = compute_reinforcement_contribution(rows, yield_controlled)
    out_b = compute_reinforcement_contribution(rows, bond_controlled)
    assert out_y.t_max == out_y.tensile_capacity
    assert out_b.t_max == out_b.bond_capacity


def test_invalid_spacing_rejected_in_config() -> None:
    try:
        ReinforcementConfig(enabled=True, spacing_x=0.0)
        assert False, "Expected ValueError for spacing_x <= 0"
    except ValueError:
        pass

