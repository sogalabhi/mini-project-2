# Hungr Method Notes (Phase 9)

## Scope

This note documents the current implementation behavior for:

- Hungr-Janbu simplified (`method_id=2`)
- Hungr-Janbu corrected (`method_id=3`)

Implemented in:

- `3d_slope_stability/solvers/hungr_janbu.py`

## Simplified Janbu (method 2)

The simplified Janbu variant uses force-equilibrium style iteration:

- `FS = sum(Resisting_i) / sum(Driving_i)`
- where each column contributes:
  - `Resisting_i = c_i * A_i + N_eff_i * tan(phi_i)`
  - `Driving_i = W_i * sin(alpha_i) * alignment_i`

The solver is run per candidate sliding direction and converges with:

- fixed-point update,
- configurable damping,
- tolerance-based stopping (`tol_fs`),
- iteration cap (`max_iterations`).

## Corrected Janbu (method 3)

The corrected variant applies a correction factor to simplified Janbu FS:

- `FS_corrected = FS_simplified * C_j`

Current implementation uses a deterministic bounded approximation:

- `C_j = 1 + 0.08*sin(avg_dip) + 0.05*tan(avg_phi)`
- clamped to `[1.0, 1.35]`

Where:

- `avg_dip` is average base dip (radians) across active columns.
- `avg_phi` is average friction angle (radians) across active columns.

## Expected Behavior

For identical input rows and direction settings:

- corrected Janbu should be greater than or equal to simplified Janbu,
- because correction factor `C_j >= 1.0`.

This behavior is verified in:

- `tests/unit/test_hungr_janbu_phase9.py`
  - `test_janbu_corrected_converges_and_is_not_lower_than_simplified`

## Notes and Limitations

- The correction branch is deterministic and stable for Phase 9 closure.
- The correction formula is currently an MVP approximation and may be refined
  in later phases with benchmark-calibrated method-specific equations.
- Direction search and result aggregation are shared with Bishop-style solver
  infrastructure from Phase 7.

