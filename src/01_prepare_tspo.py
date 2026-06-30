# src/prepare_tspo.py
import os
import sys
from pathlib import Path

from pdbfixer import PDBFixer
from openmm.app import PDBFile

# Paths relative to repository root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKING_DIR = PROJECT_ROOT / "docking"
TSPO_DIR = DOCKING_DIR / "TSPO"

HUMAN_PDB = TSPO_DIR / "Human_TSPO.pdb"
BACT_PDB = TSPO_DIR / "4UC1.pdb"
OUTPUT_PDB = TSPO_DIR / "TSPO_prepped.pdb"

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
