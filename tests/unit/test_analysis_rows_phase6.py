import importlib
import math

models = importlib.import_module("3d_slope_stability.domain.models")
InterpolatedSurface = models.InterpolatedSurface
MaterialDefinition = models.MaterialDefinition
HydroState = models.HydroState
StrengthState = models.StrengthState
ColumnIntersectionState = models.ColumnIntersectionState
ColumnIntersectionSummary = models.ColumnIntersectionSummary

analysis_rows = importlib.import_module("3d_slope_stability.analysis.analysis_rows")
build_analysis_rows = analysis_rows.build_analysis_rows
validate_analysis_rows = analysis_rows.validate_analysis_rows
build_legacy_comparison_rows = analysis_rows.build_legacy_comparison_rows


def test_build_and_validate_analysis_rows() -> None:
    top_surface = InterpolatedSurface(
        label="tt",
        x_values=(0.0, 1.0, 2.0),
        y_values=(0.0, 1.0, 2.0),
        z_grid=((10.0, 10.0, 10.0), (10.0, 10.0, 10.0), (10.0, 10.0, 10.0)),
    )
    summary = ColumnIntersectionSummary(
        intersections=(
            ColumnIntersectionState(1, 0, 0, True, 8.0, "valid"),
            ColumnIntersectionState(2, 1, 1, False, None, "outside_slip_surface"),
        ),
        valid_count=1,
        excluded_count=1,
        reasons={"valid": 1, "outside_slip_surface": 1},
    )
    materials = {"default": MaterialDefinition("default", 1, (30.0, 5.0), 18.0)}
    hydro = {1: HydroState(pressure_head=1.0, pore_pressure=9.81)}
    strength = {
        1: StrengthState(
            friction_angle_rad=math.radians(30.0),
            cohesion=5.0,
            shear_strength=20.0,
            model_name="mohr_coulomb",
            diagnostics={},
        )
    }

    rows = build_analysis_rows(top_surface, summary, materials, hydro, strength)
    assert len(rows) == 1
    validate_analysis_rows(rows)
    legacy = build_legacy_comparison_rows(rows)
    assert len(legacy) == 1
    assert "effective_normal_stress" in legacy[0]

