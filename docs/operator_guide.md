# Operator Guide: Inputs, Outputs, and Runbook

## Input Format Spec

## Surface CSV (`x,y,z`)

- Required columns: at least 3 numeric values per row (`x`, `y`, `z`).
- Empty rows are ignored.
- File must exist and contain numeric rows.

Used by:

- `io/csv_reader.py::read_xyz_csv`
- `io/parsers.py::parse_surface_inputs`

## Curve CSV (`x,y`)

- For user-defined shear-normal curves.
- Required: at least 2 numeric values per row.

## Runtime Config Objects

- `GridConfig`
  - bounds (`x_min..z_max`) + column counts.
- `SlipSurfaceConfig`
  - mode: `ellipsoid` or `user_defined`.
- `MethodRunConfig`
  - method id, solver limits, direction search options.
- Material definitions:
  - `name`, `model_type`, `model_parameters`, `unit_weight`.

## Output Schema

Main result object: `PipelineResult`

- `column_count`
- `analysis_rows` (canonical rows)
- `method_result`
  - `fs_min`
  - `critical_direction_rad`
  - `direction_results`
  - `diagnostics`
- `generated_files`
- `diagnostics` (preprocess summary)

## Run Examples

## Python API

```python
import importlib

pipeline = importlib.import_module("3d_slope_stability.pipeline")
schema = importlib.import_module("3d_slope_stability.config.schema")
method_options = importlib.import_module("3d_slope_stability.config.method_options")
models = importlib.import_module("3d_slope_stability.domain.models")

result = pipeline.run_pipeline(
    method_config=method_options.MethodRunConfig(
        method_id=1,
        solver=method_options.SolverConfig(max_iterations=100, tol_fs=1e-4, damping=1.0),
        direction=method_options.DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
    ),
    grid_config=schema.GridConfig(0, 2, 0, 2, 0, 20, 2, 2),
    slip_surface_config=schema.SlipSurfaceConfig(
        mode="ellipsoid",
        ellipsoid_center=(1.0, 1.0, 9.0),
        ellipsoid_radii=(2.0, 2.0, 3.0),
    ),
    materials={"default": models.MaterialDefinition("default", 1, (30.0, 5.0), 18.0)},
    top_surface=models.SurfaceDataset(
        label="tt",
        path="synthetic_top.csv",
        interpolation_mode="a1",
        points=(
            models.DEMPoint(0, 0, 10),
            models.DEMPoint(2, 0, 10),
            models.DEMPoint(0, 2, 9.5),
            models.DEMPoint(2, 2, 9.5),
        ),
    ),
)
print(result.method_result.fs_min)
```

## CLI

- `python -m 3d_slope_stability.pipeline.cli --config /path/to/config.json`

The JSON includes `grid`, `slip_surface`, `method`, `materials`, and optional
surface lists/exports.

## Troubleshooting

- **Missing file errors**
  - Verify path exists and is readable.
- **Unsupported interpolation mode**
  - Use one of: `a1`, `b1..b6`, `c1..c6`.
- **No valid columns after intersection**
  - Check slip-surface parameters versus terrain elevation.
- **Non-convergence**
  - Increase `max_iterations`, relax `tol_fs`, or adjust direction window.
- **Unexpected low FS**
  - Validate material parameters and pore-pressure assumptions.

