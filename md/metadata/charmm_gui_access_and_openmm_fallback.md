# CHARMM-GUI access limitation and OpenMM fallback

CHARMM-GUI registration required an institutional academic or governmental affiliation email address. Independent researcher registration using a non-consumer correspondence domain was declined.

Because CHARMM-GUI access was not available through a legitimate affiliation route, the MD workflow was pivoted to a fully local OpenMM-based setup.

The fallback workflow uses:

    OpenMM for system construction and simulation
    OpenMM Modeller for membrane/water/ion setup
    POPC as the first-pass membrane model
    TIP3P water
    0.15 M ionic strength
    Amber-family protein/lipid force field files available through OpenMM
    OpenFF ligand parameterization through openmmforcefields, if available

This fallback workflow is intended for short-timescale docked-pose stability screening, not absolute binding free energy estimation.

Large generated systems, trajectories, checkpoints, and logs remain excluded from GitHub and are stored locally.
