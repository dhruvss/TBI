# Molecular dynamics workflow

This folder contains curated setup files, metadata, scripts, and lightweight summary outputs for replicated molecular dynamics simulations of selected TSPO ligand candidates.

## Final replicated panel

The finalized MD panel contains five compounds:

* AC-5216: reference scaffold
* A3: PBPK-prioritized analogue
* A7: highest-ranked PBPK candidate and integrated performance lead
* A8: retained ADMET-discordant comparator
* A15: retained developability comparator

Five independent 10 ns production trajectories were completed for each compound, yielding 25 independent trajectories in total.

The purpose of these simulations is to compare short-timescale ligand-pocket association in a membrane-embedded TSPO model. The simulations are not intended to provide experimental binding validation, absolute binding free energies, residence times, or proof of conformational convergence.

## Current workflow

1. Select the final fine-docking pose for each ligand.
2. Convert the selected Vina PDBQT pose to single-pose SDF and PDB representations.
3. Parameterize nonstandard ligands through the OpenFF workflow and document formal-charge assumptions or warnings.
4. Build and visually inspect the POPC/TIP3P/0.15 M NaCl protein-ligand system.
5. Perform energy minimization and the three-stage restrained equilibration protocol.
6. Run five independently seeded 10 ns OpenMM production trajectories for each compound.
7. Reconstruct trajectories under periodic boundary conditions and align the protein before structural analysis.
8. Analyze the three prespecified primary endpoints at the independent-trajectory level.
9. Aggregate all 25 trajectories and run the prespecified replicate-level statistics.
10. Commit only curated inputs, scripts, provenance, and lightweight result tables and figures.

## Prespecified primary endpoints

The primary MD endpoints are:

* mean fixed-pocket contact count within 4 Å
* mean ligand center-of-mass distance from the fixed-pocket center
* percentage of frames retaining at least 10 fixed-pocket contacts

Protein-backbone RMSD, ligand RMSD, ligand-protein minimum distance, and all-protein contacts are retained as secondary descriptive or quality-control endpoints.

## Statistical analysis

Each independent trajectory is the statistical unit; trajectory frames are not treated as independent replicates.

The finalized workflow reports:

* candidate-level descriptive statistics
* Kruskal-Wallis omnibus tests for the three primary endpoints
* two-sided analogue-versus-AC-5216 Mann-Whitney U comparisons
* Holm correction across the four analogue-versus-reference comparisons within each endpoint
* Cliff's delta and Hedges' g effect sizes

Secondary endpoints remain descriptive.

The authoritative replicated outputs are stored under:

    md/results_summary/replicated_v2/

Key files include:

    md_replicate_primary_endpoints.csv
    md_replicate_provenance_manifest.csv
    md_primary_endpoint_descriptive_statistics.csv
    md_primary_endpoint_omnibus_tests.csv
    md_primary_endpoint_vs_AC-5216_statistics.csv
    md_primary_endpoints_replicate_values.png
    md_primary_endpoints_replicate_values.pdf

## Interpretation boundary

Replicated MD supports comparative statements about short-timescale pocket association. Only the A7-versus-AC-5216 fixed-pocket contact comparison remained significant after Holm correction. No claim of global statistical superiority across all MD endpoints is made.

## GitHub/local boundary

GitHub contains:

* selected ligand poses
* cleaned starting complexes
* setup notes and provenance files
* simulation and analysis scripts
* replicate-level summary CSVs
* primary figures and statistical outputs

Local storage contains:

* full membrane-system build directories
* OpenMM production run folders
* trajectories
* checkpoints
* failed runs
* large logs
* exploratory working files

Large MD files are intentionally excluded from GitHub.
