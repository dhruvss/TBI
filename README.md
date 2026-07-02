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

## Citation

Dhruv Subramanian. In Silico Evaluation of Haloalkylated Human 18kDa Translocator Protein PET Tracer Candidates for Traumatic Brain Injury Neuroinflammation. ChemRxiv. 21 May 2026.
DOI: https://doi.org/10.26434/chemrxiv.15003660/v1
