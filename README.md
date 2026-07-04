# In Silico Evaluation of Haloalkylated TSPO PET Tracer Candidates for Traumatic Brain Injury Neuroinflammation

This repository contains code, processed data, figures, and supplementary materials for a computational study prioritizing haloalkylated emapunil-derived TSPO PET tracer candidates for traumatic brain injury neuroinflammation.

The workflow includes reference TSPO tracer scoring, AC-5216/emapunil pharmacophore selection, analog enumeration, CNS-MPO filtering, AutoDock Vina docking, PBPK-derived candidate ranking, and Logan graphical analysis of simulated time–activity curves.

This project is entirely computational. The proposed analogs should be interpreted as prioritized candidates for future radiosynthesis, TSPO binding assays, autoradiography, and preclinical TBI PET validation, not as experimentally validated radiotracers.

## Repository Structure

- `docking/`: Docking requirements and structures of lead candidates, errors and error logs in docking, and all TSPO/2nd generation tracer structures loaded.
- `src/`: Source code for enumeration, screening, docking analysis, PBPK aggregation, and PET kinetic analysis.
- `data_analysis/`: Reference-tracer scoring and z-score analysis scripts.
- `processed_data_supplements/`: Final supplementary CSV tables supporting the manuscript.
- `figures/`: Manuscript and analysis figures.
- `templates_functional_groups/`: Functional-group templates used for analog enumeration.
- `manuscripts/`: Manuscript and supplementary information files.
- `PKSim TAC figures/`: PKSim time-activity curves for top 17 lead candidate data + respective figs
- `supp_ref-scripts `: auxiliary zcripts to src - use when needed, includes a SMILES converter script, validations, plotting, and overall file conversion for SDFs for easier visualization

## Environment setup

The reproducible analysis environment is defined in `environment.yml`.

Create and activate the environment with:

```bash
conda env create -f environment.yml
conda activate tbi-tracer
```
# To update an existing environment
```bash
conda env update -f environment.yml --prune
```

# Then run the core reproducibility checks:
```
python -m py_compile src/*.py
python src/08B_CNS_profile_allroundsref.py
Rscript src/02_z-score_refs.R
Rscript src/11_MoBi_turku_logan_fits.R
```
# Expected regenerated or validated outputs include:
```
docking/master_stats.csv
figures/pet_tracer_features_and_z.csv
figures/leaderboard_composite.png
figures/scatter_vt_vs_bpnd.png
data_analysis/outputs/MASTER_VT_logan_with_sensitivity.csv
```
# The full generated docking workspaces are intentionally excluded from GitHub:
```
docking/emap_enum_round1/
docking/emap_enum_round2/
docking/emap_enum_round3/
```
These directories contain thousands of reproducible intermediate SDF/PDBQT files, docking poses, and logs. Instead, this repository provides the full analog SMILES table, curated docking-result summaries, master statistics, receptor/tracer inputs, analysis scripts, PK-Sim/MoBi exports, and processed outputs needed to reproduce the reported rankings and downstream analyses.

Original docking was performed with AutoDock Vina 1.2.5. The Conda environment installs Vina from conda-forge; minor version differences may slightly affect newly regenerated docking scores, so the processed docking outputs used in the study are included.

## Important limitation

Do not include PK-Sim or MoBi in this file. They are external GUI applications and need separate installation instructions.

## External software

The following software is not managed through Conda:

- PK-Sim
- MoBi
- PyMOL, used for molecular visualization
- CHARMM-GUI, accessed through its web interface
- Google Colab, optionally used for GPU-based molecular dynamics
- Excel/Google Sheets for basic z-scoring and ranking of lead candidates

Processed PK-Sim and MoBi exports are included so that downstream analyses
can be reproduced without rebuilding every simulation manually.

## Citation

Dhruv Subramanian. In Silico Evaluation of Haloalkylated Human 18kDa Translocator Protein PET Tracer Candidates for Traumatic Brain Injury Neuroinflammation. ChemRxiv. 21 May 2026.
DOI: https://doi.org/10.26434/chemrxiv.15003660/v1
