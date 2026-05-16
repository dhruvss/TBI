# Research Journal
AI-Driven Novel Fluorinated TSPO Tracers for High-Accuracy TBI Diagnostics

## Entry 1 — Initial Research Question

**Date:** 3/20/25

**Original Research Question:**  
Is there a biomarker that can be discovered either as a functional neuroanatomical area of the brain or as a blood/tissue based biomarker that can give us a definitive diagnosis of chronic traumatic encephalopathy? How do we use such a biomarker to detect CTE early?

---

## Entry 2 — CTE Case Definition and Background

**Date:** 3/22/25

**CTE Case Definition**

| **Psychological Symptoms** | **Neurodegenerative Symptoms** |
| --- | --- |
| Clinical features:
• impairments in mood (i.e. suicidal tendencies, irritability, depression)
• behavior (impulsivity, explosivity)
• cognition (impaired memory, exec. function, loss of concentration)
• motor function (parkinsonism, gait ataxia) | • tauopathy characterized by neurofibrillary tangles, tau-positive astrocytes, and tau-positive cell processes
• amyloid beta plaques near the brain stem
• perivascular - sulci and cortical areas on the outside - causes neurodegeneration in the **youngest** layers of the brain
• occurs in particular at the dura mater and arachnoid mater evident in fMRIs
• **can be distinguished from other tauopathies like Alzheimer’s, Guamanian Parkinsonism Dementia Complex, age-related cognitive decline** |

Halicki Study

- amyloid-ß analyzed as a possible biomarker for CTE
- retrospective autopsy cohort
- 44% with diffuse amyloid plaques
- 10% meeting criteria for early-onset Alzheimer’s disease
- 114 brains analyzed with staged pathology including aß, APOE4, neuritic/dendritic plaques

Possible biomarkers identified in early review:

- Lewy bodies  
- Total tau / hyperphosphorylated tau  
- Tau-related aggregates (NFTs, plaques)  
- Amyloid-ß (diffuse vs neuritic)  
- APOE4  

---

## Entry 3 — MRI-Based Investigation

**Date:** 3/30/25

**Objective:**  
Evaluate whether functional neuroanatomical MRI features could serve as a primary or early biomarker for CTE.

**Markers evaluated:**
- Microhemorrhages (SWI)
- Cavum Septum Pellucidum (CSP)
- Frontal sulcal widening
- Global cortical atrophy
- Evans index ≥ 0.30

(CTE staging table and conclusions recorded previously retained unchanged.)


## Entry 4 — Segmentation and Radiomics Attempts

**Dates:** 4/20/25 – 4/28/25

**Pipelines tested:**
- SWIN-UNETR-BTCV (MONAI bundle)
- wholeBrainSeg UNeSt
- FASTSurfer radiomics segmentation

I used these pipelines as they were premier skull-stripping applications where I was able to visualize structural lesions and identify flortaucipir tau PET and amyloid PET activity.

**Errors and termination:**
- MONAI bundle dependency failures
- UNeSt blockify divisibility and convolution mismatches
- FASTSurfer completed but insufficient data volume limited statistical power

## Entry 5 — Data Limitation

**Date:** 6/15/25

- Final MRI dataset: 10 scans
- ADNI datasets not suitable for CTE-specific analysis
- Imaging-only pathway terminated

## Entry 6 — Pivot to Molecular Biomarkers
Research Process
The project began as an independent investigation into neuroimaging biomarkers. The original plan was to train an AI model to detect chronic traumatic encephalopathy from open-source MRI, but only ten usable scans were available, which made that direction statistically underpowered. The work therefore pivoted to molecular and cellular neuroscience with the goal of designing a PET radiotracer for acute TBI. Human PET metrics were extracted from the literature, inhibition constants were procured and standardized, and molecular docking simulations were added to create a z-score framework. I would like to focus on using small, structure-guided R-group substitutions to generate analogs that can be docked, scored, and prioritized for synthesis and, if feasible, radiolabeling.

MAIN HYPOTHESIS FOR THIS ENTIRE PROJECT: Halogenation/fluorination 

**Date:** 6/16/25

**New project scope:**  
Shift from chronic CTE imaging to **acute traumatic brain injury molecular imaging**.

**Candidate biomarker classes considered - acute TBI:**
- Neurofilament light (NfL)
- GFAP
- TSPO (18 kDa translocator protein)


## Entry 7 — Literature Review Phase: Biomarker Selection

**Dates:** 6/15/25 – 11/23/25

### Fluid Biomarker Review and Comparative Analysis

**NfL**
- NfL was originally going to be the top choice for biomarker - being considered a premier axonal neurodegeneration marker, and was involved in the cytoskeleton in 

**GFAP**
- Astroglial injury marker (reactive astrogliosis)
- Peaks ~20–24 hours post-injury
- Blood-based concentration only - there are no modes of analysis for pharmacokinetics such as tissue concs and plasma concs, hence blood tests can be invented but PET imaging takes a hit when it comes to this marker (typically, LPs are needed for this application)

**TSPO**
- clear acute --> subacute --> chronic signaling patterns
- radiotracer backbones available and clear neuroinflammation upregulation
- analyzable in PET imaging, there in brain tissue as it is an intracellular mitochondrial protein upregulated in mitochondrial rupture (TBI lesion pathology??)
- con: TBI pathology strength in neuroinflammation is more auxiliary, while upregulated compared to markers like NfL and GFAP

- Due to these considerations, TSPO had the best PET radioligand design potential, being directly analyzable in PET imaging, containing upregulation across multiple pharmacokinetic compartments, and had a clear acute-->subacute-->chronic upregulation pattern across glial cells which were reviewed by current literature.

**Key papers reviewed:**
- Caplan, H. W., Cardenas, F., Gudenkauf, F., Zelnick, P., Xue, H., Cox, C. S., & Bedi, S. S. (2020). Spatiotemporal Distribution of Microglia After Traumatic Brain Injury in Male Mice. ASN neuro, 12, 1759091420911770. https://doi.org/10.1177/1759091420911770
- Central Nervous System Radiotracer Development (TE‑2052). Radiotracers for PET and SPECT imaging of CNS targets implicated in neuropsychiatric disorders. International Atomic Energy Agency, TE-2052; 2022.
- Delage, C., Vignal, N., Guerin, C. et al. From positron emission tomography to cell analysis of the 18-kDa Translocator Protein in mild traumatic brain injury. Sci Rep 11, 24009 (2021). https://doi.org/10.1038/s41598-021-03416-3
- Ramlackhansingh AF, Brooks DJ, Greenwood RJ, Bose SK, Turkheimer FE, Kinnunen KM, Gentleman S, Heckemann RA, Gunanayagam K, Gelosa G, Sharp DJ. Inflammation after trauma: microglial activation and traumatic brain injury. Ann Neurol. 2011 Sep;70(3):374-83. doi: 10.1002/ana.22455. Epub 2011 Jun 27. PMID: 21710619.
- Neil S. N. Graham et al.
 ,Axonal marker neurofilament light predicts long-term outcomes and progressive neurodegeneration after traumatic brain injury.Sci. Transl. Med.13,eabg9922(2021).DOI:10.1126/scitranslmed.abg9922
- Israel, I., Ohsiek, A., Al-Momani, E. et al. Combined [18F]DPA-714 micro-positron emission tomography and autoradiography imaging of microglia activation after closed head injury in mice. J Neuroinflammation 13, 140 (2016). https://doi.org/10.1186/s12974-016-0604-9
- Alderson, P., & Roberts, I. (2005). Corticosteroids for acute traumatic brain injury. The Cochrane database of systematic reviews, 2005(1), CD000196. https://doi.org/10.1002/14651858.CD000196.pub2
- Pike V. W. (2009). PET radiotracers: crossing the blood-brain barrier and surviving metabolism. Trends in pharmacological sciences, 30(8), 431–440. https://doi.org/10.1016/j.tips.2009.05.005

**Findings from Ramlackhansingh et al.:**
- TSPO PET signal increases after TBI
- Distinct timepoints for upregulation:
  - Acute: early microglial activation
  - Subacute: sustained inflammation
  - Chronic: persistent neuroinflammatory signal years after injury
- TSPO upregulation observed even in regions remote from primary injury

**Conclusion of literature review:**
- TSPO uniquely spans acute, subacute, and chronic phases
- Provides spatially resolved signal
- Directly targetable by PET radiotracers
- Selected as final biomarker for computational tracer design

Pipeline Definitions - realized what I wanted to do with the pipeline - start off with currently available PET TSPO tracers, figure what is best for enumeration-based modifications (RDkit)
**IAEA** Framework for PK-Sim simulations and CNS multi-parametric optimization, inspired workflow for final tracer statistical analysis

## Entry 8 — Literature Curation for Ki, logD7.4, and Related Parameters

**Dates:** 6/15/25 – 11/23/25

**9/23/25** update: hypothesis - develop fluorinated PET tracers as fluorination is a common organic synthesis-drug discovery method 

**Purpose** I wanted to collect data for currently available reference TSPO tracers used in PET imaging, and wanted to check which tracers have suitable parameters for a sufficient z-score normalization integrating PET metric, physicochemical params, human tissue compartment stats, and structural docking energies (manual analysis done).

**Parameters collected:**
- Ki (nM) from in vitro binding assays in discussion sections of papers
- logD7.4 (measured or reported) from literature
- HAB ratio (high-affinity binding ratio) - not normalized, not included - external stat for validation
- Tissue extraction method
- Species HUMAN - specified, only human data used for clinical effectiveness
- Source reliability notes (Sokias et al. for emapunil was a calculated val)
- NOTE: logD7.4 for AC5216 was calculated from evidence in Sokias et al. - "12.6-fold loss in KI for HABs compared to the LAB Ki of 30.3" - extrapolated to 30.3/12.6 showing 2.4 as Ki in HAB concentrations - HAB was the primary measurement for all tracer Ki levels.
- NOTE: PBR111 and DAA1106 have no listed logD - hence normalized with a 0 value in z score pipeline, SD computed from other params.

Systematic Review - neurosci.cn - Brust et al. 

**Raw reference table excerpt (verbatim format):**

Ki_ref,logD_ref
Owen et al. (2011),Pike, 2009; Shah et al., 1994; Zhang et al. 2021
Owen et al. (2011),Boutin et al. 2007
Owen et al. (2011),Imaizumi et al. 2009
Chau et al. (2015),Wadsworth et al., 2012; Wickström et al., 2014
Sokias et al. (2017) - calculated value,Zhang et al. 2021
Owen et al. (2011),NA
Owen et al. (2011),Imaizumi et al. 2009
Owen et al. (2011),NA

## Entry 9 - Z-score normalization pipeline
Z-score normalization was the primary statistical method used for elucidating what currently available PET tracer can evaluate molecular inflammation in TBI the best through physicochemical parameters (listed below) with statistical weighting, docking energies estimated through Autodock Vina, and PET metrics extracted from literature with weights manually assumed based on consensus principles in PET tracer development from Lammertsma et al. and Innis et al.

**Acute-TBI composite weights (recorded):**
Weighting is a heuristic according to these values, framework for prioritization derived from: Adriaan A. Lammertsma, "Basic Principles of Tracer Kinetic Modelling" Department of Nuclear Medicine & PET Research, VU University Medical Center, Amsterdam, The Netherlands and Peter Brust, et al. 2015, neurosci.cn
- BPND: 0.32 - Innis et al.
- VT/fP: 0.18 - Basic Principles of Tracer Kinetic Modelling
- VT: 0.08 - Basic Principles of Tracer Kinetic Modelling
- VND inverse: 0.05 - Innis et al.
- Docking: -0.20 (according to directional changes - the more negative the better) - Autodock Vina
- pKi: 0.10 - other literature - -log(Ki) = pKi, Ki literature - listed. 
- logD closeness: 0.05 - IAEA TECDOC-2052 framework
- fP: 0.02 - Zoghbi, S. S., Anderson, K. B., Jenko, K. J., Luckenbaugh, D. A., Innis, R. B., & Pike, V. W. (2012). On quantitative relationships between drug-like compound lipophilicity and plasma free fraction in monkey and human. Journal of pharmaceutical sciences, 101(3), 1028–1039. https://doi.org/10.1002/jps.22822 - linear regression scale
- K1: 0.00 - PET kinetic rate constant

**Direction rules (carried forward):**
- Docking: \(Z_{dock} = -Z_{energy}\) (more negative energy = better)
- VND: \(Z_{VND\_inv} = Z(-VND)\)
- logD: \(Z_{logD\_close}\) from deviation-to-ideal transform above

**NOTE** Directionally corrected frameworks are used - refined z-table shows the corrected results due to these direction rules. Otherwise, the raw data was originally not corrected for these directional changes. 

**Recorded decision basis (as implemented in the scoring framework):**
- Chosen as the scaffold that performed consistently under standardized comparisons and had suitable literature/chemical support for:
  - TSPO engagement (Ki/pKi where available)
  - CNS suitability signals (logD window behavior + proxy metrics)
  - Practical feasibility for systematic analog generation (clear R1/R2 attachment logic used later)

**Disclaimer: Statistical normalization, weighting strategy, and error auditing for the tracer prioritization pipeline were developed using R (version 4.5.1) with error assistance from an AI large language model (ChatGPT, OpenAI). All final computations, data handling, and results were independently executed and verified by the author (me).**

AI prompt: "please design a z-score normalization for parameters BPND, VT, fP, VND inverse, docking energies (extracted from Vina), Ki and logD7.4 prioritizing BPND and other PET metrics, make it through R 4.5.1"

### normalization of all properties to original parameter of TSPO-upregulated control specimens with standardized metrics
keep_row <- function(cond) if (is.na(cond)) TRUE else !str_detect(cond, "(?i)\\bMS\\b|^ms_")
metrics_f <- metrics %>%
  filter(keep_row(condition)) %>%
  mutate(
    geno_rank = case_when(toupper(coalesce(genotype,""))=="HAB" ~ 1L, TRUE ~ 2L), # nolint
    region_rank = case_when(
      is.na(region) ~ 5L,
      region %in% c("global_mean","whole_brain") ~ 1L,
      region %in% c("mean_of_10_rois") ~ 2L,
      region %in% c("frontal_cortex","frontal","cortex") ~ 3L,
      TRUE ~ 4L
    ),
    value = suppressWarnings(as.numeric(value))
  ) %>% drop_na(value)

metrics_pick <- metrics_f %>%
  arrange(tracer_c, metric, geno_rank, region_rank) %>%
  group_by(tracer_c, metric) %>%
  slice(1) %>% ungroup() %>%
  select(tracer_c, metric, value)
ok("selected per-tracer metrics")
**ERROR** intermediate CSV outputs for missing or inconsistent values - normalized accordingly, as there were a few PET metrics that were missing in the original analysis - these are highlighted in the heatmap for missing VND and fP most commonly.
### physicochemical properties normalization
physchem_pick <- physchem %>%
  transmute(
    tracer_c,
    mean_Ki_nM = suppressWarnings(as.numeric(mean_Ki_nM)),
    logD7.4    = suppressWarnings(as.numeric(`logD7.4`))
  ) %>% distinct(tracer_c, .keep_all = TRUE)

### docking energy normalization
dock_pick <- dock %>%
  transmute(tracer_c, energy = suppressWarnings(as.numeric(energy))) %>%
  group_by(tracer_c) %>% slice(1) %>% ungroup()

wide <- full_join(
          physchem_pick,
          pivot_wider(metrics_pick, names_from = metric, values_from = value),
          by = "tracer_c"
        ) %>% full_join(dock_pick, by = "tracer_c")

study_tracers <- c("PK11195","DPA-713","PBR28","PBR06","PBR111","GE-180","AC-5216","DAA1106")
wide <- wide %>% filter(tracer_c %in% study_tracers)

### normalizing fP to percentage values
if("fP" %in% names(wide) && any(!is.na(wide$fP))){
  if(max(wide$fP, na.rm = TRUE) > 1 && max(wide$fP, na.rm = TRUE) <= 100){
    wide <- wide %>% mutate(fP = fP/100)
  }
}
ok(paste("built wide table with", nrow(wide), "tracers"))

### total z score normalization protocol
zify <- function(x){
  if (all(is.na(x)) || is.na(sd(x, na.rm=TRUE)) || sd(x, na.rm=TRUE)==0) rep(NA_real_, length(x)) else as.numeric(scale(x))
}
mutate(
    log10Ki    = if_else(!is.na(mean_Ki_nM), log10(mean_Ki_nM), NA_real_),
    z_Ki_inv   = zify(-log10Ki),
    z_VT       = zify(VT),
    z_BPND     = zify(BPND),
    z_VND_inv  = zify(-VND),
    z_fP       = zify(fP),
    z_VT_over_fP = zify(VT_over_fP),
    z_logD     = zify(logD7.4),
    z_dock_inv = zify(-energy)
  )

z_cols <- c("z_Ki_inv","z_VT","z_BPND","z_VND_inv","z_fP","z_VT_over_fP","z_logD","z_dock_inv")

**NOTE** DAA1106 was originally part of the tracer table in the z-score normalization process, but was excluded from the protocol, due to statistically significant amounts of missing PET metric data that couldn't be accomplished through thorough literature searches. Because of this, DAA1106 didn't make the cut to this step in the research process.

**NOTE** In figures, K1 was used as a supplementary measure, however was not part of the overall z-score normalization, due to the emphasis on logD7.4 measurements for BBB permeability, and was also excluded due to insufficient data.

**NOTE** Raw aggregated scores used a different scoring model (raw data in data_analysis dir) and reflects an aggregate score rather than a granular, detailed account. The second scoring model used (refined_z_table.csv) reflects the true values per parameter and all figures are based on those values. This scoring model is directional-corrected, and reflects the true z-scored values.

# Entry 10 - Enumeration Protocols 

**Dates:**  
- Round 1: 11/23/25  
- Round 2: 11/24–11/27/25  
- Round 3: 11/28/25  

**Purpose:**  
Generate a chemically valid, synthesis potential, and TSPO-relevant ligand library from the AC-5216 scaffold using controlled, round-specific enumeration strategies.

**General Functional Group/Mod Rationale**
Fluorination framework: Trifluoromethyl ethers – synthesis and properties of an unusual substituent, Frédéric R. Leroux, et al. , Beilstein J. Org. Chem. 2008
General functional group ideation: Viviano, M. et al. (2022). Essential Principles and Recent Progress in the Development of TSPO PET Ligands for Neuroinflammation Imaging. Current medicinal chemistry, Haranahalli, K., Honda, T., & Ojima, I. (2019). Journal of fluorine chemistry
- Defined modification system based on three functional groups
    **R1** - the tertiary amide nitrogen between the N-benzyl and ethyl groups which tunes lipophilicity according to specific fluorinations and alkyl additions 
    **R2** - terminal benzyl group that toggles hydrophobicity as according to the prepped TSPO conformer model, tweaks hydrophobic properties.
        - This offered a better washout/lowered efflux risk!
    **R3** - the heterocyclic nitrogen handle at the edge of the purine - scaffold handle that is kept to monitor conformational changes that may occur due to R1 and R2 modifications, the controlled stratum in this experiment - modifications bound to R3 on end, though
- Demarcated by round of modification - each round focused on a specific modification rationale as follows:
    **Round 1** - focused on baseline enumeration - testing the boundaries of molecular weight, docking changes, and a baseline high-throughput screening platform
        Key modifications done in Round 1: addition of simple aromatic functional groups such as methyl and ethyl groups in place of the tertiary amide nitrogen (R1), no targeted halogenation - established a baseline for enumeration and bulk properties such as molecular weight and dipole moment
    **Round 2** - Round 2 primarily modified R2 - the terminal benzyl group - and focused on permuting the logD7.4 levels (most important parameter for BBB permeability), with substitutions of fluoroalkyls and perfluoroalkyls. Introduced fluorination - common groups CF₃, CHF₂, CH₂CF₃, CH₂CF₂CH₃ and etc. in substitution of alkyl groups, and primarily defined the CNS window for multiparametric optimization (next method step)
    **Round 3** -  Targeted stress tests on molecular weight, polarity, and efflux were the key functional groups/modifications done on the AC5216 pharmacophore. These are R2 mods that included ether-linked (e.g. OCHF2, OCH2CH2CF3, etc.) fluoroalkyls that minimize polarity through transmembrane channels. Relatively higher failure rate due to unloaded docking energies (not suitable with the TSPO receptor)
    **Round 4** - Exploratory testing of silyl ethers and inorganic additions (CH2SiEt3, CH2CH2SiMe3) and addition of silyl ethers - drastically increased molecular weight, and had a high docking failure rate - disproves potential hypothesis of silication being useful in the construction of TSPO radioligand scaffold analogs for synthesis and in vivo validation.

**Gen AI Statements** AI did briefly assist with enumeration as it was used to scan the RDKit documentation in potential pharmacophore identification. AI helped validate pharmacophore adjustment and SMILES conversion, although all final SMILES computations and pharmacophore creation were independently done according to clear literature corroborations of the potential R-substitutions - literature listed above in the rationale. AI helped code the data validation snippets (auxiliary) to validate the main RDKit enumeration protocol.

**Code Used**
`enumerate_emapunil_round(x).py`
AI Prompt: based on scaffold SMILES CCN({R1})C(=O)Cn2c3c(cnc(n3)c4ccccc4)n(c2=O){R2} can you please develop a CNS window in Python titled CNS_profile_allroundsref.py off of the IAEA TE-2052 framework prioritizing statistical weights from the documentation - create a multi-parameter optimization score similar to Wager et al. but use TBI permeability parameters and efflux risk as that is hugely important in CNS specific binding to TSPO.
**Scaffold Template**
```python
TEMPLATE = "CCN({R1})C(=O)Cn2c3c(cnc(n3)c4ccccc4)n(c2=O){R2}"

- Main RDKit Enumeration Protocol
for r1n,r1 in r1_list:
    for r2n,r2 in r2_list:
        smi=TEMPLATE.replace("{R1}",r1).replace("{R2}",r2)
        mol=Chem.MolFromSmiles(smi)
# Data validation in RDKit (AI was used in the creation of this snippet - prompt: "validate the mod-->SMILES chain and raise a fail statement if molecule is not loaded.") #
    if mol is None:
    fail += 1
    bad.append((name, smi, "MolFromSmiles failed"))
    continue
# Sanitization of molecules
    try:
    Chem.SanitizeMol(mol)
except Exception as e:
    fail += 1
    bad.append((name, smi, f"SanitizeMol: {e}"))
    continue
# Hard validation for count mismatch procedure (AI used - check previous prompt.)
if ok != target:
    sys.exit(1)

CODE REVIEW

Round 1
Attempt 1 — 2025-11-22
AI prompt: explain error that occurred with zsh "command not found" and normalize keys preventing traceback (most recent call last).
```zsh
# [ERROR] 2025-11-22 — zsh: command not found: vina,/Users/...emap2...log
# Shell interpreted a token with a comma adjacent to 'vina' (likely CSV/filename join).
RECEPTOR="$PWD/TSPO_receptor.pdbqt"
LIGDIR="$PWD/pdbqt_clean"
# (fragment printed in terminal): vina,/Users/...emap2_Bn-3,4diCl_CH2CF3.log

# Normalized the keys for each compound by removing all commas and spaces that may throw tracebacks.
sanitize() { local s=$1; s=${s//,/_,}; s=${s// /_}; s=${s//\//_}; print -r -- $s }
for lig in ${LIGDIR}/*.pdbqt(N); do
  raw=${${lig:t}%.pdbqt}; base=$(sanitize "$raw")
  vina --receptor "$RECEPTOR" --ligand "$lig" \
       --center_x 5.2 --center_y 12.8 --center_z 8.3 \
       --size_x 20 --size_y 20 --size_z 20 \
       --exhaustiveness 8 --num_modes 1 \
       --out "$PWD/docking/round1/poses/${base}.out.pdbqt" \
       > "$PWD/docking/round1/logs/${base}.log" 2>&1 || true
done
```

### Attempt 2 — 2025-11-22
```zsh
# [ERROR] 2025-11-21 — ls: : No such file or directory
vina --receptor "$RECDIR/TSPO_receptor.pdbqt" \
     --ligand "$LIGDIR/$(ls "$LIGDIR" | head -n1)" \
     --center_x 5.2 --center_y 12.8 --center_z 8.3 \
     --size_x 20 --size_y 20 --size_z 20 \
     --exhaustiveness 8 --num_modes 1 \
     --out /tmp/test_out.pdbqt > /tmp/test.log 2>&1 && tail -n 5 /tmp/test.log

# Avoided subshells; use zsh with (N) to handle empty dirs.
LIG_DIR="${LIGDIR:-$PWD/pdbqt_clean}"
ligs=(${LIG_DIR}/*.pdbqt(N))
(( ${#ligs} == 0 )) && { echo "[ERROR] No .pdbqt files in $LIG_DIR"; exit 3; }
test_lig=${ligs[1]}
vina --receptor "$RECDIR/TSPO_receptor.pdbqt" --ligand "$test_lig" \
     --center_x 5.2 --center_y 12.8 --center_z 8.3 \
     --size_x 20 --size_y 20 --size_z 20 \
     --exhaustiveness 8 --num_modes 1 \
     --out /tmp/test_out.pdbqt > /tmp/test.log 2>&1
```

---

## Round 1 — Enumeration (Python / RDKit) - exited with NO ERRORS!

## Round 2 — Enumeration (Python / RDKit)

### Attempt 1 — 2025-11-26
```python
# [ERROR] 2025-09-12 — No immediate docking because 'tspo-tracer' env not active.
# (Enumeration succeeded; downstream docking later failed until env was switched.)
# Reused Round-1 enumeration logic; wrote updated CSV/ligands for Round 2.
```

### Attempt 2 — 2025-11-28
```zsh
# SDF --> PDBQT conversions were slightly tricky as obabel refused to load! created a new pdbqt clean directory through this code for round3 due to high number of analogs. 
mkdir -p pdbqt_clean
for sdf in pdbqt_in/*.sdf(N); do
  base=${${sdf:t}%.sdf}
  obabel "$sdf" -O "pdbqt_clean/${base}.pdbqt" --gen3d || true
done
conda activate tspo-tracer   # ensure vina present
```

## Round 2 — Docking (AutoDock Vina)

### Attempt 1 — 2025-11-30
```zsh
# [ERROR] 2025-11-22 — zsh: command not found: vina,/Users/...emap2...log
# Cause: filenames with commas + mis-parsed token - normalized key instituted.
RECEPTOR="$PWD/TSPO_receptor.pdbqt"
LIG_DIR="$PWD/pdbqt_clean"
for lig in ${LIG_DIR}/*.pdbqt(N); do
  base=${${lig:t}%.pdbqt}
  # (bad join produced a token like 'vina,/path/to/log')
done

#CHECK PREVIOUS ERRORS! normalized keys were instituted for R2 analogs as well, mismatch between rounds.
sanitize() { local s=$1; s=${s//,/_,}; s=${s// /_}; s=${s//\//_}; print -r -- $s }
OUT_DIR="$PWD/docking/round2"
mkdir -p "$OUT_DIR/poses" "$OUT_DIR/logs"
for lig in ${LIG_DIR}/*.pdbqt(N); do
  raw=${${lig:t}%.pdbqt}; base=$(sanitize "$raw")
  vina --receptor "$RECEPTOR" --ligand "$lig" \
       --center_x 5.2 --center_y 12.8 --center_z 8.3 \
       --size_x 20 --size_y 20 --size_z 20 \
       --exhaustiveness 16 --num_modes 9 \
       --out "$OUT_DIR/poses/${base}.out.pdbqt" \
       > "$OUT_DIR/logs/${base}.log" 2>&1 || true
done
```

### Attempt 3 — 2025-11-30 - exited without errors!
```zsh
# [FIX] Finalized Round-2 loop (stable baseline)
RECEPTOR="$PWD/TSPO_receptor.pdbqt"
LIG_DIR="$PWD/pdbqt_clean"
OUT_DIR="$PWD/docking/round2"
mkdir -p "$OUT_DIR/poses" "$OUT_DIR/logs"
for lig in ${LIG_DIR}/*.pdbqt(N); do
  raw=${${lig:t}%.pdbqt}; base=${raw//,/_,}; base=${base// /_}; base=${base//\//_}
  vina --receptor "$RECEPTOR" --ligand "$lig" \
       --center_x 5.2 --center_y 12.8 --center_z 8.3 \
       --size_x 20 --size_y 20 --size_z 20 \
       --exhaustiveness 16 --num_modes 9 \
       --out "$OUT_DIR/poses/${base}.out.pdbqt" \
       > "$OUT_DIR/logs/${base}.log" 2>&1 || true
done
```

## Round 3 — Enumeration (Python / RDKit)

### Attempt 1 — 2025-11-23
```python
# [FIX] Carry-forward enumeration to feed Round-3 ligands
# (same pattern as Round-1/2; ensure clean names carried into PDBQT step)
```

### Attempt 2 — 2025-11-23 - check the R1 version - exited with same errors, pdbqt dir fixed.
```zsh
# [FIX] SDF→PDBQT with sanitized basenames for Round-3
mkdir -p pdbqt_clean
for sdf in pdbqt_in/*.sdf(N); do
  base=${${sdf:t}%.sdf}
  safe=${base//,/_,}; safe=${safe// /_}; safe=${safe//\//_}
  obabel "$sdf" -O "pdbqt_clean/${safe}.pdbqt" --gen3d || true
done
```
**NOTE** OBABEL was used instead of pdbqt_meeko, the native AutodockVina tool for sdf --> pdbqt conversion - easier to execute in zsh and compress file types.
---

## Round 3 — Docking (AutoDock Vina)

### Attempt 1 — 2025-11-24
```zsh
# [ERROR] 2025-11-04 — Permission denied on runner
# Tried to run the new zsh script without exec bit.
./round3_docking.zsh
# [FIX]
chmod +x round3_docking.zsh
```

### Attempt 2 — 2025-11-24
```zsh
# [ERROR] 2025-11-04 — zsh: command not found: vina
# [FIX] Activate env & guard
conda activate tspo-tracer
command -v vina >/dev/null || { echo "[ERROR] vina missing"; exit 2; }
```

### Attempt 3 — 2025-11-24
```zsh
# [ERROR] 2025-11-04 — [ERROR] No .pdbqt files in ./pdbqt_clean
# Cause: LIG_DIR pointed to empty/other path.
LIG_DIR="$PWD/pdbqt_clean"
ligs=(${LIG_DIR}/*.pdbqt(N))
(( ${#ligs} == 0 )) && { echo "[ERROR] No .pdbqt files in $LIG_DIR"; exit 3; }

# [FIX] Verify path and populate ligands, then rerun.
```

### Attempt 4 — 2025-11-24
```zsh
# [ERROR] 2025-11-04 — Receptor path mismatch (RECDIR vs RECEPTOR)
vina --receptor "$RECDIR/TSPO_receptor.pdbqt"  # wrong var in local shell
# [FIX] Use RECEPTOR consistently or export it explicitly
export RECEPTOR="$PWD/TSPO_receptor.pdbqt"
```

### Attempt 5 — 2025-11-24
```zsh
# [ERROR] 2025-11-04 — Logs created but no 'VINA RESULT' lines
# Cause: earlier failures left empty logs; summary scripts found nothing.
# [FIX] Re-run successfully and parse logs again (script auto-parses on resume).
RESUME=1 ./round3_docking.zsh
```

### Attempt 6 — 2025-11-24 (Stable Round-3 runner)
```zsh
# [FIX] Final Round-3 zsh runner (Round-2 style) — concise and robust
RECEPTOR=${RECEPTOR:-"$PWD/TSPO_receptor.pdbqt"}
LIG_DIR=${LIG_DIR:-"$PWD/pdbqt_clean"}
OUT_DIR=${OUT_DIR:-"$PWD/docking/round3"}
EXHAUSTIVENESS=${EXHAUSTIVENESS:-8} # identical parameters to original loop!
NUM_MODES=${NUM_MODES:-9}
CPU=${CPU:-$(sysctl -n hw.ncpu 2>/dev/null || echo 4)}
mkdir -p "$OUT_DIR/poses" "$OUT_DIR/logs"

sanitize() { local s=$1; s=${s//,/_,}; s=${s// /_}; s=${s//\//_}; print -r -- $s }

for lig in ${LIG_DIR}/*.pdbqt(N); do
  raw=${${lig:t}%.pdbqt}; base=$(sanitize "$raw")
  out_pdbqt="$OUT_DIR/poses/${base}.out.pdbqt"
  log_path="$OUT_DIR/logs/${base}.log"
  if [[ -s "$out_pdbqt" ]]; then
    echo "[SKIP] $base"; [[ -s "$log_path" ]] && awk '/VINA RESULT/{print}' "$log_path" >/dev/null
    continue
  fi
  echo "[RUN ] $base"
  # MAIN VINA LOOP - exhaustiveness and center settings for docking poses made sure to be the same between all rounds and original docking z-score pipeline.
  vina --receptor "$RECEPTOR" --ligand "$lig" \
       --center_x 5.2 --center_y 12.8 --center_z 8.3 \
       --size_x 20 --size_y 20 --size_z 20 \
       --exhaustiveness "$EXHAUSTIVENESS" --num_modes "$NUM_MODES" \
       --cpu "$CPU" \
       --out "$out_pdbqt" > "$log_path" 2>&1 || true
done
```

---

## Quick Run (Round 3)
```zsh
conda activate tspo-tracer
chmod +x round3_docking.zsh
./round3_docking.zsh
# Resume to re-parse existing logs and fill summaries after fixes
RESUME=1 ./round3_docking.zsh
```

---

# Entry 11 - CNS Window and Multi-Parametric Optimization

**AI prompt** "Give me a code snippet for a CNS penalty gate on Python through RDKit - here is the documentation: https://www.rdkit.org/docs/source/rdkit.Chem.Descriptors.html#module-rdkit.Chem.Descriptors that takes limits of parameters across docking energy, estimated logD7.4, logS (use ESOL framework from Delaney et al.), clogP, TPSA, molecular weight, HBD, HBA, and RotB with data and key stats weights given." AI was used to create the initial code scaffold for the CNS window, but I checked all code and CNS property modifications with conflicting sources - IAEA was the main source used here, but I crosschecked Wager et al. for any significant conflicts in optimization patterns in the CNS window.

**Dates:** 12/04/25 – 12/18/25 

**Purpose:**  
Run the compounds through a CNS window to evaluate enumerated TSPO ligands in order to:
- filter out chemically valid but CNS-infeasible structures,
- standardize physicochemical constraints into a common framework,
- prepare a stratified candidate set for docking and z-score–based ranking.

- KEY PARAMETERS

The following parameters were computed or derived for each enumerated ligand:

- Molecular weight (MW)
- Topological polar surface area (TPSA)
- Hydrogen bond donors (HBD)
- Hydrogen bond acceptors (HBA)
- Rotatable bonds (RotB)
- cLogP
- logD7.4 (measured if available; otherwise estimated)
- ESOL solubility proxy (logS)
- Efflux risk heuristic (0–2)
- CNS MPO score according to the IAEA (International Atomic Energy Agency)'s TECDOC 2052 framework on pharmacokinetics and radiolabeling properties of CNS PET radioligands

**Source script:**  
`CNS_profile_allroundsref.py`

**RDKit-based core property extraction:** 
```python
mw   = Descriptors.MolWt(m)
tpsa = rdMolDescriptors.CalcTPSA(m)
hbd  = rdMolDescriptors.CalcNumHBD(m)
hba  = rdMolDescriptors.CalcNumHBA(m)
rotb = rdMolDescriptors.CalcNumRotatableBonds(m)
clogp = Crippen.MolLogP(m)

**Function Definitions for each Parameter**
logD7.4: def logD74_estimate(clogp, tpsa):
            return clogp - (tpsa/120.0)
ESOL solubility: def esol_logS_est(clogp, mw, rotb):
    return 0.16 - 0.63*clogp - 0.0062*mw + 0.066*rotb
Efflux risk (risk of pumping radioligands out of cells - nonspecific binding): 
def efflux_risk_0to2(mw, logd74, hbd, hba, tpsa):
    r = 0
    if mw > 500 or logd74 > 4.0: r += 1
    if mw > 550 or logd74 > 4.5: r += 1
    if hbd > 1 or hba > 9 or tpsa >= 90: r += 1
    return min(r, 2)
CNS MPO SCORING GUIDELINE
def band_score(x, ideal, outer):
    x = float(x)
    ideal_lo, ideal_hi = ideal
    outer_lo, outer_hi = outer
    if x < outer_lo or x > outer_hi:
        return 0.0
    if ideal_lo <= x <= ideal_hi:
        return 1.0
    if x < ideal_lo:
        return (x - outer_lo) / (ideal_lo - outer_lo) if ideal_lo != outer_lo else 0.0
    return (outer_hi - x) / (outer_hi - ideal_hi) if outer_hi != ideal_hi else 0.0
def cns_mpo_te2052(clogp, logd74, mw, tpsa, hbd, pka=None):
    terms = []
    if clogp is not None: terms.append(band_score(clogp, (1.5,4.0), (1.0,4.5)))
    if logd74 is not None: terms.append(band_score(logd74,(1.5,4.0),(1.0,4.5)))
    if mw is not None:     terms.append(band_score(mw,   (300,500),(250,550)))
    if tpsa is not None:   terms.append(1.0 if tpsa < 70 else (0.5 if tpsa < 90 else 0.0))
    if hbd is not None:    terms.append(1.0 if hbd == 0 else (0.5 if hbd == 1 else 0.0))
    if pka is not None:    terms.append(band_score(pka,(7.5,10.5),(6.5,11.5)))
    if not terms: return None
    return (sum(terms)/len(terms))*6.0
# window showed tracer limits at:
# clogP = 1.5 - 4.0
# MW = 300 - 500 ± 50
# TPSA with weights at ≤70 and ≤90
# HBD, pKa at statistical weight limits, pKa was not used at all for analyses
# band-score used according to IAEA framework for CNS MPO

**CNS TBI SCORE SCORING PRACTICE** - as a CSV file, 1926 enumerated analogs were narrowed down to 22 final derivatives based on a NON-PROBABILISTIC, WEIGHTED statistical average. The regex is input here:
IF(
  AND(
    MW >= 350 AND MW <= 550,
    logD7.4 >= 1.5 AND logD7.4 <= 4.2,
    TPSA < 90,
    HBD <= 1,
    HBA <= 9,
    RotB <= 10,
    ring_constraint <= 1,
    (logS is blank OR logS <= -6.5),
    BBB_metric >= 0.6
  ),
  PASS,
  FAIL
)
TOTAL COUNTS - 1926 total analogs, 22 final analogs, 1902 failed analogs from the CNS window post-score. 
AVERAGE MPO SCORE OF PASSED ANALOGS: 5.29 ± 0.606 SD
```
---

# Entry 12 - Fine Docking and Pharmacokinetic Simulation (current stage)
**Dates** 1/8 - 2/10

## Fine docking procedures
1/9 Fine docking done - exited with no errors, parameters: 
Grid center: X 5.2 Y 12.8 Z 8.3
Grid size  : X 14 Y 14 Z 14
Grid space : 0.375
Exhaustiveness: 32
CPU: 8
Verbosity: 1

AI guidance used to help start the VMWare fusion virtual environment for Windows - PKSim only works on windows, AI used for original PKSim start-up help.

PKSim - AC5216 done as ref, test - parameters match AC5216 values. 
**Anatomy and Physiology** Human_Adult_TBI_Template used as the key "subject" for the in-silico PBPK modeling. Key parameters: European Male Human, 30 years old, 70.00 kg, 175.00 cm, BMI 22.86 kg/m^2. 
**Measured Quantities** Key measurements - concentrations of tracer in different media - Arterial Blood-Plasma-Concentration, Brain-Tissue-Concentration, Liver-Tissue-Concentration, Peripheral Venous Blood-Plasma-Concentration. 
Key parameters: 
AUC_inf [µmol*min/l]
AUC_inf_norm [µg*min/l]
AUC_tEnd [µmol*min/l]
AUC_tEnd_norm [µg*min/l]
C_max [µmol/l]
C_max_norm [mg/l]
C_tEnd [µmol/l]
Total body clearance/F [ml/min/kg]
% AUC (tlast-∞)
MRT [h]
t_max [h]
Half-Life [h]
Vd (plasma)/F [ml/kg]
Vss (plasma)/F [ml/kg]

## PK-Sim Output Parameters

PK-Sim reports pharmacokinetic (PK) summary parameters derived from simulated concentration–time profiles. Unit listing displayed here for each parameter measured.

### Exposure Metrics
- **AUC_inf [µmol·min/L]**  
  Area under the concentration–time curve extrapolated to infinite time. Represents total systemic exposure assuming a terminal elimination phase can be reliably estimated.

- **AUC_inf_norm [µg·min/L]**  
  Mass-normalized version of AUC_inf. Conveys the same information in different units.

- **AUC_tEnd [µmol·min/L]**  
  Area under the concentration–time curve from time zero to the end of the simulation window.  
  **Used in this study** as the primary exposure metric, as it reflects exposure over the PET-relevant time horizon without relying on uncertain terminal extrapolation.

- **AUC_tEnd_norm [µg·min/L]**  
  Mass-normalized AUC_tEnd. Not used separately to avoid redundancy.

### Concentration Metrics
- **C_max [µmol/L]**  
  Maximum concentration observed in the compartment. Indicates peak exposure immediately following dosing.

- **C_max_norm [mg/L]**  
  Mass-normalized C_max. Equivalent information expressed in different units.

- **C_tEnd [µmol/L]**  
  Concentration at the end of the simulation window. Used qualitatively as a washout indicator.

### Clearance and Residence
- **Total body clearance / F [mL/min/kg]**  
  Systemic clearance estimated from the plasma concentration–time profile. Represents the rate at which compound is removed from circulation.  
  Used as a plausibility check, not as a primary ranking metric.

- **% AUC (tlast–∞)**  
  Fraction of total AUC extrapolated beyond the last simulated time point. High values indicate unreliable AUC_inf estimates. Used only for diagnostics.

- **MRT [h] (Mean Residence Time)**  
  Average time molecules spend in the system. Informative for general PK behavior but not directly PET-relevant for acute imaging windows.

- **t_max [h]**  
  Time to reach C_max. For IV bolus dosing this is near zero and effectively identical across compounds; not used for ranking.

### Half-Life and Distribution
- **Half-Life [h]**  
  Terminal elimination half-life estimated from the late log-linear slope of the plasma curve.  
  **Not used in this study for z-scoring**, as half-life estimates in PBPK microdose simulations are often unstable and not informative for PET scan windows.

- **Vd (plasma) / F [mL/kg]**  
  Apparent volume of distribution. Reflects the extent of tissue distribution but does not specify where the compound distributes - analogous to VT - total volume of distribution, except PBPK rather than PET kinetics.

- **Vss (plasma) / F [mL/kg]**  
  Volume of distribution at STP - ss = steady state. Used as a qualitative check for extreme or implausible distribution behavior.

## Parameter Protocol

**Administration Protocol** I dosed the model at 0.01 mg IV - that's the standard amount used in PET studies of 0.01 mg in intravenous bolus form. This was done to account for the micromolar and nanomolar concentrations of tracer molecule in relation to TSPO for best measurement practices. This hence increases accuracy and PET significance.
**Compounds** Compounds were created according to the parameters of lipophilicity (as logD with reference pH 7.4), fraction unbound (free fraction fP), molecular weight - accounting for halogen properties in Da (g/mol), solubility constant in reference ph (7.4) - solubility was substituted with a non-rate-determining constant value for all 17 analogs that were simulated (at 1000 mg/L) that allows for defensible PET simulation regardless of template body. Permeability was a parameter calculated off of logD (7.4) and fraction unbound.

**PKSim fU calculations** - Zoghbi, S. S., Anderson, K. B., Jenko, K. J., Luckenbaugh, D. A., Innis, R. B., & Pike, V. W. (2012). On quantitative relationships between drug-like compound lipophilicity and plasma free fraction in monkey and human. Journal of pharmaceutical sciences, 101(3), 1028–1039. https://doi.org/10.1002/jps.22822 - gives an accurate linear regression ratio for logD7.4 --> fraction unbound in humans and non-human primates for accurate PBPK testing.
**AC5216 Ref Kinetics** - Owen, D. R., Phillips, A., O'Connor, D., Grey, G., Aimola, L., Nicholas, R., & Matthews, P. M. (2022). Human pharmacokinetics of XBD173 and etifoxine distinguish their potential for pharmacodynamic effects mediated by translocator protein. British journal of clinical pharmacology, 88(9), 4230–4236. https://doi.org/10.1111/bcp.15392

PKSIM DEVELOPMENTS
**REMOVED** [1/20/25] ANALOG 18 - duplicated and mismatched label, RDKit error. 
**ERROR** Systematic errors with ANALOGS 15, 16, 17, 19 - label --> SMILES mismatches, redocked and recreated SMILES. RDKit used a truncated version and wasn't able to parse CF vs. CF2 design modifications, hence led to a systematic error - issue causes statistical inflation in the CNS window by causing lower molecular weights and lower lipophilicity - sample set potentially larger than expected and warranted.
**FIX** recoded all smiles strings to match the design cues of these analogs. structurally derived properties changed, leading to changes in PKSim modeling.
**DEVELOPMENT** All analogs that experienced this systematic error had lower MPO scores, lower TBI Scores, higher MWs leading to their failure in the CNS window - this systematic error hence reduced the sample set that will be put through PK-Sim. Failure analogs were maintained in the dataset for documentation purposes, but didn't advance to pharmacokinetic simulation stages.
 
Remaining 17 analogs exited without errors (1/22/25) -- data was collected for all key parameters and put through a modified z-score model. Docking scores were substituted with fine docking data and compared with the CNS multi-parametric optimization scores from the previous enumeration and profiling run. Factors that were weighted in this z-score run were AUC_brain_tEnd, Brain_30min,	Brain_60min, Brain_90min, Plasma_30min,	Plasma_60min, Plasma_90min, Brain_Plasma_30min, Brain_Plasma_60min, Brain_Plasma_90min, Washout_30_to_90, Washout_Plasma_30_to_90. The washout indicators were used as penalty indicators for analogs that didn't have proper washout, efflux, and permeability in terms of pharmacokinetics in real world data. 
ALL 17 ANALOGS showed halogenated side chains, validating original hypothesis of halogenation/fluorination in CNS tracer groups.
Weighted average: =
0.3 * ((AD2 - AVERAGE($AD$2:$AD$18)) / STDEV($AD$2:$AD$18)) +
0.15 * ((AC2 - AVERAGE($AC$2:$AC$18)) / STDEV($AC$2:$AC$18)) +
0.1 * ((AE2 - AVERAGE($AE$2:$AE$18)) / STDEV($AE$2:$AE$18)) +
0.2 * ((T2  - AVERAGE($T$2:$T$18))  / STDEV($T$2:$T$18)) +
0.15 * ((K2  - AVERAGE($K$2:$K$18))  / STDEV($K$2:$K$18)) +
0.1 * ( -1 * (L2 - AVERAGE($L$2:$L$18)) / STDEV($L$2:$L$18)) +
IF(OR(AF2<0.15, AF2>1.5), -0.2, 0) +
IF(AG2>0.8, -0.1, 0)

TOP 5 ANALOGS - A3, A6, A7, A12, A13
TOP 3 ANALOGS (increasing) - A6, A3, A7

# Entry 13 - Data Validation through MoBi PET Kinetics and Mathematical Modeling
 - PET kinetics - mathematical modeling through a 2-tissue compartment model (2TCM) - PK concentration curves plotted through Open Systems Pharmacology's MoBi platform
 - Main deliverables from this regression model - time activity curves gotten from MoBi - concentrations of tracer in 8 curves through arterial blood plasma, peripheral venous blood, brain intracellular, brain tissue, hepatic clearance, brain plasma, and brain-resident blood cells - helps clinically map the radioactivity curve across multiple cellular sources
 - Key parameters - BPND, VT, VND, rate constants K1, K2, K3, K4 for reaction rate with TSPO as a simulated binding protein
 - Curves fit based on the framework https://journals.sagepub.com/doi/pdf/10.1038/sj.jcbfm.9600493 - Innis et al. 2007
  Consensus nomenclature for in vivo imaging of reversibly binding radioligands which shows the mathematical frameworks for the 2-tissue compartment model
 - 2TCM primary source: https://www.turkupetcentre.net/petanalysis/model_2tcm.html
 - PET framing procedure - https://www.turkupetcentre.net/petanalysis/simulation_frames.html?utm_source=chatgpt.com

**GenAI Statement** AI was used to design the initial code template for the 2-tissue compartment model, and was used to correct errors in the script modeling this linear regression methodology through R and helped install file packages in my virtual environment. 

 - Code was taken and cited from kinfitr - R library, Matheson, G. J. (2019). Kinfitr: Reproducible PET Pharmacokinetic Modelling in R. bioRxiv: 755751. https://doi.org/10.1101/755751 and Tjerkaski, J., Cervenka, S., Farde, L., & Matheson, G. J. (2020). 
  - Kinfitr – an open source tool for reproducible PET modelling: Validation and evaluation of test-retest reliability. bioRxiv: 2020.02.20.957738. https://doi.org/10.1101/2020.02.20.957738

ERROR LOG

Attempt 1: 
> master <- do.call(rbind, master_rows)
> write.csv(master, file.path("outputs", "MASTER_2tcm_results.csv"), row.names = FALSE)
> 
> message("\nDone. See outputs/ for CSVs and figures.")
Code failed silently - VT, BPND and other PET metrics didn't load into results. I suspect this is due to a confusion in the original data format as I didn't include fraction unbound (fP) and the code didn't recognize the missing value when asked to calculate, hence it may have gotten confused.

Attempt 2: used kinfitr in order to potentially correct error. Code given according to kinfitr documentation.
+   res <- data.frame(
+     analog_id = analog_id,
+     cp_header = cp_col,
+     ct_header = ct_col,
+     fit_window_min = tail(edges, 1),
+     K1 = K1, k2 = k2, k3 = k3, k4 = k4,
+     VT = VT, BPND = BPND, VND = VND,
+     AUCp_0T = AUCp_0T, AUCt_0T = AUCt_0T,
+     fit_stat = fit_stat,
+     row.names = NULL
+   )
+ 
+   write.csv(res, file.path("outputs", "fits", paste0(analog_id, "_kinfitr_2tcm_results.csv")), row.names = FALSE)
+   master_rows[[analog_id]] <- res

--- Processing A3 ---
Using:
  time: Time [h]
  Cp  : ArterialBlood-Plasma-Analog3-Concentration in container [µmol/l]
  Ct  : Brain-Analog3-Tissue [µmol/l]
Error: 'fit_2tcm' is not an exported object from 'namespace:kinfitr'

Validation message didn't work correctly - the variable I used in order to call 2tcm functioning was not exclusive to kinfitr, hence didn't load the regression model.

Attempt 3: 

Error in kinfitr::weights_create(Ct_frame$frame_mid_min, Ct_frame$frame_dur_min) : 
  argument "tac" is missing, with no default
Error: unexpected ',' in "write.csv(master, file.path("outputs", "MASTER_kinfitr_twotcm_results.csv")),"

This error I believe may be caused by missing stats weights in the PET kinetics functionality in kinfitr, hence time activity curves couldn't be loaded into the final CSV for analysis.

Attempt 4: 
Error in kinfitr::weights_create(t_tac = Ct_frame$frame_mid_min, tac = Ct_frame$Cavg,  : 
  unused arguments (t_tac = Ct_frame$frame_mid_min, dur = Ct_frame$frame_dur_min)
Similar error thrown up even after defining all PET kinetic variables ( analog_id = analog_id,
+     cp_header = cp_col,
+     ct_header = ct_col,
+     fit_window_min = tmax,
+     K1 = K1, k2 = k2, k3 = k3, k4 = k4,
+     VT = VT, BPND = BPND, VND = VND,
+     AUCp_0T = AUCp_0T, AUCt_0T = AUCt_0T,
+     fit_stat = fit_stat,
+     row.names = NULL)
This may be due to arguments pertaining to TAC interpretation not loading the TACs, next fix will include hard-coded TAC identification procedure.
According to Turku PET Centre documentation - Weighting schemes are usually defined in terms of frame boundaries (and/or frame duration) because the variance structure depends strongly on how long each frame is and how many counts it contains - this may be the overall reason for the error of stats weights not correctly computing frame boundaries.

Attempt 5:

1: In kinfitr::twotcm(t_tac = Ct_frame$frame_mid_min, tac = Ct_frame$Cavg,  :
  
Fitted parameters are hitting upper or lower limit bounds. Consider 
either modifying the upper and lower limit boundaries, or else using 
multstart when fitting the model (see the function documentation).

2: In kinfitr::twotcm(t_tac = Ct_frame$frame_mid_min, tac = Ct_frame$Cavg,  :
  
Fitted parameters are hitting upper or lower limit bounds. Consider 
either modifying the upper and lower limit boundaries, or else using 
multstart when fitting the model (see the function documentation).

3: In kinfitr::twotcm(t_tac = Ct_frame$frame_mid_min, tac = Ct_frame$Cavg,  :
  
Fitted parameters are hitting upper or lower limit bounds. Consider 
either modifying the upper and lower limit boundaries, or else using 
multstart when fitting the model (see the function documentation).

Statistical weighting errors thrown up by all analog computations: weights_create() failed (argument "t_start" is missing, with no default); using uniform weights.

Fix: hardcoded call for kinfitr::weights_create in order to pass the t_start window

Attempt 6
Exited with no errors in the first run - K4 results however were exactly 1e-4 for rate constant, which meant that this value was strictly due to the weighting framework combined with limits for rate constants in the differential model. Hence, I reran the kinfitr model with iteration speed increased (assists in plotting values for each TAC) combined with an unconstrained run that didn't include upper bound values for rate constants. 
K4 is important for this equation as BPND directly relies on the index between K3/k4 - dc/dt = dn/dt --> dc/dt = k3/k4. Hence BPND is not reliable in the current run.

Attempts 6-19
Exited with multiple errors either due to missing data inputted into master CSVs, K4 running poorly and hitting penalty limits - this is due to interstitial brain concentrations being 240x larger than tissue concentration which meant Mobi tissue specs came from extravascular origin rather than intravascular. Hence, BPND is not a reliable measure.

Attempt 20 (current attempt)
Abandoned kinfitr methods - decided to run simple VT regression analysis rather than considering BPND - VT and VT/fp will be the primary PET metrics in this data validation. Simple VT analysis went through! Showed sensitivity and specificity based on critical value of t-test t* changes (10-40 min) - VT stayed constant and acted as a great regression predictor with an r^2 value of 0.999986 - VT stayed constant across all analogs. 

**Analog Results**
A7 emerged as the best modified analog scaffold - emap2_Bn-3,4diF_CHF2 - all top 3 analogs emerged with fluorinated side chains indicating high success rate of fluorination method

