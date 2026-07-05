# CHARMM-GUI submission notes

## System purpose

The goal is to prepare membrane-embedded TSPO-ligand systems for short-timescale molecular dynamics simulations.

These simulations are intended to evaluate docked-pose stability and local protein-ligand contact behavior. They are not intended to estimate absolute binding free energies or experimentally validate binding.

## Protein inputs

Raw protein provenance structure:

    docking/TSPO/Human_TSPO.pdb

Prepared protein used for docking and MD inspection:

    docking/TSPO/TSPO_prepped.pdb

Docking receptor file:

    docking/TSPO/TSPO_receptor.pdbqt

`TSPO_prepped.pdb` is used for PyMOL inspection and construction of protein-ligand complex PDB files.

`TSPO_receptor.pdbqt` is used only for docking and is not used directly as the MD input structure.

## Ligand inputs

Final fine-docking poses are taken from:

    docking/fine_all_rounds/out_pdbqt/

The selected MD panel is:

    AC-5216
    A15
    A3
    A7
    A17

For each candidate, the selected docked PDBQT pose is converted to a single-pose SDF and PDB.

The SDF is used for ligand chemistry and bond-order inspection.

The PDB is used with the protein PDB to save a combined protein-ligand complex in PyMOL.

## AC-5216 reference system

AC-5216 was fine-docked using the same receptor and docking box as the analogs.

Docking settings:

    Receptor: docking/TSPO/TSPO_receptor.pdbqt
    Ligand: docking/tracers/AC-5216.pdbqt
    Grid center: x=5.2, y=12.8, z=8.3
    Grid size: x=20, y=20, z=20
    Exhaustiveness: 32
    Number of modes: 10
    Selected pose: mode 1
    Vina affinity: -6.1 kcal/mol

The selected pose was visually inspected in PyMOL against `TSPO_prepped.pdb` and occupied a TSPO pocket/cleft without obvious catastrophic clashes.

Close contacts from the rigid-receptor docked pose are expected to be relaxed during minimization.

## CHARMM-GUI plan

CHARMM-GUI is used through the web interface, not installed locally.

The intended workflow is:

    Input Generator
    Membrane Builder
    Upload protein-ligand complex
    Parameterize ligand using CHARMM-GUI Ligand Reader / CGenFF route
    Build membrane protein system
    Select OpenMM output
    Download generated system locally

Initial first-pass system choices:

    Protein model: TSPO_prepped-derived complex
    Membrane: POPC
    Water model: TIP3P
    Ion concentration: 0.15 M NaCl
    Protein force field: CHARMM36 / CHARMM36m additive force field
    Ligand parameterization: CHARMM-GUI Ligand Reader & Modeler / CGenFF
    Simulation engine output: OpenMM

The first CHARMM-GUI system is built only for AC-5216.

Analog systems are built only after the AC-5216 reference system completes minimization, equilibration, and pilot MD successfully.

## Local storage

Full CHARMM-GUI output folders and MD trajectories are stored locally under:

    ~/Documents/Research/TBI-tracer/MD_runs/

They are excluded from GitHub due to size and because they include generated simulation machinery rather than curated analysis outputs.
