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
profile_pipeline_stages = importlib.import_module(
    "3d_slope_stability.benchmarks.timers"
).profile_pipeline_stages
run_benchmark_matrix = importlib.import_module(
    "3d_slope_stability.benchmarks.matrix"
).run_benchmark_matrix


def _fixture_surface() -> SurfaceDataset:
    return SurfaceDataset(
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


def test_stage_level_timers_present() -> None:
    timings = profile_pipeline_stages(
        method_config=MethodRunConfig(
            method_id=1,
            solver=SolverConfig(max_iterations=80, tol_fs=1e-4, damping=1.0),
            direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
        ),
        grid_config=GridConfig(0, 2, 0, 2, 0, 20, 2, 2),
        slip_surface_config=SlipSurfaceConfig(
            mode="ellipsoid",
            ellipsoid_center=(1.0, 1.0, 9.0),
            ellipsoid_radii=(2.0, 2.0, 3.0),
        ),
        materials={"default": MaterialDefinition("default", 1, (30.0, 5.0), 18.0)},
        top_surface=_fixture_surface(),
    )
    for key in ("interpolation", "grid_assembly", "slip_intersection", "hydro_strength", "solver_core", "total"):
        assert key in timings
        assert timings[key] >= 0.0


def test_benchmark_matrix_deterministic_shape() -> None:
    rows = run_benchmark_matrix(
        top_surface=_fixture_surface(),
        materials={"default": MaterialDefinition("default", 1, (30.0, 5.0), 18.0)},
        seed=42,
    )
    # 3 grid sizes * 3 methods * 2 solver profiles
    assert len(rows) == 18
    required = {"grid_size", "method_id", "max_iterations", "tol_fs", "total"}
    for row in rows:
        assert required.issubset(set(row.keys()))

