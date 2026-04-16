import importlib

GridConfig = importlib.import_module("3d_slope_stability.config.schema").GridConfig
SlipSurfaceConfig = importlib.import_module("3d_slope_stability.config.schema").SlipSurfaceConfig
models = importlib.import_module("3d_slope_stability.domain.models")
DEMPoint = models.DEMPoint
SurfaceDataset = models.SurfaceDataset
InterpolatedSurface = models.InterpolatedSurface
build_grid_axes = importlib.import_module("3d_slope_stability.geometry.grid").build_grid_axes
surfaces = importlib.import_module("3d_slope_stability.geometry.surfaces")
sample_slip_surface = surfaces.sample_slip_surface
intersect_columns_with_slip_surface = surfaces.intersect_columns_with_slip_surface


def test_ellipsoid_sampling_and_mask() -> None:
    cfg = GridConfig(0, 10, 0, 10, 0, 20, 4, 4)
    axes = build_grid_axes(cfg)
    slip_cfg = SlipSurfaceConfig(
        mode="ellipsoid",
        ellipsoid_center=(5.0, 5.0, 12.0),
        ellipsoid_radii=(8.0, 8.0, 6.0),
    )
    sample = sample_slip_surface(slip_cfg, axes)
    assert len(sample.surface.z_grid) == len(axes.x_edges)
    assert len(sample.surface.z_grid[0]) == len(axes.y_edges)
    valid_count = sum(1 for row in sample.valid_mask for v in row if v)
    assert valid_count > 0


def test_column_intersection_summary_counts() -> None:
    z_top = tuple(tuple(20.0 for _ in range(5)) for _ in range(5))
    z_slip = tuple(tuple(10.0 for _ in range(5)) for _ in range(5))
    mask = tuple(tuple(True for _ in range(5)) for _ in range(5))
    top = InterpolatedSurface("tt", (0, 1, 2, 3, 4), (0, 1, 2, 3, 4), z_top)
    slip = models.SlipSurfaceSample(
        surface=InterpolatedSurface("ss", (0, 1, 2, 3, 4), (0, 1, 2, 3, 4), z_slip),
        valid_mask=mask,
    )
    summary = intersect_columns_with_slip_surface(top, slip, z_min=0.0)
    assert summary.valid_count == 16
    assert summary.excluded_count == 0
    assert summary.reasons["valid"] == 16


def test_user_defined_surface_mode() -> None:
    cfg = GridConfig(0, 2, 0, 2, 0, 10, 2, 2)
    axes = build_grid_axes(cfg)
    user_surface = SurfaceDataset(
        label="ss",
        path="synthetic.csv",
        interpolation_mode="a1",
        points=(
            DEMPoint(0.0, 0.0, 3.0),
            DEMPoint(2.0, 0.0, 3.0),
            DEMPoint(0.0, 2.0, 3.0),
            DEMPoint(2.0, 2.0, 3.0),
        ),
    )
    slip_cfg = SlipSurfaceConfig(mode="user_defined", user_defined_surface_path="synthetic.csv")
    sample = sample_slip_surface(slip_cfg, axes, user_surface=user_surface)
    assert all(all(v for v in row) for row in sample.valid_mask)

