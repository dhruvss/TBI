# A3 1 ns OpenMM pilot

This folder contains lightweight analysis outputs from the A3 1 ns OpenCL/OpenMM pilot trajectory.

## Summary

- Protein backbone RMSD mean: 1.472 Å
- Protein backbone RMSD final: 1.643 Å
- Ligand heavy-atom pose RMSD mean: 3.571 Å
- Ligand heavy-atom pose RMSD final: 1.928 Å
- Ligand-protein minimum distance mean: 3.418 Å
- Ligand-protein minimum distance final: 3.291 Å
- Ligand-protein contacts mean: 15.5 contacts within 4 Å
- Ligand-protein contacts final: 30 contacts within 4 Å
- Temperature mean: 300.360 K
- Temperature range: 297.621–302.982 K

## Interpretation

A3 passed the 1 ns short-timescale pocket-retention screen. The TSPO/membrane system remained stable, and A3 remained protein-associated throughout the trajectory.

A3 showed transient contact loss during parts of the trajectory, but the final pose recovered strong ligand-protein contact density. The final ligand RMSD was lower than the trajectory mean, and the final contact count was the highest observed value.

This makes A3 the strongest pocket-retention result so far among the tested compounds.
