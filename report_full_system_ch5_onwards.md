# CHAPTER 5: METHODOLOGY (FULL CURRENT SYSTEM)

## 5.1 Methodology Overview

This document presents the methodology of the complete implemented system, covering:

- 2D slope stability analysis,
- 3D limit equilibrium analysis (7 methods),
- reinforcement-effect modeling,
- computational visualization workflow,
- **representative results** (Chapter 6),
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

### 5.3.1 2D Analysis Scope

The 2D workflow includes:

- Bishop-based primary analysis,
- Fellenius comparison on the same candidate slip-circle population,
- optional water and loading effects,
- practical reinforcement recommendation layer.

### 5.3.2 2D Inputs

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

### 5.3.3 Core Equilibrium Formulation

For slice-based evaluation:

$$
FS = \frac{\sum_i R_i}{\sum_i D_i}
$$

where:

- $R_i$ is resisting contribution of slice $i$,
- $D_i$ is driving contribution of slice $i$.

#### Fellenius (Ordinary Method of Slices)

$$
R_i = c'_i L_i + N'_i \tan\phi'_i
$$

$$
D_i = W_i \sin\alpha_i
$$

The ordinary method neglects detailed inter-slice force coupling, giving a simple but often conservative estimate.

#### Bishop Simplified (Iterative)

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

### 5.3.4 Shared Candidate-Circle Comparison

For fair comparison between Bishop and Fellenius:

1. A candidate circle set is generated once using:
   - the same `num_iterations`,
   - the same random seed.
2. The **same circle set** is used for both methods.
3. Minimum method-wise FS is reported.

This removes search-population bias and isolates method-equation differences.

### 5.3.5 Meaning of `num_iterations = 2000`

In this system, `num_iterations` refers to candidate slip-surface generation attempts (circle-search budget), not one single nonlinear loop for one equation.
This is different from solver-side iterative convergence used inside methods (for example Bishop-style fixed-point updates).

So with `2000`:

- up to ~2000 circle attempts are generated and filtered,
- both methods evaluate the same accepted circle population.

### 5.3.6 2D Reinforcement Recommendation Layer

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

### 5.4.1 Method Selection Guide (Engineering Context)

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

### 5.4.2 Family-Level Rationale

#### Hungr Suite (Methods 1–3)

- Intended for rapid global screening and optimization loops.
- Lower computational overhead than highly coupled alternatives.
- Well suited for identifying critical zones and candidate mechanisms before final verification.

#### Cheng–Yip Suite (Methods 4–7)

- Better suited to complex 3D geometry and richer inter-column behavior assumptions.
- Preferred where slope shape/material variation is irregular or highly non-uniform.
- Method 7 (Spencer-like) is best used as a final verification step.

### 5.4.3 3D Preprocessing Pipeline

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

### 5.4.4 Shared 3D Force Terms

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

### 5.4.5 Method 1: Hungr-Bishop

Direction-wise fixed-point iteration:

$$
FS_{k+1} = \frac{\sum_i(R_i/m_{\alpha,i})}{\sum_i D_i}
$$

$$
m_{\alpha,i} = \cos\alpha_i + \frac{\sin\alpha_i\tan\phi_i}{FS_k}
$$

### 5.4.6 Method 2: Hungr-Janbu Simplified

Force-equilibrium style:

$$
FS = \frac{\sum_i R_i}{\sum_i D_i}
$$

Engineering context:

- Fast and useful for translational trends.
- Can show conservative tendency compared to corrected/coupled methods.

### 5.4.7 Method 3: Hungr-Janbu Corrected

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

### 5.4.8 Methods 4-7: Cheng-Yip Family

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

### 5.4.9 Direction Search and Selection

For each candidate direction:

1. Solve method equations.
2. Check convergence.
3. Store diagnostics and FS.

Final FS is the minimum converged direction result.

### 5.4.10 Method-Specific Limitations

#### Hungr-Bishop (Method 1)

- Partial equilibrium formulation; may be less reliable for strongly translational mechanisms.
- Best interpreted for rotational-like behavior.

#### Hungr-Janbu Simplified (Method 2)

- May be conservative due to simplified force treatment.
- Useful for screening, not always ideal as sole final-design basis.

#### Hungr-Janbu Corrected (Method 3)

- Correction is model-form dependent and not universally exact.
- Improves simplified behavior but remains approximation-based.

#### Cheng–Yip Bishop-like / Janbu-like (Methods 4–5)

- Improved 3D handling but still branch-dependent (moment- or force-dominant assumptions).
- Convergence can degrade in highly irregular geometries.

#### Cheng–Yip Janbu-like Corrected (Method 6)

- Adds refinement over Method 5 but retains correction-model dependence.
- Should be cross-checked against Method 7 in critical cases.

#### Cheng–Yip Spencer-like (Method 7)

- Most coupled in the implemented method set.
- Higher computational demand and greater non-convergence sensitivity on difficult geometries.

### 5.4.11 General 3D LEM Limits (Current System)

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

### 5.6.1 Purpose

Visualization is used for interpretability of geometry and diagnostics, not as a substitute for engineering validation.

### 5.6.2 Visualization Data

The visualization workflow uses optional render data including:

- top-surface points,
- column geometric summaries (centers and vertical extents),
- per-column scalar field proxy (for heatmap),
- morphology tags (crest/face/toe metadata).

### 5.6.3 Layers

- point cloud / terrain mesh,
- slip geometry view,
- grid bounds,
- column centers and lines,
- prism view (with performance cap fallback),
- scalar heatmap,
- morphology overlay.

In practice, the scalar heatmap is used to show local safety-related indicators
(for example local FS proxies or local resisting-force intensity), helping identify potential weak zones in the 3D mass.

### 5.6.4 Performance Controls

- decimation for large scenes,
- prism-cap fallback,
- warning messages for disabled/degraded layers.

---

# CHAPTER 6: RESULTS (REPRESENTATIVE CASE STUDIES)

This section documents **illustrative outputs** from the implemented software for two deliberately “busy” models: a **layered 2D cross-section** with surface loads and a phreatic surface, and a **3D column-grid case** with a non-planar top surface, two strength models, a water level, and optional Phase-2 soil nails.  
All numeric values below were produced by **running the current project analysis code** in the development environment (fixed geometry and solver settings as stated). They are **not** independent field or laboratory validations; they demonstrate **system behavior and comparative trends**.

---

## 6.1 2D Case: Layering, Surcharge, Phreatic Surface, and Nail Design

### 6.1.1 Model definition (inputs)

| Item | Value |
|------|--------|
| Slope height $H$ | 14.0 m |
| Slope face angle | $40^\circ$ (horizontal length from geometry closure) |
| Slices | 35 |
| Candidate circles (search budget) | 800 (shared by Bishop and Fellenius) |
| Random seed (circle population) | 42 |
| **Layer 1** (0–3 m) | $\gamma = 19\ \mathrm{kN/m^3}$, $c' = 8\ \mathrm{kPa}$, $\phi' = 32^\circ$ (silty sand) |
| **Layer 2** (3–8 m) | $\gamma = 20\ \mathrm{kN/m^3}$, $c' = 15\ \mathrm{kPa}$, $\phi' = 28^\circ$ (stiff clay) |
| **Layer 3** (below 8 m) | $\gamma = 21\ \mathrm{kN/m^3}$, $c' = 5\ \mathrm{kPa}$, $\phi' = 38^\circ$ (dense sand) |
| UDL | 25 kPa from crest, horizontal extent 4 m, offset 2 m from crest |
| Line load | 120 kN/m at 4 m from crest |
| Phreatic surface | 2.5 m below the slope surface; $\gamma_w = 9.81\ \mathrm{kN/m^3}$ |

This configuration is intended to be **governed by water and loads** in the upper part of the profile while still differentiating the three strength layers.

### 6.1.2 2D limit equilibrium results (Bishop and Fellenius)

Both methods were evaluated on the **same** randomly generated set of trial circles (methodology in §5.3.4).

| Method | Global FS (minimum over shared circles) |
|--------|----------------------------------------|
| Bishop (simplified) | **0.874** |
| Fellenius (ordinary slices) | **0.384** |

The large gap is consistent with the ordinary method **neglecting** inter-slice normal-force transfer while Bishop **partially** includes it. For reporting: **Bishop** is the more accepted baseline here; Fellenius is reported as a **coarse, often conservative** comparator.

### 6.1.3 2D reinforcement (soil nail) **design** output

The 2D workflow includes a **practical soil-nail recommendation layer** driven by a target factor of safety and material/strength settings. It is **not** a full nail–slip surface intersection in the slice equilibrium; it provides **nail count, spacing, and diameter/length** consistent with a resistance shortfall.

Settings for this run:

- Reinforcement: **enabled**
- Target FS: **1.45**
- Steel yield: **500 MPa**
- Allowable bond (grout–soil): **85 kPa** (interface model parameter in the design helper)

**Reported design summary (abridged):**

- Current governing FS (from the PySlope-based Bishop run used for design): **0.874**
- Required tension reserve (normalized driving-force estimate): **$\Delta R \approx 991\ \mathrm{kN/m}$** (order of magnitude, per internal normalization)
- **Nail count and spacing (from the recommender):** **9** horizontal rows $\times$ **12** columns along the slope $\Rightarrow$ **108** nail positions on the assumed grid; **vertical spacing** **1.6 m**, **horizontal (along-face) spacing** **1.4 m**
- **Design tension per nail (initial split of $\Delta R$):** **$\approx 11.5\ \mathrm{kN}$** per nail before standard bar selection (see tool diagnostics for exact value)
- **Bar:** **12 mm** diameter (nearest standard size from required steel area)
- **Length (conceptual):** **12.0 m** total (free + bond + cover per simplified rules in the design routine)
- **Batter:** $15^\circ$ from horizontal (default in the recommender)

**Important distinction:** In **2D**, this block is **decision support** and reporting; the **Bishop and Fellenius numbers in §6.1.2** are the **unreinforced** LEM results on the same cross-section. In **3D**, the Phase-2 nail model **adds a resisting term inside** the limit equilibrium (see §6.2.3).

---

## 6.2 3D Case: Irregular top surface, two materials, water level, and nails

### 6.2.1 Model definition (inputs)

| Item | Value |
|------|--------|
| Plan extent | $x,y \in [0,2]\ \mathrm{m}$; vertical grid $z \in [0,22]\ \mathrm{m}$ |
| Column discretization | $5 \times 5$ → **25** active column bases after intersection (case-dependent) |
| Top surface | Nine sample points (non-planar “patch” DEM-style surface); bilinear-style interpolation on the structured grid (mode `a1` in the implementation) |
| Example corner elevations | $(0,0): 14.0\ \mathrm{m}$; $(2,0): 13.2\ \mathrm{m}$; $(0,2): 13.5\ \mathrm{m}$; $(2,2): 12.8\ \mathrm{m}$; interior/edge points between these |
| Slip surface | Ellipsoid, center $(1,1,10)$ m, semi-axes **(1.6, 1.6, 2.4) m** |
| Water | Phreatic elevation **$z = 11.0\ \mathrm{m}$** (constant head in current hydro setup) |
| **Governing material (homogeneous block)** | Mohr–Coulomb type 1: $\phi' = 30^\circ$, $c' = 5\ \mathrm{kPa}$, $\gamma = 18.5\ \mathrm{kN/m^3}$ (first entry in the materials map for this run) |
| Direction search | Spacing $1.0^\circ$, band $\pm 8.0^\circ$ (implementation defaults for this case) |
| Method solver | Max 200 FS iterations, tolerance $10^{-4}$ |

*Implementation note (materials map):* The request can carry **multiple** named `MaterialDefinition` entries; in the **current** 3D preprocessing path, strength is resolved from the **first** material in the mapping and applied **uniformly** to all valid columns. A second, stronger notional material was present in the input dictionary for this run but **does not** change the result until per-column or layered material assignment is extended. The case study therefore shows **varied 3D geometry and hydro** on a **single** strength model, which still exercises solvers, direction search, and nail terms honestly.

### 6.2.2 3D global FS — all seven methods (unreinforced)

**Phreatic surface at** $z = 11.0\ \mathrm{m}$**, nails disabled.**

| Method | Reported min FS over direction search |
|--------|--------------------------------------|
| 1 — Hungr-Bishop | **1.564** |
| 2 — Hungr-Janbu simplified | **1.644** |
| 3 — Hungr-Janbu corrected | **1.735** |
| 4 — Cheng–Yip Bishop-like | **1.462** |
| 5 — Cheng–Yip Janbu-like | **1.644** |
| 6 — Cheng–Yip Janbu-like corrected | **1.735** |
| 7 — Cheng–Yip Spencer-like | **1.559** |

These values are **not** interchangeable with the 2D numbers in §6.1: the **geometry, water model, and failure surface family** are different, and 3D methods **branch** on equilibrium assumptions (§5.4).

### 6.2.3 3D results with **Phase-2 simplified** soil nails (in-equilibrium term)

The same 3D model was re-run with **reinforcement enabled** using a **moderate** nail layout (intended to show a **finite FS gain** without dominating the problem):

- Bar diameter 25 mm, bond length 3.0 m, **nail installation angle** $10^\circ$ **from horizontal** (not to be confused with soil effective friction $\phi'$)  
- Spacing $2.0\ \mathrm{m} \times 2.0\ \mathrm{m}$; steel area $5\times 10^{-4}\ \mathrm{m^2}$; $f_y = 500\ \mathrm{MPa}$; bond strength 90 kPa (interface)

| Method | FS without nails | FS with Phase-2 nails |
|--------|------------------|------------------------|
| Hungr-Bishop (1) | 1.564 | **1.776** |
| Cheng–Yip Spencer-like (7) | 1.559 | **1.756** |

The increment reflects the **additive resisting contribution** in §5.5. The exact gain **depends strongly** on embedment, spacing, and bond—values here are **illustrative**. Very dense or strong nail schedules can produce **large** apparent FS in this simplified form; such outputs require **engineering judgment** and, where appropriate, **more rigorous** nail–wedge interaction models.

### 6.2.4 How to read these results

- **2D (§6.1):** Use Bishop vs Fellenius to separate **method equation** effects at fixed search budget; use the **nail design** block as **practical output**, not a third FS column unless a future release couples nails into the slice equations.
- **3D (§6.2):** Treat the seven **unreinforced** FS values as a **method suite comparison**; treat **nailed** FS as the **current Phase-2 model’s** response, clearly labeled as **simplified** (§5.5, §8.3).

### 6.3 Report figures: screenshot placeholders (replace before submission)

The following **six** figures are intended to support Chapter 6 in the final PDF or Word document. In each case, **delete the placeholder line** and **insert your exported image** (PNG or high-resolution JPEG). Keep the **figure number** and **caption** immediately below the image so cross-references stay clear.

> **Layout tip:** In Word, use *Insert → Picture* on the placeholder row; in LaTeX, replace each placeholder with `\includegraphics[width=\textwidth]{...}` and keep `\caption{...}` matching the text below.

| Fig. | What to capture | Suggested state before capture |
|------|-----------------|-------------------------------|
| **1** | 2D — **Visualizer** (left) + **Geometry** tab (right) | Same inputs as §6.1 (or very close). Run not required; clean canvas. |
| **2** | 2D — left **Results** (numeric FS, Bishop vs Fellenius) | After a successful **Run Analysis** for the §6.1 case. |
| **3** | 2D — left **Image** (server-generated diagram) | After run, when the tab is enabled. Omit only if the build never returns an image. |
| **4** | 3D — **Summary** (key FS and method for §6.2) | After **Run 3D Analysis** with settings matching §6.2. |
| **5** | 3D — **Preview** (scene: terrain, slip, optional heatmap/controls) | Same run as Fig. 4; enable layers as needed for a clear “3D result” view. |
| **6** | 2D — right tab **Results** (soil-nail **design** inputs: target FOS, steel, bond) | Matches §6.1.3 settings; shows reinforcement panel, not the left output tab. |

---

**[Insert image here — Figure 1]**

**Figure 1.** Two-dimensional web client: main **Visualizer** and **Geometry** tab with inputs consistent with the §6.1 case (slope height, face angle, length; layered profile, loads, and water entered on the other right-hand tabs as applicable).

---

**[Insert image here — Figure 2]**

**Figure 2.** Two-dimensional web client: left **Results** view after analysis — governing factor of safety and **Bishop** vs **Fellenius** comparison for the shared candidate-circle search (§6.1.2).

---

**[Insert image here — Figure 3]**

**Figure 3.** Two-dimensional web client: left **Image** tab showing the **server-generated** stability diagram (PNG) for the run corresponding to the §6.1 results, when available.

---

**[Insert image here — Figure 4]**

**Figure 4.** Three-dimensional web client: **Summary** (or equivalent primary output) after **Run 3D Analysis** for the §6.2 configuration — global FS, method identity, and status consistent with the tables in §6.2.2–6.2.3.

---

**[Insert image here — Figure 5]**

**Figure 5.** Three-dimensional web client: **Preview** — interactive scene showing **terrain mesh** (or points), **slip surface**, and optional **per-column scalar / heatmap** and scene controls, for the same §6.2 case as Figure 4.

---

**[Insert image here — Figure 6]**

**Figure 6.** Two-dimensional web client: right-hand tab labeled **Results** (reinforcement **design** inputs only) — **enable design**, **target FOS**, **steel yield**, and **soil–grout bond** aligned with §6.1.3 (distinct from the left **Results** output tab in Figure 2).

---

# CHAPTER 7: VALIDATION AND QA

## 7.1 Multi-Level Validation Strategy

1. Input schema and domain validation.
2. Unit tests for computational utilities and solvers.
3. Integration tests for full analysis workflows.
4. UI-level tests for payload mapping and core behavior.
5. Diagnostic consistency checks across methods.

## 7.2 2D Validation Focus

- geometry and material validation correctness,
- deterministic comparison behavior for fixed seed,
- stability classification consistency with FS thresholds,
- load/water sensitivity checks.

## 7.3 3D Validation Focus

- method-selection and multi-method execution behavior,
- invalid-input rejection and error envelope behavior,
- convergence and partial-failure handling,
- diagnostics structure and reporting consistency,
- reinforcement payload acceptance and effect reporting.

## 7.4 Visualization QA Focus

- adapter mapping consistency,
- fallback behavior for heavy/partial datasets,
- toggle behavior and warning visibility,
- heatmap shown only with valid scalar field.

## 7.5 Reproducibility Controls

- fixed random seed where applicable (2D comparison),
- explicit solver/search settings in request payload,
- persisted diagnostics for audit and re-check.

## 7.6 Recommended Final Submission QA Additions

1. Benchmark matrix (small/medium/large complexity cases).
2. Method spread table for 2D and 3D (see Chapter 6 for an example).
3. Sensitivity analysis for:
   - water level,
   - friction/cohesion,
   - reinforcement spacing/strength.
4. Runtime and stability profile for computational scenarios.

---

# CHAPTER 8: LIMITATIONS AND DEFERRED PHYSICS

## 8.1 2D Limitations

- Circular surface family dominates current comparison workflow.
- Fellenius omits full interslice force coupling.
- Reinforcement recommendation is practical guidance, not full structural detailing.

## 8.2 3D Methodological Limits

- Column-based representation is an approximation of continuum behavior.
- Corrected factors are deterministic bounded approximations in current stage.
- Direction resolution influences discovered critical direction.

## 8.3 Reinforcement Limits

- Current 3D reinforcement is phase-2 simplified.
- Full direction-aware explicit nail-slip intersection is deferred.

Hence reinforcement-driven FS improvement should be interpreted as model-relative.

## 8.4 Visualization Limits

- Heavy geometry may trigger decimation/fallback.
- Visual layers are diagnostic aids, not standalone proof of geomechanical adequacy.

## 8.5 Deferred Physics / Future Work

1. Full direction-aware 3D reinforcement intersection.
2. Further calibration of corrected/coupled method branches.
3. Expanded non-circular and advanced 3D failure families.
4. Uncertainty quantification and confidence band reporting.
5. Broader validated benchmark library.

---

# CHAPTER 9: CONCLUSION (FULL CURRENT SYSTEM)

The project now operates as a complete multi-method slope stability platform with:

- robust 2D analysis and Bishop/Fellenius comparison,
- modular 3D LEM implementation with seven methods,
- reinforcement effect modeling in both practical and 3D analytical workflows,
- diagnostic visualization for geometric and scalar interpretation,
- documented **representative case studies** (Chapter 6) tying inputs to numeric outputs.

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
3. Add Chapter 6 (Results), Chapter 7 (Validation/QA), Chapter 8 (Limitations), and Chapter 9 (Conclusion) from this file.
4. Keep methodology, case-study results, and QA consistent with implemented project behavior.
5. Insert screenshots at **§6.3** (Figures 1–6) and use **Appendix C** as the full UI/tab reference (optional extra figures C-1–C-4).

---

## Appendix C: Web user interface — tab structure, inputs, and figure guidance

The **primary report figures** for the B.Tech submission are **Figures 1–6** in **§6.3** (Chapter 6), with ready-made captions and a capture checklist. This appendix is the **narrative inventory** of all tabs and inputs; the optional **Figure C-1** / **C-2** naming below is an alternate minimal set if you need a short cross-reference in the methodology.

The production web client provides two full-page modes: **2D** (`/`) and **3D** (`/analysis-3d`). Each mode splits the main workspace into a **left** results/visualization region with its own **tab strip** and a **right** data-entry region with a **separate tab strip**. The subsections below list **every tab** and **all user-facing input fields** in text so the written report is complete even when only a few figures are included.

### Screenshot policy (as agreed for the report)

- **Do not** attach a separate figure for every tab on both pages; that is unnecessary for a formal report.
- **Do** include at least **one** clear screenshot per mode showing the overall layout. A practical default:
  - **2D:** left dock on **Visualizer**, right dock on the first input tab, **Geometry**, so the figure shows both the 2D canvas and slope dimensions (see **Figure C-1** placeholder below).
  - **3D:** one screenshot with a representative combination (for example **Preview** on the left and **Method** or **Surfaces** on the right) — **Figure C-2** placeholder.
- Optional extra figures: **2D** — left **Image** (generated diagram) or left **Results** (numeric table); **3D** — **Summary** or **Diagnostics** if you need to show output-heavy views in the appendix.

---

### C.1 Two-dimensional page (`/` — “Slope Stability Analyzer”)

**Chrome:** Application title, **Switch to 3D** link, **Run Analysis** control.

**Left column — main viewer (three tabs)**

| Tab | Role |
|-----|------|
| **Visualizer** | Interactive 2D sketch: slope profile, material bands, phreatic line when water is on, and external load schematics. |
| **Image** | Displays the **server-generated** stability diagram (PNG) after a run that returns image bytes; tab stays disabled until an image is available. |
| **Results** | Presents **numerical** results: minimum factor of safety, **Bishop vs Fellenius** comparison, loading and water summary, and **soil-nail design** text when reinforcement is active. |

**Right column — input (six tabs, left to right)**

1. **Geometry**  
   - **Height** (m)  
   - **Angle** (degrees)  
   - **Length** (m) — the backend accepts any **two** of the three to fix the third.

2. **Materials** (soil profile table)  
   - Per row: **name**, **unit weight** $\gamma$ (kN/m³), **friction angle** $\phi$ (°), **cohesion** $c$ (kPa), **depth to bottom** of layer (m; blank = effectively infinite in the UI).  
   - **Add layer** / **Remove** per row.

3. **Loads**  
   - **Uniform distributed loads (UDL):** for each entry — **magnitude** (kPa), **offset** from crest (m), **length** along the slope (m); add/remove.  
   - **Line loads:** each — **magnitude** (kN/m), **offset** from crest (m); add/remove.

4. **Water**  
   - **Enabled** (checkbox)  
   - **Depth** to phreatic surface below the slope top (m)  
   - **Water unit weight** (kN/m³)

5. **Settings**  
   - **Number of slices**  
   - **Iterations** (candidate slip-circle / search budget, not the sole Bishop inner loop count)  
   - **Tolerance** (numerical convergence in the 2D workflow)

6. **Results** *(tab name in the UI; content is 2D reinforcement design inputs)*  
   - **Enable design** (checkbox)  
   - **Target FOS**  
   - **Steel yield strength** (MPa)  
   - **Soil–grout bond friction** (kPa)

> **Naming note:** The right-hand tab labeled **Results** here drives **2D soil-nail *design* parameters**. The *left* tab **Results** shows **analysis output** after **Run Analysis**. The report text should not confuse the two.

**Suggested figure:** **Figure C-1** — 2D application, **Visualizer** + **Geometry** tab, with caption referencing the list above.

---

### C.2 Three-dimensional page (`/analysis-3d` — “3D Slope Analysis”)

**Chrome:** **Switch to 2D**, **Validate 3D Input**, **Run 3D Analysis** (single method) or **Run Multi-Method** (when **comparison** mode is on), and **Compare with/without nails** (visible when 3D reinforcement is enabled).

**Left column — output (five tabs)**

| Tab | Role |
|-----|------|
| **Summary** | Global FS, method identification, high-level status, “simplified reinforcement” notice when applicable, optional compare strip (with/without nails) after a compare run. |
| **Preview** | **Three.js** view: terrain mesh / points, slip surface, column centers, lines, prisms, morphology, FS heatmap overlay; scene controls and layer toggles. |
| **Comparison** | Table of factors of safety across selected methods (multi-method run). |
| **Diagnostics** | Convergence, direction search, hydro/strength messages, optional reinforcement and **render** diagnostics. |
| **Payload** | Last JSON request/response metadata (e.g. reinforcement model id, `include_render_geometry`). |

**Right column — input (seven tabs, left to right)**

1. **Method**  
   - **Method ID** (1–7); in **comparison** mode, checkboxes list full names: Hungr-Bishop, Hungr-Janbu (simplified/corrected), Cheng–Yip (Bishop-like, Janbu-like, Janbu-corrected, Spencer-like).  
   - **Solver:** max **iterations**, **FS tolerance**, **damping**.  
   - **Direction search:** **spacing** (°), **tolerance** (°), optional **user direction** (°).

2. **Grid**  
   - Bounds: **X min/max**, **Y min/max**, **Z min/max** (m)  
   - **Column counts** in $X$ and $Y$  
   - Read-only **projected** row count (for performance awareness)

3. **Slip surface**  
   - **Mode:** `ellipsoid` or `user_defined`  
   - *Ellipsoid:* center **Xc, Yc, Zc**; radii **Rx, Ry, Rz** (m)  
   - *User-defined:* **surface path** string, **interpolation** code

4. **Surfaces** (ground / top-surface)  
   - **Label**, file **path** string, **interpolation** mode  
   - Table of **X, Y, Z** points (add/remove, **Use demo surface**)  
   - Note in UI: full CSV upload may be marked deferred; manual points are the usual teaching path.

5. **Materials**  
   - Table: **name**, **model type** (integer 1–5), **unit weight**, **P1** / **P2** (for type 1 Mohr–Coulomb: **$\phi$** and **cohesion**; other types use undrained or extended parameters as implemented); add/remove materials.

6. **Hydro**  
   - **Water level** $z$ (m) or empty for no global phreatic level in the payload.

7. **Advanced**  
   - **Include analysis rows** (verbose row payload)  
   - **Include render geometry** (3D scene data)  
   - **Reinforcement** (3D Phase-2 simplified): **enabled**, **diameter**, **embed length**, **spacing** $S_x$, $S_y$, **steel area**, **yield strength**, **bond strength**, **inclination** (°), **vertical component** flag; **assumption** banner when enabled.

**Suggested figure:** **Figure C-2** — 3D application with one **left** output tab and one **right** input tab (your choice of combination), with caption listing which tabs are shown.

---

### C.3 List of figure placeholders (for the printed report)

| ID | Suggested content |
|----|-------------------|
| Figure C-1 | 2D: **Visualizer** + **Geometry** (minimum recommended). |
| Figure C-2 | 3D: e.g. **Preview** + **Method** or **Surfaces** (minimum recommended). |
| Figure C-3 *(optional)* | 2D **Image** or left **Results** after a successful analysis. |
| Figure C-4 *(optional)* | 3D **Summary** or **Diagnostics** or **Payload**. |

Replace placeholders with your actual captured images when you bind the final PDF.

