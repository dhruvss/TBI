# Fine Docking of Lead Candidates

This folder contains fine-docking outputs for the final lead candidate set advanced after enumeration, CNS-MPO screening, and initial docking.

Fine docking was performed only on the lead candidates selected for downstream PBPK and PET kinetic analysis. Compared with the coarse docking screen, fine docking used a smaller and more focused AutoDock Vina search box and higher exhaustiveness:

- Coarse docking screen: 20 × 20 × 20 grid, exhaustiveness 8
- Fine docking screen: 14 × 14 × 14 grid, exhaustiveness 32

The fine-docking stage was intended to improve relative pose and score confidence for the narrowed candidate set, not to produce experimentally validated binding affinities.

Files in this folder may include:
- Fine-docked ligand output poses
- AutoDock Vina log files
- Candidate-specific docking outputs
- Parsed docking score summaries

These outputs support the final ranking of 17 lead candidates and the AC-5216 reference comparator used in PBPK and weighted z-score analyses.
