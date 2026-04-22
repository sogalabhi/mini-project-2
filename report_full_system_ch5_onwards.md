# CHAPTER 5: METHODOLOGY (FULL CURRENT SYSTEM)

## 5.1 Methodology Overview

This chapter presents the methodology of the complete implemented system, covering:

- 2D slope stability analysis,
- 3D limit equilibrium analysis (7 methods),
- reinforcement-effect modeling,
- computational visualization workflow,
- validation and QA strategy,
- limitations and deferred physics.

The implemented system combines:

- a computational core for engineering calculations,
- a user interface for input, analysis execution, and result interpretation,
- a 3D rendering workflow for geometric and diagnostic visualization.

---

## 5.2 End-to-End Computational Flow

### 5.2.1 Workflow Stages

1. Input definition: geometry, materials, loading, hydro conditions, and solver settings.
2. Input validation: schema-level and domain-level checks.
3. Analysis execution:
   - 2D computational path or
   - 3D computational path with method selection.
4. Result aggregation:
   - global safety indicators,
   - method diagnostics,
   - optional visualization data.
5. User-facing interpretation:
   - summary,
   - method comparison,
   - diagnostics,
   - visualization layers.

### 5.2.2 Methodology Principles

- Reproducibility for fixed settings.
- Transparent diagnostics.
- Practical engineering interpretability.
- Modular extensibility from 2D to 3D.

---

## 5.3 2D Methodology

## 5.3.1 2D Analysis Scope

The 2D workflow includes:

- Bishop-based primary analysis,
- Fellenius comparison on the same candidate slip-circle population,
- optional water and loading effects,
- practical reinforcement recommendation layer.

## 5.3.2 2D Inputs

- Slope geometry: height, angle, length (two given, one derived).
- Soil layering:
  - unit weight,
  - friction angle,
  - cohesion,
  - optional depth boundaries.
- External loads:
  - UDL,
  - line load.
- Water table:
  - depth and water unit weight.
- Numerical settings:
  - `num_slices`,
  - `num_iterations` (candidate search budget),
  - `tolerance`.

## 5.3.3 Core Equilibrium Formulation

For slice-based evaluation:

$$
FS = \frac{\sum_i R_i}{\sum_i D_i}
$$

where:

- $R_i$ is resisting contribution of slice $i$,
- $D_i$ is driving contribution of slice $i$.

### Fellenius (Ordinary Method of Slices)

$$
R_i = c'_i L_i + N'_i \tan\phi'_i
$$

$$
D_i = W_i \sin\alpha_i
$$

The ordinary method neglects detailed inter-slice force coupling, giving a simple but often conservative estimate.

### Bishop Simplified (Iterative)

$$
FS_{k+1} =
\frac{
\sum_i\left(\frac{c'_i b_i + (W_i-u_i b_i)\tan\phi'_i}{m_{\alpha,i}}\right)
}{
\sum_i (W_i\sin\alpha_i)
}
$$

$$
m_{\alpha,i} = \cos\alpha_i + \frac{\sin\alpha_i\tan\phi'_i}{FS_k}
$$

Because $FS$ appears on both sides, iterative convergence is required.

## 5.3.4 Shared Candidate-Circle Comparison

For fair comparison between Bishop and Fellenius:

1. A candidate circle set is generated once using:
   - the same `num_iterations`,
   - the same random seed.
2. The **same circle set** is used for both methods.
3. Minimum method-wise FS is reported.

This removes search-population bias and isolates method-equation differences.

## 5.3.5 Meaning of `num_iterations = 2000`

In this system, `num_iterations` refers to candidate slip-surface generation attempts (circle-search budget), not one single nonlinear loop for one equation.
This is different from solver-side iterative convergence used inside methods (for example Bishop-style fixed-point updates).

So with `2000`:

- up to ~2000 circle attempts are generated and filtered,
- both methods evaluate the same accepted circle population.

## 5.3.6 2D Reinforcement Recommendation Layer

When reinforcement settings are enabled, practical recommendations are derived from:

- current FS vs target FS,
- estimated additional resisting requirement,
- steel and bond assumptions,
- resulting nail count/spacing/length suggestions.

This output is decision-support guidance, not a full structural detailing module.

---

## 5.4 3D Methodology (7 Implemented Methods)

### 5.4.0 Implementation Origin and Adaptation Note

The 3D methodology in this project was developed with technical inspiration from the legacy open-source repository:

- [https://github.com/enokjun/2D-and-3D-LEM-Slope-Analysis-Python3/blob/master/3D_backend_analysis.py](https://github.com/enokjun/2D-and-3D-LEM-Slope-Analysis-Python3/blob/master/3D_backend_analysis.py)

That codebase is from an older software ecosystem (approximately 8 years old), and direct reuse was not practical because of major changes in:

- Python runtime behavior and language ecosystem,
- package/dependency versions and compatibility,
- modern project structure, testing, and integration requirements.

Therefore, this project does **not** directly copy the old implementation.  
Instead, the team used the legacy repository as conceptual/methodological reference and implemented a new 3D analysis system compatible with the current environment.

## 5.4.1 Method Selection Guide (Engineering Context)

The implemented 3D methods span simplified to strongly coupled equilibrium formulations.
Method selection is a trade-off between computational speed, numerical robustness, and equilibrium rigor.

| Method ID | Method | Classification | Best Used For | Practical Note |
|---|---|---|---|---|
| 1 | Hungr-Bishop | Moment-oriented | Initial 3D rotational screening | Stable and fast baseline |
| 2 | Hungr-Janbu Simplified | Force-oriented | Translational / planar tendencies | Conservative tendency in many cases |
| 3 | Hungr-Janbu Corrected | Force + correction | Non-circular/transitional failures | Uses correction factor to reduce simplified bias |
| 4 | Cheng-Yip Bishop-like | Moment-dominant | Curved 3D geometries | Enhanced geometric handling vs basic baseline |
| 5 | Cheng-Yip Janbu-like | Force-dominant | Irregular/deep-seated non-circular trends | Useful for force-dominant scenarios |
| 6 | Cheng-Yip Janbu-like Corrected | Force + correction | Refined non-circular design checks | Correction in Cheng-Yip framework |
| 7 | Cheng-Yip Spencer-like | Coupled force+moment | Final critical verification | Most coupled and computationally sensitive in current set |

## 5.4.2 Family-Level Rationale

### Hungr Suite (Methods 1–3)

- Intended for rapid global screening and optimization loops.
- Lower computational overhead than highly coupled alternatives.
- Well suited for identifying critical zones and candidate mechanisms before final verification.

### Cheng-Yip Suite (Methods 4–7)

- Better suited to complex 3D geometry and richer inter-column behavior assumptions.
- Preferred where slope shape/material variation is irregular or highly non-uniform.
- Method 7 (Spencer-like) is best used as a final verification step.

## 5.4.3 3D Preprocessing Pipeline

1. Parse and validate surface/slip/material/hydro definitions.
2. Build grid and active columns.
3. Compute slip intersection and geometric column states.
4. Assign strength and hydro attributes.
5. Build canonical per-column rows for solver dispatch.

Per-column canonical fields include:

- center coordinates,
- $z_{top}$ and $z_{bottom}$,
- base area and volume proxies,
- dip and dip-direction proxies,
- effective stress terms.

## 5.4.4 Shared 3D Force Terms

For each column $i$:

$$
R_i = c_iA_i + N_{\text{eff},i}\tan\phi_i
$$

$$
D_i = W_i\sin\alpha_i \cdot alignment_i
$$

$$
alignment_i = \max\left(0.2,\left|\cos(\theta-\beta_i)\right|\right)
$$

where:

- $\theta$: candidate movement direction,
- $\beta_i$: base dip direction.

Global method result is selected from direction-wise solutions (minimum converged FS).

## 5.4.5 Method 1: Hungr-Bishop

Direction-wise fixed-point iteration:

$$
FS_{k+1} = \frac{\sum_i(R_i/m_{\alpha,i})}{\sum_i D_i}
$$

$$
m_{\alpha,i} = \cos\alpha_i + \frac{\sin\alpha_i\tan\phi_i}{FS_k}
$$

## 5.4.5 Method 2: Hungr-Janbu Simplified

Force-equilibrium style:

$$
FS = \frac{\sum_i R_i}{\sum_i D_i}
$$

Engineering context:

- Fast and useful for translational trends.
- Can show conservative tendency compared to corrected/coupled methods.

## 5.4.7 Method 3: Hungr-Janbu Corrected

$$
FS_{corr} = FS_{simp}\cdot C_j
$$

with bounded correction:

$$
C_j = 1 + 0.08\sin(\overline{dip}) + 0.05\tan(\overline{\phi}), \quad C_j \in [1.0,1.35]
$$

where:

- $\overline{dip}$ is the area-weighted average base dip over the active slip mass,
- $\overline{\phi}$ is the area-weighted average friction angle over the same active slip mass.

## 5.4.8 Methods 4-7: Cheng-Yip Family

Unified framework tracks:

- $FS_{force}$,
- $FS_{moment}$.

Variant branches:

- Method 4: Bishop-like (moment-dominant),
- Method 5: Janbu-like (force-dominant),
- Method 6: Janbu-like corrected,
- Method 7: Spencer-like with lambda coupling.

For Spencer-like:

$$
mismatch = FS_{force} - FS_{moment}
$$

lambda is iteratively updated with bounds, step-control, and oscillation checks.

## 5.4.9 Direction Search and Selection

For each candidate direction:

1. Solve method equations.
2. Check convergence.
3. Store diagnostics and FS.

Final FS is the minimum converged direction result.

## 5.4.10 Method-Specific Limitations

### Method 1: Hungr-Bishop

- Partial equilibrium formulation; may be less reliable for strongly translational mechanisms.
- Best interpreted for rotational-like behavior.

### Method 2: Hungr-Janbu Simplified

- May be conservative due to simplified force treatment.
- Useful for screening, not always ideal as sole final-design basis.

### Method 3: Hungr-Janbu Corrected

- Correction is model-form dependent and not universally exact.
- Improves simplified behavior but remains approximation-based.

### Methods 4-5: Cheng-Yip Bishop-like / Janbu-like

- Improved 3D handling but still branch-dependent (moment- or force-dominant assumptions).
- Convergence can degrade in highly irregular geometries.

### Method 6: Cheng-Yip Janbu-like Corrected

- Adds refinement over Method 5 but retains correction-model dependence.
- Should be cross-checked against Method 7 in critical cases.

### Method 7: Cheng-Yip Spencer-like

- Most coupled in the implemented method set.
- Higher computational demand and greater non-convergence sensitivity on difficult geometries.

## 5.4.11 General 3D LEM Limits (Current System)

- Column-based LEM assumes rigid-body style failure mass behavior.
- Internal deformation modes are not explicitly modeled.
- Results are sensitive to direction-search resolution and grid discretization.
- Side-boundary effects can inflate FS in narrow domains; 2D sanity checks are recommended.

---

## 5.5 Reinforcement Effect Modeling (3D Phase-2 Simplified)

Current reinforcement contribution:

$$
T_y = A_s f_y, \quad
T_{bond} = \pi d L_{embed}\tau_{bond}, \quad
T_{max} = \min(T_y,T_{bond})
$$

$$
q_{nail} = \frac{T_{max}}{S_xS_y}, \quad
R_{nail,i} = q_{nail}A_{b,i}
$$

Updated resisting term:

$$
R_i = c_iA_i + N_{\text{eff},i}\tan\phi_i + R_{nail,i}
$$

Optional vertical coupling can modify normal-force proxy.

Important interpretation:

- This is a simplified engineering approximation in current phase,
- full explicit direction-aware nail-slip geometric intersection is deferred.
- reinforcement-induced FS gains should be interpreted as model-relative guidance in the current phase.

---

## 5.6 Visualization Methodology

## 5.6.1 Purpose

Visualization is used for interpretability of geometry and diagnostics, not as a substitute for engineering validation.

## 5.6.2 Visualization Data

The visualization workflow uses optional render data including:

- top-surface points,
- column geometric summaries (centers and vertical extents),
- per-column scalar field proxy (for heatmap),
- morphology tags (crest/face/toe metadata).

## 5.6.3 Layers

- point cloud / terrain mesh,
- slip geometry view,
- grid bounds,
- column centers and lines,
- prism view (with performance cap fallback),
- scalar heatmap,
- morphology overlay.

In practice, the scalar heatmap is used to show local safety-related indicators
(for example local FS proxies or local resisting-force intensity), helping identify potential weak zones in the 3D mass.

## 5.6.4 Performance Controls

- decimation for large scenes,
- prism-cap fallback,
- warning messages for disabled/degraded layers.

---

# CHAPTER 6: VALIDATION AND QA

## 6.1 Multi-Level Validation Strategy

1. Input schema and domain validation.
2. Unit tests for computational utilities and solvers.
3. Integration tests for full analysis workflows.
4. UI-level tests for payload mapping and core behavior.
5. Diagnostic consistency checks across methods.

## 6.2 2D Validation Focus

- geometry and material validation correctness,
- deterministic comparison behavior for fixed seed,
- stability classification consistency with FS thresholds,
- load/water sensitivity checks.

## 6.3 3D Validation Focus

- method-selection and multi-method execution behavior,
- invalid-input rejection and error envelope behavior,
- convergence and partial-failure handling,
- diagnostics structure and reporting consistency,
- reinforcement payload acceptance and effect reporting.

## 6.4 Visualization QA Focus

- adapter mapping consistency,
- fallback behavior for heavy/partial datasets,
- toggle behavior and warning visibility,
- heatmap shown only with valid scalar field.

## 6.5 Reproducibility Controls

- fixed random seed where applicable (2D comparison),
- explicit solver/search settings in request payload,
- persisted diagnostics for audit and re-check.

## 6.6 Recommended Final Submission QA Additions

1. Benchmark matrix (small/medium/large complexity cases).
2. Method spread table for 2D and 3D.
3. Sensitivity analysis for:
   - water level,
   - friction/cohesion,
   - reinforcement spacing/strength.
4. Runtime and stability profile for computational scenarios.

---

# CHAPTER 7: LIMITATIONS AND DEFERRED PHYSICS

## 7.1 2D Limitations

- Circular surface family dominates current comparison workflow.
- Fellenius omits full interslice force coupling.
- Reinforcement recommendation is practical guidance, not full structural detailing.

## 7.2 3D Methodological Limits

- Column-based representation is an approximation of continuum behavior.
- Corrected factors are deterministic bounded approximations in current stage.
- Direction resolution influences discovered critical direction.

## 7.3 Reinforcement Limits

- Current 3D reinforcement is phase-2 simplified.
- Full direction-aware explicit nail-slip intersection is deferred.

Hence reinforcement-driven FS improvement should be interpreted as model-relative.

## 7.4 Visualization Limits

- Heavy geometry may trigger decimation/fallback.
- Visual layers are diagnostic aids, not standalone proof of geomechanical adequacy.

## 7.5 Deferred Physics / Future Work

1. Full direction-aware 3D reinforcement intersection.
2. Further calibration of corrected/coupled method branches.
3. Expanded non-circular and advanced 3D failure families.
4. Uncertainty quantification and confidence band reporting.
5. Broader validated benchmark library.

---

# CHAPTER 8: CONCLUSION (FULL CURRENT SYSTEM)

The project now operates as a complete multi-method slope stability platform with:

- robust 2D analysis and Bishop/Fellenius comparison,
- modular 3D LEM implementation with seven methods,
- reinforcement effect modeling in both practical and 3D analytical workflows,
- diagnostic visualization for geometric and scalar interpretation.

Major outcomes:

- reproducible method-comparison workflows,
- clear diagnostic visibility for engineering interpretation,
- extensible computational architecture for future geotechnical enhancements.

The system is suitable for educational, pre-design, and research-oriented analysis use,
with transparent assumptions and clearly identified deferred physics.

---

## Appendix A: Method List

### 2D Methods

- Bishop
- Fellenius (Ordinary Method of Slices)

### 3D Methods

- Hungr-Bishop
- Hungr-Janbu Simplified
- Hungr-Janbu Corrected
- Cheng-Yip Bishop-like
- Cheng-Yip Janbu-like
- Cheng-Yip Janbu-like Corrected
- Cheng-Yip Spencer-like

---

## Appendix B: How to Merge with Existing Report

Suggested integration:

1. Keep Chapters 1-4 after correcting formula wording and scope.
2. Replace old Chapter 5 with this Chapter 5.
3. Add Chapters 6, 7, and 8 from this file.
4. Keep methodology and QA consistent with implemented project behavior.

