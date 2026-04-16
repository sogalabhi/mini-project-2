import importlib

GridConfig = importlib.import_module("3d_slope_stability.config.schema").GridConfig
models = importlib.import_module("3d_slope_stability.domain.models")
DEMPoint = models.DEMPoint
SurfaceDataset = models.SurfaceDataset
build_grid_axes = importlib.import_module("3d_slope_stability.geometry.grid").build_grid_axes
interpolate_surface_to_grid = importlib.import_module(
    "3d_slope_stability.geometry.interpolation"
).interpolate_surface_to_grid
primitives = importlib.import_module("3d_slope_stability.geometry.primitives")
area_3d_polygon = primitives.area_3d_polygon
tetra_volume = primitives.tetra_volume


def test_build_grid_axes_is_deterministic() -> None:
    config = GridConfig(
        x_min=0.0,
        x_max=10.0,
        y_min=0.0,
        y_max=10.0,
        z_min=0.0,
        z_max=5.0,
        col_x_max=5,
        col_y_max=5,
    )
    axes = build_grid_axes(config)
    assert axes.x_edges[0] == 0.0
    assert axes.x_edges[-1] == 10.0
    assert len(axes.x_centers) == 5
    assert axes.x_centers[0] == 1.0


def test_interpolation_returns_expected_grid_shape() -> None:
    surface = SurfaceDataset(
        label="tt",
        path="synthetic.csv",
        interpolation_mode="a1",
        points=(
            DEMPoint(0.0, 0.0, 0.0),
            DEMPoint(10.0, 0.0, 10.0),
            DEMPoint(0.0, 10.0, 10.0),
            DEMPoint(10.0, 10.0, 20.0),
        ),
    )
    out = interpolate_surface_to_grid(surface, (0.0, 5.0, 10.0), (0.0, 5.0, 10.0))
    assert len(out.z_grid) == 3
    assert len(out.z_grid[0]) == 3
    assert out.z_grid[0][0] == 0.0


def test_primitives_basic_geometry() -> None:
    area = area_3d_polygon(
        (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (0.0, 1.0, 0.0),
        )
    )
    assert round(area, 6) == 1.0

    vol = tetra_volume(
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    )
    assert round(vol, 6) == round(1.0 / 6.0, 6)

