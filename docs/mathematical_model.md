# 3D LEM Mathematical Model Reference

## Scope

This document defines the equation-level reference for the rewritten 3D LEM module.
It covers the currently implemented method families:

- Hungr-Bishop (`method_id=1`)
- Hungr-Janbu simplified/corrected (`method_id=2/3`)
- Cheng-Yip variants (`method_id=4/5/6/7`)

## Shared Symbols

- `i`: column index.
- `theta`: candidate sliding direction.
- `FS`: factor of safety.
- `W_i`: column weight.
- `A_i`: base area.
- `alpha_i`: base dip.
- `beta_i`: base dip direction.
- `c_i`, `phi_i`: cohesion and friction angle.
- `N_eff_i`: effective normal force proxy.
- `u_i`: pore pressure.

## Shared Terms

- Effective stress proxy at base:
  - `sigma_eff_i = max(0, sigma_total_i - u_i)`
- Mohr-Coulomb resistance component:
  - `R_i = c_i * A_i + N_eff_i * tan(phi_i)`
- Direction alignment term:
  - `alignment_i = max(0.2, abs(cos(theta - beta_i)))`
- Driving term:
  - `D_i = W_i * sin(alpha_i) * alignment_i`

## Hungr-Bishop (method 1)

Iterative fixed-point structure:

- `FS_{k+1} = sum(R_i / m_alpha_i) / sum(D_i)`
- `m_alpha_i = cos(alpha_i) + (sin(alpha_i) * tan(phi_i))/FS_k`

Convergence:

- `abs(FS_{k+1} - FS_k) <= tol_fs`
- stop at `max_iterations` if not converged.

## Hungr-Janbu Simplified (method 2)

Force-equilibrium style:

- `FS = sum(R_i) / sum(D_i)`

Convergence uses the same fixed-point/damping framework as Bishop.

## Hungr-Janbu Corrected (method 3)

Corrected Janbu:

- `FS_corrected = FS_simplified * C_j`

Current bounded deterministic correction factor:

- `C_j = 1 + 0.08*sin(avg_dip) + 0.05*tan(avg_phi)`
- `C_j` clamped to `[1.0, 1.35]`.

## Cheng-Yip Unified Framework (methods 4/5/6/7)

The implementation tracks force and moment FS pairs per direction:

- `FS_force = sum(R_force_i) / sum(D_force_i)`
- `FS_moment = sum(R_moment_i) / sum(D_moment_i)`

Mode behavior:

- method `4` (Bishop-like): use moment-dominant FS path.
- method `5` (Janbu-like): use force-dominant FS path.
- method `6` (Janbu-like corrected): force path with correction branch.
- method `7` (Spencer-like): coupled force/moment condition with lambda updates.

## Lambda Strategy (Spencer-like)

- Bidirectional updates based on mismatch sign:
  - mismatch = `FS_force - FS_moment`
- step reduction on oscillation or worsening mismatch.
- safeguards:
  - lambda bounds,
  - minimum step stall detection,
  - capped oscillation tracking.

## Convergence and Selection

For each direction candidate:

- iterate until FS convergence and any method-specific coupled condition.
- record diagnostics and failure reason on non-convergence.

Global result:

- select minimum converged FS over direction candidates.

## Assumptions and Limits

- Deterministic approximations are used in this rewrite stage.
- Some advanced method equations are represented by controlled approximations
  that preserve expected behavior and stability while enabling modular extension.
- Full publication-grade equation parity can be tightened in later calibration phases.

