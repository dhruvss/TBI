# A17 1 ns OpenMM pilot

This folder contains lightweight analysis outputs from the A17 1 ns OpenCL/OpenMM pilot trajectory.

## Summary

- Protein backbone RMSD mean: 2.010 Å
- Protein backbone RMSD final: 2.248 Å
- Ligand heavy-atom pose RMSD mean: 30.430 Å
- Ligand heavy-atom pose RMSD final: 65.795 Å
- Ligand-protein minimum distance mean: 3.244 Å
- Ligand-protein minimum distance final: 3.208 Å
- Ligand-protein contacts mean: 10.3 contacts within 4 Å
- Ligand-protein contacts final: 3 contacts within 4 Å
- Temperature mean: 300.253 K
- Temperature range: 297.288–303.320 K

## Interpretation

A17 was included as an ADMET-favorable backup candidate.

The TSPO/membrane system remained stable during the 1 ns pilot, but A17 did not strongly retain the original docked pocket pose. The ligand remained near the protein by minimum-distance analysis, but the high ligand pose RMSD and low final contact count suggest substantial displacement from the starting binding mode.

A17 is therefore treated as a weak or borderline pocket-retention result, below A3 and A7 in the MD-prioritized panel.
