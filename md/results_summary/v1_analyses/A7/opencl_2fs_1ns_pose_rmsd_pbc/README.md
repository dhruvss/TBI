# A7 1 ns OpenMM pilot

This folder contains lightweight analysis outputs from the A7 1 ns OpenCL/OpenMM pilot trajectory.

## Summary

- Protein backbone RMSD mean: 1.675 Å
- Protein backbone RMSD final: 1.848 Å
- Ligand heavy-atom pose RMSD mean: 5.329 Å
- Ligand heavy-atom pose RMSD final: 6.560 Å
- Ligand-protein minimum distance mean: 3.249 Å
- Ligand-protein minimum distance final: 3.347 Å
- Ligand-protein contacts mean: 18.7 contacts within 4 Å
- Ligand-protein contacts final: 28 contacts within 4 Å
- Temperature mean: 300.434 K
- Temperature range: 297.322–303.762 K

## Interpretation

A7 passed the 1 ns short-timescale pocket-retention screen.

The ligand showed moderate pose rearrangement relative to the starting docked pose, but it remained protein-associated throughout the trajectory. Ligand-protein minimum distance stayed in contact range, and final contact count recovered strongly to 28 contacts within 4 Å.

This supports A7 as a retained PBPK exposure-maximized candidate after MD screening.
