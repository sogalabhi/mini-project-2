import importlib
import math

models = importlib.import_module("3d_slope_stability.domain.models")
MaterialDefinition = models.MaterialDefinition

hydro = importlib.import_module("3d_slope_stability.hydro")
pore_pressure_from_head = hydro.pore_pressure_from_head
hydro_state_from_levels = hydro.hydro_state_from_levels

strength_models = importlib.import_module("3d_slope_stability.strength.models")
mohr_coulomb_shear_strength = strength_models.mohr_coulomb_shear_strength
undrained_depth_cohesion = strength_models.undrained_depth_cohesion
undrained_datum_cohesion = strength_models.undrained_datum_cohesion
power_curve_shear_strength = strength_models.power_curve_shear_strength
user_curve_shear_strength = strength_models.user_curve_shear_strength

resolve_strength_state = importlib.import_module(
    "3d_slope_stability.strength.resolver"
).resolve_strength_state


def test_groundwater_pressure_radian_safe() -> None:
    pore = pore_pressure_from_head(
        water_level_z=10.0,
        base_level_z=8.0,
        water_unit_weight=9.81,
        base_dip_rad=math.radians(60),
    )
    assert pore > 0.0
    hs = hydro_state_from_levels(10.0, 8.0, 9.81, math.radians(30))
    assert hs.pore_pressure > 0.0
    assert hs.pressure_head > 0.0


def test_strength_model_branches() -> None:
    assert mohr_coulomb_shear_strength(100.0, math.radians(30), 10.0) > 10.0
    assert undrained_depth_cohesion(8.0, 10.0, 50.0, 2.0, 30.0, 80.0) >= 30.0
    assert undrained_datum_cohesion(8.0, 5.0, 40.0, 1.0, 20.0, 60.0) >= 20.0
    assert power_curve_shear_strength(100.0, 100.0, 0.7, 0.8) > 0.0
    assert user_curve_shear_strength(50.0, [(0.0, 10.0), (100.0, 30.0)]) == 20.0


def test_strength_resolver_mohr_and_unsat() -> None:
    mat = MaterialDefinition(
        name="m1",
        model_type=1,
        model_parameters=(30.0, 5.0),
        unit_weight=18.0,
    )
    state = resolve_strength_state(
        mat,
        z=8.0,
        z_top=10.0,
        effective_normal_stress=100.0,
        matric_suction=30.0,
        unsaturated_params=(12.0, 10.0, 25.0),
    )
    assert state.model_name == "mohr_coulomb"
    assert state.shear_strength > 0.0
    assert "unsat_increment" in state.diagnostics

