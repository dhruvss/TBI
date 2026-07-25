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

## Minimized structure inspection

The minimized AC-5216 OpenMM setup 003 structure was visually inspected in PyMOL.

Inspection outcome:
- TSPO remained embedded in the POPC membrane.
- The POPC bilayer remained coherent after minimization.
- AC-5216 remained in the TSPO binding pocket.
- AC-5216 ligand geometry remained chemically reasonable.
- Ligand-protein contacts were retained after minimization.
- No obvious catastrophic lipid/protein/ligand distortion was observed.

Conclusion:
The minimized AC-5216 setup 003 system is accepted for restrained equilibration.

## Restrained equilibration stage 1 inspection

Restrained equilibration stage 1 completed successfully.

Output directory:

    /Users/dhruv/Documents/Research/TBI-tracer/MD_runs/AC-5216/openmm_setup_003/equilibration_stage1/

Stage 1 results:

    Total simulated time: 5 ps
    Final temperature: 298.868 K
    Final potential energy: -632119.422 kJ/mol
    Final kinetic energy: 172471.213 kJ/mol
    Final total energy: -459648.209 kJ/mol

Inspection outcome:

    The system completed without NaN coordinates or simulation crash.
    Temperature smoothly approached 300 K.
    TSPO remained embedded in the POPC membrane.
    The POPC bilayer remained coherent.
    AC-5216 remained in the TSPO pocket.
    AC-5216 ligand geometry remained chemically reasonable.
    Ligand-protein contacts were retained after restrained equilibration.

Conclusion:

    AC-5216 restrained equilibration stage 1 is accepted. The system is suitable for a second restrained equilibration stage with reduced positional restraints.

## Restrained equilibration stage 3

Restrained equilibration stage 3 completed successfully using the stage 2 equilibrated PDB as input.

Input files:

    /Users/dhruv/Documents/Research/TBI-tracer/MD_runs/AC-5216/openmm_setup_003/equilibration_stage2/AC-5216_equil_stage2.pdb
    /Users/dhruv/Documents/Research/TBI-tracer/MD_runs/AC-5216/openmm_setup_003/AC-5216_system.xml

Output directory:

    /Users/dhruv/Documents/Research/TBI-tracer/MD_runs/AC-5216/openmm_setup_003/equilibration_stage3/

Settings:

    Ensemble: NVT
    Steps: 20000
    Timestep: 1.0 fs
    Total simulated time: 20 ps
    Temperature: 300 K
    Platform: CPU
    Protein heavy-atom restraint: 50 kJ/mol/nm^2
    Ligand heavy-atom restraint: 25 kJ/mol/nm^2
    Ligand residue name: UNK

Restraint selection:

    Restrained protein heavy atoms: 1340
    Restrained ligand heavy atoms: 30

Energy result:

    Initial potential energy: -629528.265 kJ/mol
    Final potential energy: -629003.204 kJ/mol
    Energy change: 525.061 kJ/mol

Interpretation:

    Stage 3 completed without NaN coordinates or simulation crash. The small energy change relative to stages 1 and 2 is consistent with a stabilized system under light positional restraints. The system is accepted for a 1 ns unrestrained AC-5216 pilot MD run.
