# Slope Stability Methodology Reference (All 9 Methods)

## Scope

This document consolidates the mathematical methodology used in this project for:

- 2D methods (2 total)
  - Bishop
  - Fellenius (Ordinary Method of Slices)
- 3D methods (7 total)
  - Hungr-Bishop
  - Hungr-Janbu Simplified
  - Hungr-Janbu Corrected
  - Cheng-Yip Bishop-like
  - Cheng-Yip Janbu-like
  - Cheng-Yip Janbu-like Corrected
  - Cheng-Yip Spencer-like

This is a project-level engineering reference, aligned with implementation behavior.

---

## Common Notation

- `FS`: Factor of Safety.
- `R`: resisting force (or moment-equivalent resisting term).
- `D`: driving force (or moment-equivalent driving term).
- `i`: slice index (2D) or column index (3D).
- `W_i`: weight of slice/column.
- `c_i, phi_i`: cohesion and friction angle.
- `u_i`: pore pressure.
- `N_eff_i`: effective normal force proxy.
- `alpha_i`: base dip.
- `beta_i`: base dip direction (3D).
- `theta`: candidate sliding direction (3D).

In all methods, conceptually:

- `FS = resisting / driving`
- `FS > 1` indicates stable against that failure mechanism.

---

## 2D Methods

## 1) Bishop (2D)

### Concept

Bishop Simplified is an iterative method of slices for circular failure surfaces.
It includes normal force interaction in a simplified way and is generally more accurate than ordinary slices for many practical cases.

### Core idea

For each slice:

- resisting term includes `c'` and friction based on effective normal force,
- driving term comes from slice weight and base inclination.

Global FS is solved iteratively because FS appears on both sides.

### Typical form

One common Bishop simplified structure:

- `FS = sum((c' * b + (W - u * b) * tan(phi')) / m_alpha) / sum(W * sin(alpha))`
- `m_alpha = cos(alpha) + (sin(alpha) * tan(phi')) / FS`

### In this codebase

- Main 2D analysis endpoint reports `"method": "Bishop"`.
- Bishop is the primary returned method in `/analyze`.
- Comparison mode also computes Bishop over shared candidate circles.

---

## 2) Fellenius (2D, Ordinary Method of Slices)

### Concept

Fellenius (Swedish circle / Ordinary Method of Slices) is a non-iterative force-ratio method.
It neglects inter-slice force equilibrium in detail, so it is usually more conservative.

### Core idea

For each slice:

- `R_i = c_i * l_i + N_eff_i * tan(phi_i)`
- `D_i = W_i * sin(alpha_i)`

Then:

- `FS = sum(R_i) / sum(D_i)`

### In this codebase

- Implemented as comparison method `"Fellenius"` in `run_comparison`.
- Uses generated candidate circles and selects minimum FS circle.
- Useful as a baseline against Bishop for consistency checks.

---

## 3D Shared Model Structure (All 7 3D Methods)

The 3D implementation evaluates many direction candidates and aggregates to the critical FS.

Shared terms:

- `R_i = c_i * A_i + N_eff_i * tan(phi_i)` (plus optional reinforcement term)
- `D_i = W_i * sin(alpha_i) * alignment_i`
- `alignment_i = max(0.2, abs(cos(theta - beta_i)))`

Direction search:

- For each `theta`, solve method equations.
- Keep converged solutions.
- Global result is minimum converged FS over all directions.

---

## 3) Hungr-Bishop (3D, method_id=1)

### Concept

3D analogue of Bishop-style iterative equilibrium with a correction factor in denominator term per column.

### Equation pattern

- `FS_{k+1} = sum(R_i / m_alpha_i) / sum(D_i)`
- `m_alpha_i = cos(alpha_i) + (sin(alpha_i) * tan(phi_i)) / FS_k`

### Characteristics

- Iterative fixed-point method.
- Good practical stability for many models.
- Includes convergence checks via tolerance and max iterations.

---

## 4) Hungr-Janbu Simplified (3D, method_id=2)

### Concept

Force-equilibrium style ratio without full moment coupling.

### Equation pattern

- `FS = sum(R_i) / sum(D_i)`

### Characteristics

- Typically faster than coupled methods.
- Can be conservative relative to corrected variants.

---

## 5) Hungr-Janbu Corrected (3D, method_id=3)

### Concept

Applies correction factor over simplified Janbu.

### Equation pattern

- `FS_corrected = FS_simplified * C_j`
- current implementation:
  - `C_j = 1 + 0.08*sin(avg_dip) + 0.05*tan(avg_phi)`
  - `C_j` clamped to `[1.0, 1.35]`

### Characteristics

- Deterministic bounded correction.
- Expected to be `>=` simplified Janbu for same case.

---

## 6) Cheng-Yip Bishop-like (3D, method_id=4)

### Concept

Unified Cheng-Yip framework operated in moment-dominant mode.

### Equation pattern

Framework computes:

- `FS_force = sum(R_force_i)/sum(D_force_i)`
- `FS_moment = sum(R_moment_i)/sum(D_moment_i)`

Bishop-like branch selects moment-focused update path.

### Characteristics

- Behaves analogous to a moment-oriented Bishop family variant.

---

## 7) Cheng-Yip Janbu-like (3D, method_id=5)

### Concept

Unified Cheng-Yip framework in force-dominant mode.

### Equation pattern

- Same dual-track structure (`FS_force`, `FS_moment`)
- Janbu-like branch follows force-focused update behavior.

### Characteristics

- Useful where force-balance style behavior is preferred.

---

## 8) Cheng-Yip Janbu-like Corrected (3D, method_id=6)

### Concept

Janbu-like force branch with correction behavior.

### Equation pattern

- Starts from Janbu-like force path and applies corrected-branch logic in framework.

### Characteristics

- Should trend above non-corrected Janbu-like in controlled comparisons.

---

## 9) Cheng-Yip Spencer-like (3D, method_id=7)

### Concept

Coupled force-moment equilibrium using lambda updates (Spencer-like).

### Coupling logic

- mismatch: `mismatch = FS_force - FS_moment`
- update lambda to reduce mismatch
- converge only if:
  - FS update converges, and
  - mismatch criteria satisfied

### Safeguards

- lambda bounds
- step reduction on oscillation/worsening
- stall detection

### Characteristics

- Most coupled of current 3D variants.
- Can be more computationally expensive but richer equilibrium behavior.

---

## Reinforcement Term (Current 3D Phase-2 Model)

Applied in 3D methods when reinforcement is enabled:

- `T_y = A_s * f_y`
- `T_bond = pi * d * L_embed * tau_bond`
- `T_max = min(T_y, T_bond)`
- `q_nail = T_max / (S_x * S_y)`
- `R_nail_i = q_nail * A_b_i`

Updated resisting term:

- `R_i = c_i * A_i + N_eff_i * tan(phi_i) + R_nail_i`

Optional vertical coupling:

- `N_eff_i_adj = N_eff_i + R_nail_i * tan(theta_nail)`

Important:

- This is a simplified engineering approximation in current phase.
- Full direction-aware nail-slip geometric intersection is deferred.

---

## Method Comparison Summary

| Method | Dim | Family | Solver Type | Coupling Level | Typical Use |
|---|---:|---|---|---|---|
| Bishop | 2D | Bishop Simplified | Iterative | Medium | Primary 2D FS |
| Fellenius | 2D | Ordinary Slices | Direct ratio | Low | Quick conservative baseline |
| Hungr-Bishop | 3D | Hungr | Iterative | Medium | Stable general 3D baseline |
| Hungr-Janbu Simplified | 3D | Hungr | Ratio/iterative framework | Low-Medium | Fast force-balance style |
| Hungr-Janbu Corrected | 3D | Hungr | Corrected ratio | Medium | Improved Janbu estimate |
| Cheng-Yip Bishop-like | 3D | Cheng-Yip | Unified dual-track | Medium | Moment-focused variant |
| Cheng-Yip Janbu-like | 3D | Cheng-Yip | Unified dual-track | Medium | Force-focused variant |
| Cheng-Yip Janbu-like Corrected | 3D | Cheng-Yip | Unified + correction | Medium-High | Corrected force variant |
| Cheng-Yip Spencer-like | 3D | Cheng-Yip | Coupled with lambda | High | Strong force-moment coupling |

---

## Practical Interpretation Guidance

- Compare methods on the same geometry/material/load setup.
- Treat method spread as epistemic/model uncertainty indicator.
- Use corrected/coupled methods when you need stronger equilibrium coupling checks.
- For screening or early iteration, simpler methods are faster.
- For final decision support, review:
  - convergence status,
  - diagnostics,
  - method-to-method consistency,
  - sensitivity to direction search and reinforcement assumptions.

---

## Project-Specific Notes

- 2D API currently exposes Bishop as primary method and Fellenius via comparison output.
- 3D API exposes method IDs `1..7` with versioned endpoints under `/api/v1/3d/*`.
- 3D math and method notes are also documented in:
  - `docs/mathematical_model.md`
  - `docs/method_notes_hungr.md`
  - `docs/method_notes_cheng_yip.md`

This file is the consolidated “all methods at one place” reference.

---

## Implementation-Level Deep Dive (Expanded)

This section extends the document with code-path-level methodology and execution logic,
including how candidate surfaces are generated, shared, and evaluated.

---

## Part A: 2D Engine Deep Dive

## A1. 2D Program Architecture

The 2D solver flow in this project is implemented in the `SlopeStabilityAnalyzer`
class and exposed through backend endpoints.

High-level 2D execution:

1. Build geometry and materials.
2. Apply loads and water table.
3. Configure settings:
   - `num_slices` (default 50),
   - `num_iterations` (default 2000),
   - `tolerance` (default 0.001).
4. Run primary Bishop analysis.
5. Run method comparison (`Bishop` and `Fellenius`) on shared candidate circles.
6. Return outputs.

Key files:

- `slope_analyzer.py` (2D methodology and implementation)
- `backend/main.py` (2D API route orchestration)

---

## A2. Why 2000 Iterations for 2D Comparison

The default `num_iterations=2000` is used as a practical candidate-surface search budget.
In this implementation, each "iteration" means attempting to generate one candidate
circular slip surface for comparison workflow.

Important detail:

- This does **not** mean 2000 Newton iterations for one equation.
- It means up to 2000 **candidate circles** attempted and filtered.

Actual valid circle count can be lower than 2000 because geometric filters reject invalid circles.

---

## A3. Shared Candidate Set (Critical Comparison Principle)

In `run_comparison`, the implementation generates one shared list:

- `circles = _generate_candidate_circles(circle_count, seed)`

Then the same `circles` list is sent to:

- `_run_bishop_on_circles(circles)`
- `_run_fellenius_on_circles(circles)`

This is an important methodology choice:

- It removes sampling bias between methods.
- Any difference in FS comes from method equations, not from different surface populations.

This is exactly what you asked for: same generated set used by both 2D methods.

---

## A4. Deterministic Reproducibility in 2D

The comparison routine uses a fixed seed (default `seed=42`).

Benefits:

- repeated calls with same input produce same candidate circles,
- method comparison is stable and auditable,
- regression testing is easier.

The returned comparison payload includes:

- `circle_count` (actual valid generated circles),
- `seed`.

---

## A5. Candidate Circle Generation Logic (2D)

Candidate generation implementation is in `_generate_candidate_circles`.

Per attempted sample:

1. Compute slope ratio:
   - `m = height / length`
2. Sample two x-intersection candidates:
   - `x1` sampled near upper slope region,
   - `x2` sampled further downslope with minimum separation.
3. Compute corresponding slope surface points:
   - `y1 = m * x1`
   - `y2 = m * x2`
4. Compute midpoint and chord.
5. Construct normal direction to chord.
6. Sample normal offset distance.
7. Compute candidate circle center `(cx, cy)` and radius `r`.
8. Apply validity checks:
   - positive chord,
   - center elevation check (reject unrealistic geometry),
   - non-degenerate arc projection.
9. Keep valid candidate.

This produces a stochastic but constrained population of plausible circles.

---

## A6. 2D Bishop Comparison Path Details

In `_run_bishop_on_circles`:

1. Build PySlope model.
2. Clear default search limits/planes.
3. Add each generated candidate as explicit circular plane.
4. Run PySlope analysis.
5. Extract minimum FS and associated critical circle.

Method output:

- `method_name="Bishop"`
- `fos`
- `critical_circle_center`
- `critical_circle_radius`

This gives direct "best-of-population" Bishop result on the shared circle set.

---

## A7. 2D Fellenius Comparison Path Details

In `_run_fellenius_on_circles`:

1. Loop over the same shared circles.
2. For each circle call `_fellenius_fos_for_circle`.
3. Keep minimum FS.
4. Return method result.

Inside `_fellenius_fos_for_circle`:

1. Compute circle intersections with slope line.
2. Slice interval into `n = max(10, num_slices)`.
3. For each slice:
   - get mid-point coordinates,
   - compute base elevation from circle,
   - compute slice thickness,
   - compute base inclination `alpha`,
   - compute base length `l_base`,
   - compute equivalent soil properties through depth,
   - compute weight `W`,
   - add UDL/line load contributions,
   - compute pore pressure `u` if water table exists,
   - compute `N_eff`,
   - compute resisting and driving terms.
4. Aggregate:
   - `FS = sum_resisting / sum_driving`

This is an explicit OMoS-style implementation in project code.

---

## A8. 2D Load and Water Effects

Both methods include load/water effects but through their own computational paths:

- Bishop path via PySlope model behavior.
- Fellenius path via explicit in-loop contributions.

Load incorporation in Fellenius implementation:

- UDL contributes distributed force across covered slice width.
- Line load contributes near slice location threshold.

Water incorporation:

- pore pressure from head at base (`head = water_table_y - y_base` if positive),
- `u = gamma_w * head`,
- `N_eff = W*cos(alpha) - u*l_base`.

---

## A9. 2D Output Interpretation

Comparison output gives:

- Bishop FS on shared circles.
- Fellenius FS on same circles.

Interpretation pattern:

- If Bishop > Fellenius (common), ordinary method is conservative.
- Large gap can indicate sensitivity to interslice-force treatment and pore pressure.
- Similar values can indicate robust geometry and moderate stress state.

---

## A10. 2D Methodological Limits

- Circular surface family only (in current comparison routine).
- Candidate generation is random-search constrained, not exhaustive.
- Fellenius is simplified (no full interslice force equilibrium).
- Bishop relies on PySlope implementation details for internal iteration path.

---

## Part B: 3D Engine Deep Dive

## B1. 3D Program Architecture

High-level 3D flow:

1. Validate and map API payload.
2. Build columns from top/slip/hydro/material models.
3. Dispatch selected method by `method_id`.
4. Evaluate across direction candidates.
5. Aggregate minimum converged FS.
6. Return diagnostics and optional render data.

Key components:

- Config and method options (`method_options`)
- Pipeline (`pipeline/runner.py`, preprocess/dispatcher)
- Solvers (`hungr_bishop.py`, `hungr_janbu.py`, `cheng_yip.py`)
- API adapter normalization (`three_d_mapper.py`)

---

## B2. 3D Shared Preprocessing

Before any 3D method runs, canonical rows are built:

- grid discretization,
- slip intersection with columns,
- hydro state assignment,
- strength state assignment,
- geometric state (`z_top`, `z_bottom`, `base_area`, `dip`, `dip_direction`),
- stress proxies and diagnostics.

This canonical row representation is crucial because all methods evaluate the same base geometry/material state.

---

## B3. 3D Direction Search Philosophy

Unlike 2D circular search, 3D method family evaluates directional resistance/driving behavior:

- candidate directions generated from spacing/tolerance configuration,
- per-direction FS solved by method-specific equations,
- final FS is minimum converged value.

This maps to the idea of finding the most critical movement direction of the 3D mass.

---

## B4. Hungr-Bishop Detailed Methodology (3D)

For each candidate direction:

1. Compute per-column terms:
   - driving proxy from weight, base dip, directional alignment,
   - resisting proxy from cohesion + friction.
2. Build Bishop-style denominator coupling term (`m_alpha_i`).
3. Iterate FS fixed-point update until:
   - `|FS_{k+1} - FS_k| <= tol_fs`, or
   - iteration cap reached.
4. Track per-direction diagnostics:
   - convergence flag,
   - iteration count,
   - method terms summary.

Across directions:

- choose minimum converged FS.

---

## B5. Hungr-Janbu Simplified Detailed Methodology (3D)

For each direction:

1. Compute `R_i` and `D_i` from canonical rows and directional alignment.
2. Evaluate force-ratio style FS.
3. Use solver framework damping/tolerance controls for stability.

Key behavior:

- simpler coupling than Bishop,
- often faster and less stiff numerically.

---

## B6. Hungr-Janbu Corrected Detailed Methodology (3D)

After simplified estimate:

1. Compute case-average descriptors (dip/friction).
2. Build correction factor:
   - `C_j = 1 + 0.08*sin(avg_dip) + 0.05*tan(avg_phi)`
   - clamp to `[1.0, 1.35]`
3. Correct:
   - `FS_corrected = FS_simplified * C_j`

This provides bounded uplift in line with corrected-family behavior.

---

## B7. Cheng-Yip Framework Detailed Methodology (3D)

Cheng-Yip implementation evaluates two tracks:

- `FS_force`
- `FS_moment`

All variants share:

1. compute per-direction force and moment aggregates,
2. iterate update rules,
3. track mismatch and diagnostics.

Variant-specific branch:

- method 4: moment-focused update route,
- method 5: force-focused route,
- method 6: force route + correction logic,
- method 7: coupled Spencer-like route using lambda.

---

## B8. Spencer-like Lambda Coupling (Method 7)

Spencer-like branch introduces lambda to couple force and moment tracks.

Core quantities:

- `mismatch = FS_force - FS_moment`

Iteration logic:

1. update FS estimates,
2. evaluate mismatch,
3. update lambda direction and step size,
4. reduce step if oscillation/worsening is detected,
5. enforce bounds.

Convergence requires:

- FS criteria + mismatch criteria both satisfied.

Diagnostics include:

- final lambda,
- lambda iterations,
- oscillation count,
- final mismatch.

---

## B9. 3D Reinforcement Integration

When enabled, a Phase-2 simplified reinforcement term is added per column.

Steps:

1. Compute yield-limited tension:
   - `T_y = A_s * f_y`
2. Compute bond-limited tension:
   - `T_bond = pi * d * L_embed * tau_bond`
3. Select capacity:
   - `T_max = min(T_y, T_bond)`
4. Convert to distributed resistance:
   - `q_nail = T_max / (S_x * S_y)`
   - `R_nail_i = q_nail * A_b_i`
5. Add to resisting term.
6. Optional vertical coupling adjusts normal term.

Limit:

- no explicit geometric nail-slip intersection in current phase.

---

## B10. 3D API Method Mapping

- `method_id=1`: Hungr-Bishop
- `method_id=2`: Hungr-Janbu Simplified
- `method_id=3`: Hungr-Janbu Corrected
- `method_id=4`: Cheng-Yip Bishop-like
- `method_id=5`: Cheng-Yip Janbu-like
- `method_id=6`: Cheng-Yip Janbu-like Corrected
- `method_id=7`: Cheng-Yip Spencer-like

API entry points:

- single run: `/api/v1/3d/analyze`
- multi run: `/api/v1/3d/analyze/multi`
- methods list: `/api/v1/3d/methods`

---

## Part C: Comparison Methodology Across All 9 Methods

## C1. Fair Comparison Principles

To compare methods meaningfully:

1. Keep geometry fixed.
2. Keep material parameters fixed.
3. Keep load/water settings fixed.
4. Keep search population fixed where applicable.
5. Keep convergence settings fixed.

2D code explicitly satisfies #4 by sharing identical candidate circles between Bishop/Fellenius.

3D multi-run satisfies #1-#3 and method sweep by cloning base request then switching `method_id`.

---

## C2. What "Same Inputs" Means in Practice

2D same-input comparison:

- same slope geometry,
- same material layering,
- same loads and water state,
- same random seed,
- same generated candidate circles.

3D same-input comparison:

- same canonical rows from preprocessing,
- same direction search settings,
- same hydro/material state,
- different only in method equations and branch logic.

---

## C3. Method Spread Interpretation

If methods disagree:

- do not assume one is "wrong" immediately,
- check whether spread is from coupling assumptions,
- inspect convergence diagnostics,
- run sensitivity on direction spacing (3D) or circle count/seed (2D).

Engineering practice:

- narrow spread => stronger confidence,
- wide spread => higher model uncertainty, requires more scrutiny.

---

## C4. Recommended Reporting Template

For each case, report:

1. Geometry and material setup summary.
2. Water and load scenario.
3. Search settings:
   - 2D: iterations/seed/slices
   - 3D: direction spacing/tolerance/solver settings
4. Method-wise FS table.
5. Convergence and warning table.
6. Interpretation note on spread.

---

## Part D: Expanded Math Notes by Method

## D1. 2D Bishop (Expanded)

Slice-level ingredients:

- base length `b_i` or equivalent arc length representation,
- slice base angle `alpha_i`,
- slice weight `W_i`,
- pore pressure force contribution `u_i * b_i`.

Iterative coupling source:

- effective normal depends on FS through equilibrium structure,
- therefore FS appears in denominator correction term.

Convergence behavior:

- stable for many practical slopes,
- sensitive to extreme pore pressure and very low shear strength combinations.

---

## D2. 2D Fellenius (Expanded)

Ordinary method neglects interslice shear in detailed equilibrium.

Implications:

- faster and simpler,
- often conservative relative to Bishop in similar setups.

In this code:

- explicit geometric and load calculations are used slice-by-slice,
- robust handling for invalid geometric slices is included (skip/continue path).

---

## D3. 3D Hungr-Bishop (Expanded)

Bishop-style 3D adaptation balances:

- directionally projected driving,
- friction-cohesion resisting with FS-coupled denominator.

Strength:

- numerically stable baseline for many 3D runs.

Weakness:

- approximation quality depends on chosen projection/column assumptions.

---

## D4. 3D Janbu Pair (Expanded)

Simplified Janbu:

- straightforward force-ratio.

Corrected Janbu:

- applies bounded correction to account for simplified bias.

Project note:

- correction formula is deterministic and intentionally bounded for stable behavior.

---

## D5. 3D Cheng-Yip Family (Expanded)

Why dual-track FS?

- 3D mechanics can be assessed from force and moment perspectives,
- mismatch between tracks indicates coupling inconsistency.

Spencer-like branch addresses this mismatch with lambda-coupled iteration.

Tradeoff:

- more coupling sophistication,
- potentially more sensitive convergence dynamics.

---

## Part E: Practical QA and Validation Methodology

## E1. 2D Validation Checklist

- same seed reproduces same circles,
- same circles fed into both methods,
- Bishop/Fellenius outputs deterministic for fixed seed/settings,
- water/load toggles move FS in expected direction,
- critical circle exists and is physically plausible.

---

## E2. 3D Validation Checklist

- each method returns direction result set,
- converged count > 0 for valid scenario,
- corrected variants not unexpectedly below simplified variant in controlled fixtures,
- Spencer-like mismatch diagnostics finite and bounded,
- reinforcement-off and reinforcement-on delta behaves monotonic in expected parameter sweeps.

---

## E3. Regression Strategy

For each stable test case:

1. Snapshot method outputs.
2. Snapshot convergence diagnostics.
3. Re-run after code changes.
4. Investigate any drift above tolerance band.

For stochastic workflows (2D circle generation):

- hold seed fixed in regression tests.

---

## Part F: Known Modeling Assumptions and Limits

1. 2D comparison uses circular slip family.
2. 3D methods rely on column-based representation.
3. Reinforcement in current 3D phase is simplified (no explicit intersection geometry).
4. Some corrected/coupled branches use bounded deterministic approximations for robustness.
5. Method outputs are engineering decision aids and should be interpreted with geotechnical judgment.

---

## Part G: Quick Crosswalk (Code to Method)

## G1. 2D

- Primary analyze endpoint returns Bishop (`/analyze`).
- Comparison result includes:
  - Bishop
  - Fellenius

Circle-sharing flow:

1. `run_comparison(iterations, seed)`
2. `_generate_candidate_circles(...)`
3. same list to Bishop + Fellenius evaluators

## G2. 3D

- `/api/v1/3d/analyze` => single `method_id`.
- `/api/v1/3d/analyze/multi` => clone base request and run selected IDs.
- normalization returns unified shape with diagnostics.

---

## Part H: Recommended Usage in Engineering Workflow

1. Start with 2D Bishop/Fellenius for fast sanity checks.
2. Move to 3D Hungr-Bishop or Janbu simplified for baseline.
3. Use corrected/coupled Cheng-Yip variants for robustness checks.
4. Review method spread and diagnostics.
5. If reinforcement is enabled, interpret gains as model-relative in current simplified phase.

---

## Part I: Suggested Future Enhancements

1. Add non-circular 2D slip search families.
2. Add publication-grade calibration for corrected factors.
3. Add full 3D explicit reinforcement intersection.
4. Add formal uncertainty bands across method families.
5. Add automated method-ranking diagnostics by convergence quality and stability.

---

## Part J: Final Summary

This project currently provides:

- one primary 2D analysis method (Bishop),
- one 2D comparison partner (Fellenius),
- seven 3D methods across Hungr and Cheng-Yip families.

The methodology emphasizes:

- reproducible comparisons (shared candidate sets in 2D),
- consistent canonical geometry state across methods (3D),
- transparent diagnostics and bounded approximations where needed.

For project decisions, always interpret FS together with:

- convergence,
- assumptions,
- method spread,
- scenario sensitivity.

