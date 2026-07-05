# Molecular dynamics workflow

This folder contains curated setup files, metadata, scripts, and lightweight summary outputs for molecular dynamics simulations of selected TSPO ligand candidates.

The MD panel contains five compounds:

- AC-5216: reference scaffold
- A15: strongest ADMET/developability consensus candidate
- A3: balanced clean-toxicity comparator
- A7: PBPK exposure-maximized stress-test candidate
- A17: backup ADMET-favorable alternate

The purpose of these simulations is to evaluate whether selected docked TSPO ligand poses remain geometrically stable in a membrane-embedded TSPO model over short-timescale molecular dynamics. These simulations are not intended to provide experimental binding validation or absolute binding free energies.

## Current workflow

1. Select final fine-docking pose for each ligand.
2. Convert selected Vina PDBQT pose to single-pose SDF and PDB.
3. Inspect TSPO-ligand pose in PyMOL using `docking/TSPO/TSPO_prepped.pdb`.
4. Save a cleaned protein-ligand complex PDB for CHARMM-GUI.
5. Build membrane-embedded TSPO-ligand systems using CHARMM-GUI Membrane Builder.
6. Use CHARMM-GUI/OpenMM outputs for minimization, equilibration, and pilot production MD.
7. Store large CHARMM-GUI outputs, trajectories, checkpoints, and failed runs locally, not in GitHub.
8. Commit only curated inputs, setup metadata, scripts, and lightweight summary outputs.

## GitHub/local boundary

GitHub contains:

- selected ligand poses
- cleaned starting complexes
- setup notes and provenance files
- analysis scripts
- lightweight summary CSVs and figures

Local storage contains:

- full CHARMM-GUI download folders
- OpenMM run folders
- trajectories
- checkpoints
- failed runs
- large logs
- exploratory working files

Large MD files are intentionally excluded from GitHub.
