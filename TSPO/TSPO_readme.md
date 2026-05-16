# TSPO Structural Model

This folder contains the human 18 kDa translocator protein (TSPO) structural model used for receptor preparation and docking simulations.

The TSPO structure was obtained from the AlphaFold Protein Structure Database using the corresponding human UniProt TSPO entry. This AlphaFold/UniProt-derived model was selected because it provides a ligand-free human TSPO structural prediction with high relative model confidence compared with other open structural options. Ligand-free structure selection was prioritized to avoid potential conformational bias from experimentally solved TSPO structures containing bound ligands such as PK11195.

The receptor model was prepared using PDBFixer to add missing atoms/hydrogens and prepare the AlphaFold TSPO model under physiological pH assumptions prior to docking. The prepared receptor was then converted into docking-ready format for AutoDock Vina simulations.

Files in this folder may include:
- AlphaFold/UniProt-derived TSPO structure files
- PDBFixer-prepared receptor models
- AutoDock Vina receptor input files
- Notes or metadata related to receptor preparation

This model was used for relative computational prioritization only. The docking and PBPK workflow did not explicitly model rs6971-dependent TSPO conformational variants.
