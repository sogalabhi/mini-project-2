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

## 5.4.1 Method Set

Implemented 3D method IDs:

1. Hungr-Bishop  
2. Hungr-Janbu Simplified  
3. Hungr-Janbu Corrected  
4. Cheng-Yip Bishop-like  
5. Cheng-Yip Janbu-like  
6. Cheng-Yip Janbu-like Corrected  
7. Cheng-Yip Spencer-like

## 5.4.2 3D Preprocessing Pipeline

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

## 5.4.3 Shared 3D Force Terms

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

## 5.4.4 Method 1: Hungr-Bishop

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

## 5.4.6 Method 3: Hungr-Janbu Corrected

$$
FS_{corr} = FS_{simp}\cdot C_j
$$

with bounded correction:

$$
C_j = 1 + 0.08\sin(\overline{dip}) + 0.05\tan(\overline{\phi}), \quad C_j \in [1.0,1.35]
$$

## 5.4.7 Methods 4-7: Cheng-Yip Family

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

## 5.4.8 Direction Search and Selection

For each candidate direction:

1. Solve method equations.
2. Check convergence.
3. Store diagnostics and FS.

Final FS is the minimum converged direction result.

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

