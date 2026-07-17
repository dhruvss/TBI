# A15 1 ns OpenMM pilot

This folder contains lightweight analysis outputs from the A15 1 ns OpenCL/OpenMM pilot trajectory.

The TSPO/membrane system remained stable, but A15 did not retain the original docked pocket pose during the unrestrained 1 ns pilot.

## Summary

- Protein backbone RMSD mean: 1.697 Å
- Protein backbone RMSD final: 2.030 Å
- Ligand heavy-atom pose RMSD mean: 50.818 Å
- Ligand heavy-atom pose RMSD final: 70.920 Å
- Ligand-protein minimum distance mean: 7.245 Å
- Ligand-protein minimum distance final: 11.265 Å
- Ligand-protein contacts mean: 7.7 contacts within 4 Å
- Ligand-protein contacts final: 0 contacts within 4 Å
- Temperature mean: 300.223 K
- Temperature range: 296.939–303.346 K

## Interpretation

A15 passed basic system-stability checks but failed the short-timescale pocket-retention screen. The ligand moved away from the initial TSPO pocket pose and lost final protein contacts within 4 Å.

This does not mean A15 is chemically useless, but it weakens A15 as a TSPO pocket-retentive candidate under this specific short unrestrained membrane MD protocol.
