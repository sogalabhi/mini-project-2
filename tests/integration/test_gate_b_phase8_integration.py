import importlib
import math

models = importlib.import_module("3d_slope_stability.domain.models")
InterpolatedSurface = models.InterpolatedSurface
MaterialDefinition = models.MaterialDefinition
HydroState = models.HydroState
StrengthState = models.StrengthState
ColumnIntersectionState = models.ColumnIntersectionState
ColumnIntersectionSummary = models.ColumnIntersectionSummary

build_analysis_rows = importlib.import_module(
    "3d_slope_stability.analysis.analysis_rows"
).build_analysis_rows
validate_analysis_rows = importlib.import_module(
    "3d_slope_stability.analysis.analysis_rows"
).validate_analysis_rows

MethodRunConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).MethodRunConfig
SolverConfig = importlib.import_module("3d_slope_stability.config.method_options").SolverConfig
DirectionSearchConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).DirectionSearchConfig
run_hungr_bishop = importlib.import_module(
    "3d_slope_stability.solvers.hungr_bishop"
).run_hungr_bishop


def test_gate_b_hungr_bishop_integration_fixture() -> None:
    top_surface = InterpolatedSurface(
        label="tt",
        x_values=(0.0, 1.0, 2.0, 3.0),
        y_values=(0.0, 1.0, 2.0, 3.0),
        z_grid=(
            (10.0, 10.2, 10.4, 10.6),
            (9.8, 10.0, 10.2, 10.4),
            (9.6, 9.8, 10.0, 10.2),
            (9.4, 9.6, 9.8, 10.0),
        ),
    )
    intersections = ColumnIntersectionSummary(
        intersections=tuple(
            ColumnIntersectionState(col_id, ix, iy, True, 7.5, "valid")
            for col_id, (ix, iy) in enumerate(
                [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)],
                start=1,
            )
        ),
        valid_count=9,
        excluded_count=0,
        reasons={"valid": 9},
    )

    materials = {"default": MaterialDefinition("default", 1, (30.0, 6.0), 18.0)}
    hydro = {cid: HydroState(pressure_head=1.0, pore_pressure=8.0) for cid in range(1, 10)}
    strength = {
        cid: StrengthState(
            friction_angle_rad=math.radians(30.0),
            cohesion=6.0,
            shear_strength=24.0,
            model_name="mohr_coulomb",
            diagnostics={},
        )
        for cid in range(1, 10)
    }

    rows = build_analysis_rows(top_surface, intersections, materials, hydro, strength)
    validate_analysis_rows(rows)
    rows = [
        models.AnalysisRow(
            column_id=row.column_id,
            x=row.x,
            y=row.y,
            column_state=models.ColumnState(
                **{
                    **row.column_state.__dict__,
                    "base_dip_rad": math.radians(24.0),
                    "base_dip_direction_rad": math.radians(180.0),
                }
            ),
        )
        for row in rows
    ]

    config = MethodRunConfig(
        method_id=1,
        solver=SolverConfig(max_iterations=150, tol_fs=1e-4, damping=1.0),
        direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=6.0),
    )
    result = run_hungr_bishop(rows, config)

    assert result.converged is True
    assert result.fs_min is not None
    assert result.fs_min > 0.0
    assert result.critical_direction_rad is not None
    assert len(result.direction_results) >= 5
    converged_count = sum(1 for d in result.direction_results if d.converged)
    assert converged_count >= 1

