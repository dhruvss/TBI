# OpenMM MD panel

## System purpose
The goal is to prepare membrane-embedded TSPO-ligand systems for short-timescale molecular dynamics simulations. These simulations are intended to evaluate docked-pose stability and local protein-ligand contact behavior. They are not intended to estimate absolute binding free energies or experimentally validate binding.
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

For each candidate, the selected docked PDBQT pose is converted to a single-pose SDF and PDB. The SDF is used for ligand chemistry and bond-order inspection. The PDB is used with the protein PDB to save a combined protein-ligand complex in PyMOL.

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

The selected pose was visually inspected in PyMOL against `TSPO_prepped.pdb` and occupied a TSPO pocket/cleft without obvious catastrophic clashes. Close contacts from the rigid-receptor docked pose are expected to be relaxed during minimization.
