# 3D UI MVP Guide

## Scope

This guide covers the manual-input 3D UI MVP route (`/analysis-3d`) and backend
API integration against `/api/v1/3d/*`.

## Quickstart

1. Open `3D Analysis` page from the 2D header switch.
2. Fill required tabs: Method, Grid, Slip Surface, Surfaces, Materials.
3. Click `Validate 3D Input`.
4. Click `Run 3D Analysis` or enable comparison mode and run multi-method.

## Troubleshooting

- Validation error in tab:
  - Open highlighted tab and correct invalid field values.
- `payload_too_large`:
  - Reduce `col_x_max` / `col_y_max` or disable debug rows.
- Non-converged method:
  - Increase iterations, adjust tolerance, or compare against nearby methods.

## Deferred

- Interactive 3D visualizer is intentionally deferred in MVP.
- CSV upload workflows are deferred; manual points are used in this phase.

## Model Fidelity (Reinforcement)

- Current reinforcement behavior is a simplified phase-2 engineering approximation.
- It uses a uniform per-column added resistance model for FS impact.
- Full direction-aware nail-slip intersection remains deferred.
- Treat reinforcement-driven FS gain as model-relative guidance, not an exact field prediction.

## QA Checklist

- [ ] 2D route still works unchanged.
- [ ] 3D validate endpoint returns valid/invalid state correctly.
- [ ] Single run shows FS/critical direction/convergence.
- [ ] Multi run shows mixed success/failure rows correctly.
- [ ] Payload preview matches submitted JSON exactly.
- [ ] Reinforcement messaging appears only when reinforcement is enabled.
- [ ] No reinforcement UI string claims exact/full-real/rigorous modeling.

## Golden Scenario (Baseline Lock)

- Method: `1`
- Grid: `x=[0,2], y=[0,2], z=[0,20], col_x=8, col_y=8`
- Slip: ellipsoid center `(1,1,9)`, radii `(2,2,3)`
- Surface points:
  - `(0,0,10)`
  - `(2,0,10)`
  - `(0,2,9.5)`
  - `(2,2,9.5)`

Expected:

- validate succeeds,
- single-run returns deterministic `fs_min` range across repeated runs,
- multi-run returns mixed/consistent rows per selected methods.

## Renderer Phase Notes

- Preview tab includes static top-surface points, slip wireframe, and grid bounds.
- Interactive visualizer depth remains limited to controls/toggles in post-MVP renderer phase.

