# Source Code

This folder contains source code used to generate, screen, score, and analyze emapunil-derived TSPO tracer candidates.

The code supports the major computational stages of the project:
1. Analog enumeration from the AC-5216/emapunil scaffold
2. Physicochemical descriptor calculation
3. Estimated logD7.4, solubility, efflux-risk, and CNS-MPO scoring
4. Docking output parsing
5. Lead candidate filtering
6. PBPK output aggregation
7. PET kinetic and Logan-analysis workflows
8. ADMET consensus (v1) and ADMET profile management + error correction

Scripts are organized according to their role in the computational pipeline where possible. Processed outputs and supplementary CSV tables are stored separately in the processed data folder.

The code is provided for transparency and reproducibility of the computational prioritization workflow. Some scripts may require local path adjustment depending on the user’s directory structure.
