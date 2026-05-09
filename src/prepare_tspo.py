# src/prepare_tspo.py
import os
import sys
from pdbfixer import PDBFixer
from openmm.app import PDBFile

# Paths (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCKING_DIR  = os.path.join(PROJECT_ROOT, 'docking')
HUMAN_PDB    = os.path.join(DOCKING_DIR, 'Human_TSPO.pdb')
BACT_PDB     = os.path.join(DOCKING_DIR, '4UC1.pdb')
OUTPUT_PDB   = os.path.join(DOCKING_DIR, 'TSPO_prepped.pdb')

# Choose input
if os.path.isfile(HUMAN_PDB):
    input_pdb = HUMAN_PDB
    print(f"Using human TSPO model: {input_pdb}")
elif os.path.isfile(BACT_PDB):
    input_pdb = BACT_PDB
    print(f"Human model not found: {input_pdb}")
else:
    print("ERROR: No TSPO PDB found in docking.")
    sys.exit(1)

# Fixer pipeline
fixer = PDBFixer(filename=input_pdb)
fixer.findMissingResidues()
fixer.findMissingAtoms()
fixer.addMissingAtoms()
fixer.addMissingHydrogens(pH=7.4)

# Write out the prepped file
with open(OUTPUT_PDB, 'w') as f:
    PDBFile.writeFile(fixer.topology, fixer.positions, f)

print(f"Prepared receptor saved to: {OUTPUT_PDB}")
