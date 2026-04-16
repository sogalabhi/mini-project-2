# API Freeze Contract (v0.1.0)

## Purpose

This document freezes the public interfaces and schemas for release candidate
`v0.1.0-rc1` of the rewritten 3D LEM backend.

## Public Python Interfaces (Frozen)

From `3d_slope_stability`:

- `run_pipeline`
- `run_method`
- `build_columns`
- `RuntimeSettings`
- `DEMPoint`
- `ColumnState`
- `AnalysisRow`
- `DirectionResult`
- `MethodComputationResult`
- `PipelineResult`

From `3d_slope_stability.pipeline`:

- `run_pipeline`
- `run_method`
- `build_columns`

## Frozen Method IDs

- `1`: Hungr-Bishop
- `2`: Hungr-Janbu simplified
- `3`: Hungr-Janbu corrected
- `4`: Cheng-Yip Bishop-like
- `5`: Cheng-Yip Janbu-like simplified
- `6`: Cheng-Yip Janbu-like corrected
- `7`: Cheng-Yip Spencer-like

## Frozen Schemas

- `SolverConfig(max_iterations, tol_fs, damping)`
- `DirectionSearchConfig(spacing_deg, tolerance_deg, user_direction_deg=None)`
- `MethodRunConfig(method_id, solver, direction, use_side_resistance=True)`
- `GridConfig(x_min, x_max, y_min, y_max, z_min, z_max, col_x_max, col_y_max)`
- `InterpolationConfig(mode, std_max)`
- `SlipSurfaceConfig(mode, ellipsoid_center, ellipsoid_radii, user_defined_surface_path, user_defined_interpolation)`

Frozen mode values:

- Interpolation: `a1`, `b1`, `b2`, `b3`, `b4`, `b5`, `b6`, `c1`, `c2`, `c3`, `c4`, `c5`, `c6`
- Slip surface: `ellipsoid`, `user_defined`

## Stability Guarantees

- Import-safe package behavior (no import-time runtime side effects).
- Deterministic behavior for identical inputs and options.
- Explicit validation at boundaries and structured diagnostics in solver outputs.

## Not Covered by Freeze

- Internal private helper APIs.
- Exact floating-point parity with the legacy monolithic implementation.

