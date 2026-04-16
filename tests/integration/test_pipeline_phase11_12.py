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


def _top_surface() -> SurfaceDataset:
    pts = (
        DEMPoint(0.0, 0.0, 10.0),
        DEMPoint(2.0, 0.0, 10.0),
        DEMPoint(0.0, 2.0, 9.5),
        DEMPoint(2.0, 2.0, 9.5),
    )
    return SurfaceDataset(label="tt", path="synthetic_top.csv", points=pts, interpolation_mode="a1")


def _base_args():
    grid = GridConfig(x_min=0, x_max=2, y_min=0, y_max=2, z_min=0, z_max=20, col_x_max=2, col_y_max=2)
    slip = SlipSurfaceConfig(mode="ellipsoid", ellipsoid_center=(1.0, 1.0, 9.0), ellipsoid_radii=(2.0, 2.0, 3.0))
    materials = {"default": MaterialDefinition("default", 1, (30.0, 5.0), 18.0)}
    return grid, slip, materials


def test_full_preprocess_chain_to_rows_and_method() -> None:
    grid, slip, materials = _base_args()
    result = run_pipeline(
        method_config=MethodRunConfig(
            method_id=1,
            solver=SolverConfig(max_iterations=100, tol_fs=1e-4, damping=1.0),
            direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
        ),
        grid_config=grid,
        slip_surface_config=slip,
        materials=materials,
        top_surface=_top_surface(),
    )
    assert result.column_count > 0
    assert result.method_result is not None
    assert result.method_result.fs_min is not None


def test_full_solver_chain_for_each_method_family() -> None:
    grid, slip, materials = _base_args()
    for method_id in (1, 2, 3, 4, 5, 6, 7):
        result = run_pipeline(
            method_config=MethodRunConfig(
                method_id=method_id,
                solver=SolverConfig(max_iterations=120, tol_fs=1e-4, damping=1.0),
                direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
            ),
            grid_config=grid,
            slip_surface_config=slip,
            materials=materials,
            top_surface=_top_surface(),
        )
        assert result.method_result is not None
        assert result.method_result.fs_min is None or result.method_result.fs_min > 0.0

