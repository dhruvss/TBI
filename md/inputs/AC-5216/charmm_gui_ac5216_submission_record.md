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

## OpenMM setup attempt 003 inspection

OpenMM setup attempt 003 used the corrected Meeko-exported AC-5216 ligand SDF.

Visual inspection showed that the POPC membrane system was acceptable for minimization:
- TSPO appeared embedded through the POPC bilayer rather than lying flat on the membrane surface.
- Water and ions were placed outside the bilayer region.
- The ligand geometry no longer showed the atom-order-transfer artifact from the rejected SDF attempt.
- The AC-5216 ligand remained suitable for pocket/contact inspection before minimization.

Accepted setup for minimization:

    /Users/dhruv/Documents/Research/TBI-tracer/MD_runs/AC-5216/openmm_setup_003/

Local visual inspection files:

    /Users/dhruv/Documents/Research/TBI-tracer/MD_runs/AC-5216/openmm_setup_003/setup_003_visual_inspection.pse
    /Users/dhruv/Documents/Research/TBI-tracer/MD_runs/AC-5216/openmm_setup_003/setup_003_membrane_inspection.png

Setup 003 is accepted as the first AC-5216 membrane-embedded starting system for energy minimization.
