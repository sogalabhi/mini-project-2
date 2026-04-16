import json
from pathlib import Path
import importlib

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

run_pipeline = importlib.import_module("3d_slope_stability.pipeline.runner").run_pipeline


def test_regression_against_phase10_baseline_ranges() -> None:
    baseline_path = Path("tests/fixtures/phase10_baseline.json")
    baseline = json.loads(baseline_path.read_text())
    grid = GridConfig(x_min=0, x_max=2, y_min=0, y_max=2, z_min=0, z_max=20, col_x_max=2, col_y_max=2)
    slip = SlipSurfaceConfig(mode="ellipsoid", ellipsoid_center=(1.0, 1.0, 9.0), ellipsoid_radii=(2.0, 2.0, 3.0))
    top_surface = SurfaceDataset(
        label="tt",
        path="synthetic_top.csv",
        interpolation_mode="a1",
        points=(
            DEMPoint(0.0, 0.0, 10.0),
            DEMPoint(2.0, 0.0, 10.0),
            DEMPoint(0.0, 2.0, 9.5),
            DEMPoint(2.0, 2.0, 9.5),
        ),
    )
    materials = {"default": MaterialDefinition("default", 1, (30.0, 5.0), 18.0)}

    for method_id, rng in baseline["fs_ranges"].items():
        result = run_pipeline(
            method_config=MethodRunConfig(
                method_id=int(method_id),
                solver=SolverConfig(max_iterations=120, tol_fs=1e-4, damping=1.0),
                direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
            ),
            grid_config=grid,
            slip_surface_config=slip,
            materials=materials,
            top_surface=top_surface,
        )
        fs = result.method_result.fs_min
        assert fs is not None
        assert float(rng["min"]) <= fs <= float(rng["max"])

