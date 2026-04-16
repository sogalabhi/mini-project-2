# Cheng-Yip Method Notes (Phase 10)

## Scope

This note documents the rewritten Cheng-Yip module:

- implementation file: `3d_slope_stability/solvers/cheng_yip.py`
- lambda policy file: `3d_slope_stability/solvers/lambda_update.py`

## Variant Mapping

- `method_id=4` -> Bishop-like mode
- `method_id=5` -> Janbu-like simplified mode
- `method_id=6` -> Janbu-like corrected mode
- `method_id=7` -> Spencer-like coupled mode

## Core Behavior

Each direction evaluates two FS tracks:

- `FS_force`
- `FS_moment`

Mode selection:

- Bishop-like uses moment-focused update.
- Janbu-like uses force-focused update.
- Spencer-like uses averaged update plus mismatch coupling.

## Spencer-like Coupling

Mismatch term:

- `mismatch = FS_force - FS_moment`

Coupled acceptance:

- both FS fixed-point convergence and mismatch bound must be satisfied.

Lambda updates are applied when mismatch is not acceptable.

## Lambda Diagnostics

Per-direction diagnostics include:

- `lambda_final`
- `lambda_iterations`
- `oscillation_count`
- `mismatch_final`
- trajectory lengths for lambda and FS pair histories

Method-level diagnostics include:

- variant name
- candidate count
- `max_mismatch_abs`
- `avg_mismatch_abs`

## Stability Safeguards

- step shrinking on sign flips/worsening mismatch
- lambda clamping to bounds
- minimum-step stall detection
- explicit non-convergence reasons (`max_iterations_exceeded`, `lambda_stalled`)

## Validation References

Covered by:

- `tests/unit/test_cheng_yip_phase10.py`

Checks include:

- variant convergence on controlled fixtures
- lambda update behavior
- corrected Janbu-like >= simplified Janbu-like on controlled fixtures

