# Migration Notes: Legacy to Rewritten 3D LEM

## Purpose

This document maps legacy concepts from `3D_backend_analysis.py` to the rewritten
`3d_slope_stability` package.

## Method ID Mapping

- Legacy `1` -> new `1`: Hungr-Bishop
- Legacy `2` -> new `2`: Hungr-Janbu simplified
- Legacy `3` -> new `3`: Hungr-Janbu corrected
- Legacy `4` -> new `4`: Cheng-Yip Bishop-like
- Legacy `5` -> new `5`: Cheng-Yip Janbu-like simplified
- Legacy `6` -> new `6`: Cheng-Yip Janbu-like corrected
- Legacy `7` -> new `7`: Cheng-Yip Spencer-like

## Key Output Mapping

- Legacy final minimum FS -> `PipelineResult.method_result.fs_min`
- Legacy critical direction -> `PipelineResult.method_result.critical_direction_rad`
- Legacy per-direction traces -> `PipelineResult.method_result.direction_results`
- Legacy intermediate table rows -> `PipelineResult.analysis_rows`

## Legacy Function Responsibility Mapping

- Legacy DEM ingestion/interpolation blocks ->
  - `io/csv_reader.py`
  - `io/parsers.py`
  - `geometry/interpolation.py`
- Legacy geometry/grid slicing ->
  - `geometry/grid.py`
  - `geometry/surfaces.py`
- Legacy hydro/strength inline blocks ->
  - `hydro/`
  - `strength/`
- Legacy method switch-case logic ->
  - `pipeline/dispatcher.py`
  - `solvers/*.py`

## Behavioral Differences to Expect

- Input validation is stricter and fails early with explicit exceptions.
- All method outputs carry structured diagnostics.
- Deterministic processing replaces implicit mutable global-style flow.
- Some advanced method internals are stabilized approximations and may not produce
  bit-for-bit legacy values.

## Acceptance Guidance

- Compare trends, stability, and bounded ranges, not exact floating-point parity.
- For critical projects, lock benchmark fixtures and tolerance envelopes.
- Prefer canonical named fields over positional legacy indices in all downstream code.

