# 3D LEM Rewrite Specification (Phase 0)

## Purpose

This document defines the Phase 0 rewrite specification package for the clean-room
3D LEM backend rewrite. It establishes:

- equation contract (what must be computed and with which symbols),
- data contract (typed inputs/outputs and invariants),
- risk register (known technical risks and mitigation strategy).

This specification is intentionally independent from legacy implementation details
and should be treated as the source of truth for Phase 1+ development.

## Scope

In scope:

- 3D preprocessing from DEM/layer/water/slip surfaces to canonical column states.
- 3D method families:
  - Hungr-Bishop,
  - Hungr-Janbu (simplified and corrected),
  - Cheng-Yip variants.
- Direction search and convergence control.
- Diagnostics and deterministic outputs.

Out of scope:

- frontend/UI behaviors,
- 2D methods,
- persistence/database concerns,
- cloud/distributed execution.

## Equation Contract

## Symbols

- Column index: `i`.
- Sliding direction: `theta`.
- Factor of safety: `FS`.
- Unit weight: `gamma`.
- Column volume: `V_i`.
- Column weight: `W_i = gamma_i * V_i`.
- Base area: `A_b_i`.
- Base dip and dip direction: `alpha_i`, `beta_i`.
- Effective normal stress at base: `sigma_eff_i`.
- Pore pressure at base: `u_i`.
- Effective normal force: `N_eff_i`.
- Shear strength at base: `tau_f_i`.
- Mobilized shear stress: `tau_m_i`.
- Cohesion and friction: `c_i`, `phi_i`.
- Seismic coefficients: `k_h`, `k_v`.
- Intercolumn force inclination/scaling terms for advanced methods: `lambda`.

## Geometric and Column-State Equations

1. Column volume and weight:
   - `W_i = gamma_i * V_i`.
2. Base orientation and directional components:
   - compute base normal vector from base polygon geometry,
   - derive `alpha_i` and `beta_i` from base normal with canonical axis conventions.
3. Stress terms:
   - total normal stress and pore pressure are computed from column geometry + hydro model,
   - `sigma_eff_i = sigma_total_i - u_i`.

## Shear Strength Contract

For each column base:

- Mohr-Coulomb:
  - `tau_f_i = c_i + sigma_eff_i * tan(phi_i)`.
- Undrained and power/user-defined models:
  - must return equivalent `(phi_i, c_i)` or direct `tau_f_i`,
  - mapping must be explicit in model resolver diagnostics.

Unsaturated contribution, when enabled, augments shear strength using configured
model and must be reported in diagnostics.

## Global Equilibrium Contract

For each candidate direction `theta`:

- Compute directional force/moment terms for all active columns.
- Evaluate method-specific equilibrium equations iteratively to solve for `FS(theta)`.
- Convergence criteria:
  - `abs(FS_k - FS_(k-1)) <= tol_fs` and any method-specific auxiliary checks.
- If convergence fails by `iter_max`, mark direction as non-converged with reason.

Direction search returns:

- critical direction `theta_crit`,
- minimum converged `FS_min`,
- per-direction trace payload (optional based on settings).

## Method Contract

The following method IDs are reserved for compatibility:

- `1`: Hungr-Bishop.
- `2`: Hungr-Janbu simplified.
- `3`: Hungr-Janbu corrected.
- `4`: Cheng-Yip Bishop variant.
- `5`: Cheng-Yip Janbu simplified.
- `6`: Cheng-Yip Janbu corrected.
- `7`: Cheng-Yip Spencer variant.

All solvers must expose a common interface:

- input: canonical analysis rows + method options,
- output: `MethodComputationResult`.

## Data Contract

## Core Typed Inputs

- `DEMPoint`: `(x, y, z)`.
- `SurfaceDataset`: labeled collection of DEM points and interpolation policy.
- `MaterialModel`: model type + model parameters + unit weight.
- `WaterModel`: groundwater surface and water unit weight.
- `SlipSurfaceConfig`: ellipsoid or DEM-defined surface config.
- `GridConfig`: canvas bounds + cell counts.
- `DirectionSearchConfig`: direction spacing/tolerance/override.
- `SolverConfig`: iteration and convergence limits.

## Canonical Intermediate Objects

- `ColumnCornerState`
  - corner coordinates,
  - stacked layer elevations/types.
- `ColumnCenterState`
  - center coordinates and active layer context.
- `ColumnState`
  - full geometry, hydro, strength, and stress components.
- `AnalysisRow`
  - named fields replacing legacy positional columns.

## Output Contract

- `DirectionResult`
  - direction angle,
  - converged flag,
  - FS terms,
  - iteration counts,
  - failure reason (if any).
- `MethodComputationResult`
  - method identifier,
  - `FS_min`,
  - critical direction,
  - per-direction results,
  - diagnostics.
- `PipelineResult`
  - preprocessing summaries,
  - canonical rows,
  - method result,
  - export metadata.

## Invariants

- No floating-point tuple dictionary keys in public data models.
- Angles are stored internally in radians.
- All units are canonicalized at ingest boundary.
- No import-time side effects.
- All file IO is explicit and optional in pipeline API.

## Risk Register

## R1 - Equation Transcription Risk

- Risk: incorrect translation from literature/legacy to new code.
- Impact: invalid FS results.
- Mitigation:
  - equation-level review checklist,
  - unit tests per equation block,
  - benchmark fixture comparison.

## R2 - Geometry Drift

- Risk: base area/dip/direction calculations drift from expected geometry.
- Impact: systemic bias in FS.
- Mitigation:
  - synthetic geometry fixtures with analytical targets,
  - strict tolerance assertions.

## R3 - Interpolation Behavioral Drift

- Risk: modern interpolation APIs produce different surfaces than legacy.
- Impact: different column shapes and FS.
- Mitigation:
  - fixed deterministic interpolation fixtures,
  - documented interpolation choices and seeds.

## R4 - Convergence Instability

- Risk: iterative solver divergence/oscillation for some directions.
- Impact: incomplete search or wrong critical direction.
- Mitigation:
  - configurable damping,
  - robust stop conditions,
  - non-converged direction handling strategy.

## R5 - Performance Regression

- Risk: rewrite is cleaner but slower.
- Impact: unusable for moderate/large grids.
- Mitigation:
  - benchmark matrix in CI,
  - stage-level profiling,
  - targeted vectorization of hotspots.

## R6 - Silent Data Misalignment

- Risk: column field mis-mapping during migration.
- Impact: subtle incorrect stresses/strengths.
- Mitigation:
  - typed dataclasses only,
  - schema validation,
  - no positional indexing in core solver code.

## R7 - Unit/Angle Handling Errors

- Risk: degree/radian or unit conversion mistakes.
- Impact: large physical errors.
- Mitigation:
  - centralized conversion utilities,
  - angle/unit invariants validated in constructors.

## R8 - Legacy Compatibility Ambiguity

- Risk: stakeholders expect exact legacy values despite bug fixes.
- Impact: acceptance friction.
- Mitigation:
  - document expected differences,
  - optional legacy-export adapter,
  - tolerance-based acceptance criteria.

## Phase 0 Deliverables Checklist

- [x] Equation contract defined.
- [x] Data contract defined.
- [x] Risk register with mitigation actions.
- [x] Method ID compatibility mapping defined.
- [x] Invariants and guardrails defined.
