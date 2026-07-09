# AC-5216 CHARMM-GUI submission record

## Input files

Protein-ligand complex:

    md/inputs/AC-5216/protein_ligand_complex_clean.pdb

Ligand pose SDF:

    md/inputs/AC-5216/ligand_pose.sdf

Ligand pose PDB:

    md/inputs/AC-5216/ligand_pose.pdb

Pose source note:

    md/inputs/AC-5216/pose_source.txt

## CHARMM-GUI workflow

Workflow:

    Input Generator / Membrane Builder

System:

    Membrane-embedded TSPO-ligand complex

Output engine:

    OpenMM

## System settings

Protein force field:

Ligand parameterization route:

Membrane:

Water model:

Ion concentration:

Box/edge settings:

Terminal patching:

Disulfides:

Histidine/protonation choices:

## Ligand information

Ligand residue name:

Ligand chain:

Formal charge:

CGenFF/Ligand Reader warnings:

Parameter penalty notes:

Manual corrections:

## Notes

Submission date:

CHARMM-GUI job/project ID:

Downloaded output stored locally at:

Any warnings/errors:

## OpenMM setup attempt 001 inspection

The first local OpenMM membrane setup completed technically, but visual inspection showed that the TSPO helical bundle was not correctly oriented as a transmembrane protein relative to the POPC bilayer. The protein appeared to lie largely parallel to the membrane plane / inside a lipid-cleared cavity rather than spanning the bilayer.

This setup was therefore not used for minimization or production MD.

Next action:
The TSPO-ligand coordinates will be reoriented so that the predicted transmembrane helical bundle axis is approximately aligned with the membrane normal before rebuilding the POPC membrane system.
