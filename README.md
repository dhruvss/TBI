# In Silico Evaluation of Haloalkylated TSPO PET Tracer Candidates for Traumatic Brain Injury Neuroinflammation

This repository contains code, processed data, figures, and supplementary materials for a computational study prioritizing haloalkylated emapunil-derived TSPO PET tracer candidates for traumatic brain injury neuroinflammation.

The workflow includes reference TSPO tracer scoring, AC-5216/emapunil pharmacophore selection, hypothesis-driven analogue enumeration, an IAEA-informed CNS physicochemical advancement window, AutoDock Vina docking, PBPK-derived candidate ranking and weighting sensitivity analysis, Logan graphical analysis of simulated time-activity curves, consensus ADMET assessment, replicated membrane molecular dynamics, ASKCOS retrosynthetic feasibility analysis, and integrated Pareto tradeoff analysis.

This project is entirely computational. The proposed analogues should be interpreted as prioritized candidates for future radiosynthesis, TSPO binding assays, autoradiography, and preclinical TBI PET validation, not as experimentally validated radiotracers.

## KEY OUTCOMES

The finalized analysis retained 1,922 enumerated analogues and advanced 17 PBPK records representing 15 unique analogue structures.

A7 remained the first-ranked PBPK candidate across the baseline, equal-weight, and six leave-one-component-out weighting scenarios.

The replicated MD study comprised five independent 10 ns trajectories for each of A3, A7, A8, A15, and AC-5216, yielding 25 trajectories in total. A7 was the only analogue with an analogue-versus-reference primary MD comparison that remained significant after Holm correction, for mean fixed-pocket contacts.

ASKCOS recovered complete buyable-terminal routes for A3, A8, A15, and AC-5216. No complete route was recovered for A7 under the tested search conditions; preparation of the N-difluoromethylated purinone core remained the principal unresolved transformation.

Descriptive Pareto analysis identified A7 as the only Pareto-optimal analogue across the prespecified PBPK and MD objectives. AC-5216 remained nondominated as the reference because of its slightly shorter mean ligand-to-pocket-center distance.

## Repository Structure

* `ADMET/`: Canonical ADMET profiles, identity audits, and pkCSM/SwissADME consensus outputs.
* `PKSim/`: PK-Sim workbooks, reference simulations, lead-candidate exports, and PBPK weighting-sensitivity outputs.
* `audit/`: Canonical compound identities and structure-quality-control records.
* `auxiliary/`: Supporting conversion, validation, and plotting utilities.
* `data_analysis/`: Reference-tracer inputs and PET kinetic analysis outputs.
* `docking/`: TSPO receptor inputs, ligand structures, docking summaries, error logs, and master physicochemical statistics.
* `documentation/`: Project documentation, provenance records, and AI-use documentation.
* `figures/`: Manuscript and analysis figures.
* `integrated_analysis/`: Integrated candidate matrix, Pareto-front outputs, and tradeoff figures.
* `manuscripts/`: Manuscript, graphical abstract, and supporting-information source files.
* `md/`: Curated molecular-dynamics inputs, scripts, metadata, and lightweight replicated-analysis outputs.
* `processed_data_supplements/`: Publication-facing supplementary CSV tables and machine-readable supporting datasets.
* `src/`: Source code for enumeration, screening, docking analysis, ADMET aggregation, PBPK processing, and PET kinetic analysis.
* `synthesis/askcos/`: Saved ASKCOS requests, raw responses, candidate route summaries, and the audited synthesis-feasibility comparison.
* `templates_functional_groups/`: Functional-group templates used for analogue enumeration.

# Reproducibility Instructions

## Environment setup

The reproducible analysis environment is defined in `documentation/environment.yml`. Run the following commands from the repository root.

Create and activate the environment with:

    conda env create -f documentation/environment.yml
    conda activate tbi-tracer

## To update an existing environment

    conda env update -f documentation/environment.yml --prune

## Then run the core reproducibility checks:

    python -m py_compile src/*.py
    python src/08B_CNS_profile_allroundsref.py
    Rscript src/02_z-score_refs.R
    Rscript src/11_MoBi_turku_logan_fits.R

## Expected regenerated or validated outputs include:

    docking/master_stats.csv
    figures/pet_tracer_features_and_z.csv
    data_analysis/outputs/MASTER_VT_logan_with_sensitivity.csv
    ADMET/admet_canonical_profile_v2.csv
    PKSim/sensitivity_analysis/pbpk_sensitivity_scenario_summary.csv
    md/results_summary/replicated_v2/md_replicate_primary_endpoints.csv
    md/results_summary/replicated_v2/md_primary_endpoint_vs_AC-5216_statistics.csv
    synthesis/askcos/askcos_master_summary.csv
    integrated_analysis/integrated_candidate_matrix.csv
    integrated_analysis/pareto_front.csv

## The full generated docking and MD workspaces are intentionally excluded from GitHub:

    docking/emap_enum_round1/
    docking/emap_enum_round2/
    docking/emap_enum_round3/
    full membrane-system build directories
    production trajectories and checkpoints

These directories contain thousands of reproducible intermediate SDF/PDBQT files, docking poses, logs, membrane-system files, and trajectories. Instead, this repository provides the full analogue SMILES table, curated docking-result summaries, master statistics, receptor/tracer inputs, analysis scripts, PK-Sim/MoBi exports, replicated MD summaries, ASKCOS outputs, and processed data needed to reproduce the reported rankings and downstream analyses.

Original docking was performed with AutoDock Vina 1.2.5. The Conda environment installs Vina from conda-forge; minor version differences may slightly affect newly regenerated docking scores, so the processed docking outputs used in the study are included.

## Important limitation

PK-Sim and MoBi are external GUI applications and require separate installation. Processed exports are included so that downstream analyses can be reproduced without rebuilding every simulation manually.

## External software

The following software is not managed entirely through the Conda environment:

* PK-Sim
* MoBi
* PyMOL, used for molecular visualization
* ASKCOS, accessed through its public API
* Excel/Google Sheets, used for the original PBPK score implementation and basic data review

# Citation

Dhruv Subramanian. In Silico Evaluation of Haloalkylated Human 18kDa Translocator Protein PET Tracer Candidates for Traumatic Brain Injury Neuroinflammation. ChemRxiv. 21 May 2026. DOI: https://doi.org/10.26434/chemrxiv.15003660/v1

The repository includes the expanded ChemRxiv v2 analysis and supporting materials. The citation above should be updated to the version-of-record URL after ChemRxiv v2 is posted.
