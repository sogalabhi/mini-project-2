import importlib
import random

GridConfig = importlib.import_module("3d_slope_stability.config.schema").GridConfig
SlipSurfaceConfig = importlib.import_module("3d_slope_stability.config.schema").SlipSurfaceConfig
MethodRunConfig = importlib.import_module("3d_slope_stability.config.method_options").MethodRunConfig
SolverConfig = importlib.import_module("3d_slope_stability.config.method_options").SolverConfig
DirectionSearchConfig = importlib.import_module(
    "3d_slope_stability.config.method_options"
).DirectionSearchConfig
models = importlib.import_module("3d_slope_stability.domain.models")
DEMPoint = models.DEMPoint
SurfaceDataset = models.SurfaceDataset
MaterialDefinition = models.MaterialDefinition

build_direction_candidates = importlib.import_module(
    "3d_slope_stability.solvers.direction_search"
).build_direction_candidates
run_pipeline = importlib.import_module("3d_slope_stability.pipeline.runner").run_pipeline


def test_small_randomized_invariants() -> None:
    random.seed(7)
    for _ in range(5):
        h = 9.0 + random.random() * 3.0
        grid = GridConfig(x_min=0, x_max=2, y_min=0, y_max=2, z_min=0, z_max=20, col_x_max=2, col_y_max=2)
        slip = SlipSurfaceConfig(mode="ellipsoid", ellipsoid_center=(1.0, 1.0, h - 1.0), ellipsoid_radii=(2.0, 2.0, 3.0))
        top_surface = SurfaceDataset(
            label="tt",
            path="synthetic_top.csv",
            interpolation_mode="a1",
            points=(
                DEMPoint(0.0, 0.0, h),
                DEMPoint(2.0, 0.0, h),
                DEMPoint(0.0, 2.0, h - 0.5),
                DEMPoint(2.0, 2.0, h - 0.5),
            ),
        )
        materials = {"default": MaterialDefinition("default", 1, (30.0, 5.0), 18.0)}
        result = run_pipeline(
            method_config=MethodRunConfig(
                method_id=1,
                solver=SolverConfig(max_iterations=80, tol_fs=1e-4, damping=1.0),
                direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
            ),
            grid_config=grid,
            slip_surface_config=slip,
            materials=materials,
            top_surface=top_surface,
        )
        for row in result.analysis_rows:
            assert row.column_state.volume >= 0.0
            assert row.column_state.pore_pressure >= 0.0

        candidates = build_direction_candidates(1.0, DirectionSearchConfig(spacing_deg=1.0, tolerance_deg=5.0))
        assert len(candidates) >= 2

