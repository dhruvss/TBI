# Force field and system choices

## Protein force field

Protein systems are prepared using the CHARMM additive force field family through CHARMM-GUI.

For this project, OpenMM output is selected for local or Colab execution.

## Ligand force field

The TSPO ligands are nonstandard small molecules and require ligand parameterization.

Ligand parameters are generated through the CHARMM-GUI ligand parameterization route, typically using Ligand Reader & Modeler / CGenFF-style parameter generation.

Ligand parameterization warnings, penalty scores, formal charge assumptions, and manual corrections should be recorded per candidate.

## Membrane choice

The first-pass membrane system uses POPC.

Rationale:

- TSPO is a membrane protein and should not be simulated as a protein floating in water.
- POPC is a simple, standard membrane environment for initial method validation.
- The first goal is to test whether the TSPO-ligand setup is stable and reproducible.
- More complex mitochondrial-like membrane compositions can be considered later, after the AC-5216 reference system runs cleanly.

## Solvent and ions

Initial settings:

    Water model: TIP3P
    Ion concentration: 0.15 M NaCl

## Simulation scope

The first-pass MD scope is:

    1. Minimization
    2. CHARMM-GUI equilibration protocol
    3. Short pilot production MD
    4. Ligand pose stability and contact analysis

The initial simulations are not used to claim absolute binding free energies.

They are used to compare pose stability and local TSPO-ligand interactions across a small candidate panel.
