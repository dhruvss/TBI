# AC-5216 1 ns OpenCL/OpenMM pilot

This folder contains lightweight analysis outputs from the AC-5216 / emapunil 1 ns OpenCL 2 fs OpenMM pilot trajectory.

This run is used as the primary AC-5216 reference for comparison against A15, A3, A7, and A17 because those analogs were also evaluated using the OpenCL 2 fs 1 ns protocol.

## Summary

- Protein backbone RMSD mean: 1.432 Å
- Protein backbone RMSD final: 2.014 Å
- Ligand heavy-atom pose RMSD mean: 3.940 Å
- Ligand heavy-atom pose RMSD final: 1.436 Å
- Ligand-protein minimum distance mean: 4.013 Å
- Ligand-protein minimum distance final: 3.438 Å
- Ligand-protein contacts mean: 23.6 contacts within 4 Å
- Ligand-protein contacts final: 29 contacts within 4 Å
- Temperature mean: 300.305 K
- Temperature range: 296.947–303.138 K

## Interpretation

AC-5216 / emapunil retained a protein-associated, contact-rich TSPO pose during the 1 ns OpenCL 2 fs pilot.

An earlier CPU 1 fs pilot also exists locally and showed more late-trajectory ligand relaxation. That older run is retained as a sensitivity/provenance trajectory, but this OpenCL 2 fs run is used for the final panel comparison because it matches the protocol used for A15, A3, A7, and A17.
