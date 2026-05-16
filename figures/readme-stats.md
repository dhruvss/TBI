# TSPO TBI Tracer Scoring — README (Stats & How to Read Them)

**Goal:** pick starting tracers (and guide modifications) that maximize **in-brain, specific signal** for **TBI imaging**, while remaining BBB-friendly and strongly engaging TSPO.  
All metrics are standardized to **z-scores** so different scales can be combined.

One-liner
A computational pipeline that develops analogs for AC-5216 (emapunil) for acute traumatic brain injury using human PET metrics, affinity, lipophilicity, and docking on a binding site in 18 kDa translocator protein TSPO, and develops a novel tracer that has higher clinical and simulation accuracy for detection and diagnosis of the condition. All metrics are converted to z-scores and combined with an acute-TBI weighting scheme to produce a single composite score per tracer or analog.

Research Process
The project began as an independent investigation into neuroimaging biomarkers. The original plan was to train an AI model to detect chronic traumatic encephalopathy from open-source MRI, but only ten usable scans were available, which made that direction statistically underpowered. The work therefore pivoted to molecular neuroscience with the goal of designing a PET radiotracer for acute TBI. Human PET metrics were extracted from the literature, inhibition constants were curated and standardized, and molecular docking simulations were added to create a cross-domain scoring framework. This framework was presented at the Science Mentorship Institute symposium. The current phase focuses on emapunil (AC-5216) as the lead scaffold and uses small, structure-guided R-group substitutions to generate analogs that can be docked, scored, and prioritized for synthesis and, if feasible, radiolabeling.

Current Status
Human PET metrics have been assembled for PK11195, DPA-713, PBR28, PBR06, PBR111, GE-180, AC-5216, and DAA1106 with emphasis on HAB genotype and whole-brain or global regions where available. Metrics include VT, BPND, VND, fP, and VT over fP. Ki values are standardized to pKi, and lipophilicity is captured as logD7.4. AutoDock Vina docking against a consistent TSPO receptor model provides comparative binding energies. Each metric is converted to a z-score across the set, directions are aligned so higher is always better, and a composite score is computed with acute-TBI weights. Focused enumeration around AC-5216 generates 3D analogs that are converted to PDBQT, docked, merged into the scoring table, and visualized as leaderboards, per-parameter z heatmaps, engagement sanity plots, and delta plots relative to AC-5216.

KEY OUTCOMES
AC-5216 is the most favorable starting scaffold under acute-TBI priorities. Multiple benzyl para-substitutions at R1 and small N-alkyl or fluoroalkyl substitutions at R2 produce positive improvements over AC-5216 in the composite score while remaining near central nervous system property windows for molecular weight, polarity, and lipophilicity.

Statistical Normalization And Composite Score
For each metric a z-score is computed across the current set of tracers and analogs using the sample mean and population standard deviation estimator. For metrics where lower raw values denote improvement such as docking energy and VND, values are inverted before or after z-scoring so that all final z-scores follow the convention that higher is better. For lipophilicity the deviation from the target is computed as negative absolute difference between logD7.4 and two point seven and that deviation is z-scored, which favors molecules near the center of the central nervous system window rather than those that are simply more lipophilic. The composite Score_TBI is an NA-safe weighted mean of the per-parameter z-scores. If some metrics are missing for a given tracer or analog, weights are renormalized over the metrics that are present so that the score remains comparable without imputing values.

Acute TBI Weights
The per-parameter weights sum to one. BPND equals 0.32. VT over fP equals 0.18. VT equals 0.08. VND inverse equals 0.05. Docking equals 0.20. pKi equals 0.10. logD closeness equals 0.05. fP equals 0.02. K1 equals 0.00. The rationale is that acute TBI presents variable blood–brain barrier permeability, so lipophilicity and plasma free fraction are de-emphasized while specific PET signal and biochemical engagement receive higher emphasis. K1 is excluded to avoid confounding from barrier leakage.

Reproducibility
Enumeration scripts generate analogs of AC-5216 by substituting fragments at the benzyl position and at the lactam nitrogen. The enumerator writes individual SDF files and a properties table. Open Babel converts SDF files to PDBQT. AutoDock Vina performs docking against a fixed TSPO grid and writes results to a round-tagged CSV. The scoring script reads the authoritative pet_physchem.csv and pet_metrics.csv, merges docking energies from the current round, computes per-parameter z-scores with aligned directions, applies the acute weights, and writes figures and scored tables to the figures directory. Each run appends a score_history.csv to track progress across rounds. Using consistent docking parameters and a fixed receptor model preserves comparability across rounds.

Visualization Outputs
Leaderboards are saved as images sorted by the composite Score_TBI and provide a direct ranking for decision making. Z-score heatmaps present labeled per-parameter z-scores allowing rapid diagnosis of which properties drive improvements or regressions. Scatter plots of pKi versus docking energy provide a sanity check on target engagement. Delta plots relative to AC-5216 quantify the magnitude of improvement for each analog in the current round. Scored CSVs contain raw metrics, per-parameter z-scores, and the composite score to support auditing and downstream analysis.

## Metric cheat-sheet (what, units, direction, why better, better for)

- **Docking energy**
  - **Units & conversions:** kcal/mol (if kJ/mol → **÷ 4.184**).
  - **Direction:** **More negative is better** → we use **`z_DOCK_BEN = −z(energy)`**.
  - **Why better:** predicts stronger, more stable TSPO binding.
  - **Better for:** **pre-screening** candidates before synthesis; **ranking modifications**.

- **Ki → pKi**
  - **Units & conversions (Ki):** nM (µM → **×1000** to nM; pM → **÷1000** to nM).
  - **Transform:** **`pKi = 9 − log10(Ki_nM)`** (higher pKi = tighter affinity at tracer doses).
  - **Direction:** **Higher pKi is better** → `z_PKI = z(pKi)`.
  - **Why better:** higher target occupancy at microdoses without mass effects.
  - **Better for:** **target engagement** confidence; comparing to docking.

- **VT** (total distribution volume)
  - **Units:** mL/cm³ (same numeric as mL/mL).
  - **Direction:** **Higher is better** → `z_VT`.
  - **Why better:** more brain uptake; contributes to image contrast.
  - **Better for:** **overall in-brain signal**.

- **BPND** (specific binding vs non-displaceable)
  - **Units:** unitless.
  - **Direction:** **Higher is better** → `z_BPND`.
  - **Why better:** cleaner **specific** signal (less background).
  - **Better for:** **image contrast** and **group differences** in TBI.

- **VND** (non-displaceable volume)
  - **Units:** mL/cm³.
  - **Direction:** **Lower is better** → we use **`z_VND_inv = z(−VND)`**.
  - **Why better:** less nonspecific background.
  - **Better for:** **SNR** and robustness to partial-volume/noise.

- **fP** (plasma free fraction)
  - **Units & conversions:** fraction 0–1 (if % → **÷100**).
  - **Direction:** **Higher is better** → `z_FP`.
  - **Why better:** more bioavailable tracer to enter brain/tissue.
  - **Better for:** delivery/availability; normalizing VT (see VT/fP).

- **VT/fP** (availability-normalized distribution)
  - **Units:** mL/cm³ divided by fraction (report as given).
  - **Direction:** **Higher is better** → `z_VT_OVER_FP`.
  - **Why better:** discounts plasma binding, closer to tissue-level signal.
  - **Better for:** **cross-tracer comparability** of signal.

- **logD7.4** (lipophilicity, BBB-relevant)
  - **Units:** log10 (unitless).
  - **Target:** sweet spot ~**2.5–3.0** (we use **2.7** as default center).
  - **Direction:** **Closer to target is better** → `z_LOGD_CLOSE = z(−|logD − 2.7|)`.
  - **Why better:** balances BBB penetration vs nonspecific stickiness/efflux.
  - **Better for:** **BBB suitability** under **chronic/mild TBI**; tune down for **acute** (leaky BBB).

- **K1** (optional; delivery/flow)
  - **Units:** mL/cm³/min (sometimes min⁻¹; keep consistent within your file).
  - **Direction:** **Higher is better** → `z_K1`.
  - **Why better:** faster delivery under intact BBB; note acute TBI can inflate K1 via leakage.
  - **Better for:** **chronic/mild TBI** protocols; usually low weight.

---

## How each metric affects the overall score (at a glance)
- **Increases score:** higher **BPND**, **VT/fP**, **VT**, **fP**, **pKi**, **logD closeness**, **K1**; **more negative docking energy**; **lower VND** (via inversion).
- **Decreases score:** the opposite directions (e.g., low BPND, far-from-target logD, weak docking, high VND).

> **Tip:** If you change the tracer set, means/SDs change → z-scores and ranks can shift. Keep weights the same to compare runs.

---

## Unit quick-conversions (handy)
- kJ/mol → kcal/mol: **÷ 4.184**  
- µM → nM: **× 1000**  
- pM → nM: **÷ 1000**  
- % → fraction: **÷ 100**

---

## Where this helps most
- **Design & triage:** prioritize modifications with **better docking**/**pKi** *and* **in-vivo-relevant PET profile**.  
- **TBI context:**  
  - **Chronic/mild:** keep **logD closeness** and **fP** in play (BBB matters).  
  - **Acute:** down-weight **logD closeness**; emphasize **BPND/VT/fP** and **docking**.

Summary Of Rationale
Acute traumatic brain injury introduces uncertainty in barrier integrity, so the scoring system favors specific binding measures and direct target engagement while limiting reliance on blood–brain barrier proxies that may be misleading in the acute window. The enumeration approach preserves the emapunil pharmacophore and explores solvent-exposed benzyl chemistry and small nitrogen substituents that modulate docking, pKi, and logD7.4 without inflating molecular weight or polar surface area and while preserving positions that allow late-stage radiolabeling.


