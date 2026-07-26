# AC-5216 definitive fine-pose MD

This directory contains lightweight outputs from the definitive AC-5216
reference molecular-dynamics workflow.

Docking initialization:
- receptor: human TSPO model
- AutoDock Vina scoring
- grid center: 5.2, 12.8, 8.3 Å
- grid size: 14 × 14 × 14 Å
- exhaustiveness: 32
- output modes: 10
- selected pose: lowest-energy mode within the predefined central TSPO cavity
- explicit docking seed retained in the command record

System preparation:
- chemistry-preserving Meeko pose export
- OpenFF ligand parsing and parameterization
- fresh explicit membrane, solvent, and ion system
- energy minimization
- three-stage restrained equilibration

Production:
- OpenMM
- OpenCL
- 300 K
- 2 fs timestep
- 10 ns unrestrained trajectory

Analysis:
- periodic-boundary-aware molecular reconstruction
- protein-backbone alignment
- ligand pose RMSD
- protein backbone RMSD
- ligand-protein distance
- all-protein and fixed-pocket contacts
- ligand center-of-mass displacement from the starting pocket
- full-trajectory and late-window retention metrics

Earlier AC-5216 trajectories initialized from coarse or nonuniform docking poses
are archived as exploratory v1 analyses and are not used as the definitive
manuscript MD result.
