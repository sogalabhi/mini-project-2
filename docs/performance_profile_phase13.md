# Phase 13 Performance Profile (Gate E)

## Goal

Document benchmark/profile measurements and confirm runtime is within expected
bounds after Phase 13 (`benchmarks/matrix.py` + `benchmarks/timers.py`).

## Benchmark Setup

- Matrix source: `3d_slope_stability.benchmarks.run_benchmark_matrix`
- Determinism: fixed seed `42`
- Grid sizes:
  - `small` (8x8)
  - `medium` (16x16)
  - `large` (24x24)
- Methods:
  - Bishop (`method_id=1`)
  - Janbu simplified (`method_id=2`)
  - Spencer-like (`method_id=7`)
- Solver profiles:
  - `(max_iterations=80, tol_fs=1e-3)`
  - `(max_iterations=120, tol_fs=5e-4)`
- Surface/material fixture:
  - deterministic synthetic top surface
  - single Mohr-Coulomb material (`phi=30 deg, c=5, gamma=18`)

Total benchmark rows: `18`.

## Measured Results

From the benchmark matrix summary run:

- Total time by grid size:
  - `small`: avg `0.00303s`, max `0.00355s`
  - `medium`: avg `0.01250s`, max `0.01789s`
  - `large`: avg `0.02854s`, max `0.03933s`

- Solver-core time by method:
  - method `1`: avg `0.00395s`, max `0.01081s`
  - method `2`: avg `0.00172s`, max `0.00313s`
  - method `7`: avg `0.00315s`, max `0.00592s`

- Stage maxima and averages:
  - interpolation: max `0.02255s`, avg `0.00591s`
  - grid_assembly: max `0.00040s`, avg `0.00015s`
  - slip_intersection: max `0.00264s`, avg `0.00117s`
  - hydro_strength: max `0.01543s`, avg `0.00452s`
  - solver_core: max `0.01081s`, avg `0.00294s`
  - total: max `0.03933s`, avg `0.01469s`

## Expected Bounds

For this synthetic benchmark fixture, acceptable bounds are defined as:

- `small` total max <= `0.010s`
- `medium` total max <= `0.030s`
- `large` total max <= `0.060s`
- global total max <= `0.060s`
- global solver_core max <= `0.020s`

## Bound Check

All measured metrics are within expected bounds:

- `small` max `0.00355s` <= `0.010s` : PASS
- `medium` max `0.01789s` <= `0.030s` : PASS
- `large` max `0.03933s` <= `0.060s` : PASS
- global total max `0.03933s` <= `0.060s` : PASS
- global solver_core max `0.01081s` <= `0.020s` : PASS

## Optimization Notes (Phase 13)

Applied in solver hot loops:

- precomputed row-level trig/static terms per direction in:
  - `solvers/hungr_bishop.py`
  - `solvers/hungr_janbu.py`
  - `solvers/cheng_yip.py`
- reduced repeated per-iteration allocations/recomputation.

## Gate E Status

Gate E requirement:

- \"Performance profile documented and within expected bounds.\"

Status: **PASS**.

