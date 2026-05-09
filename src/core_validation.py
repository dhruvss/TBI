#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, glob, sys
from rdkit import Chem

CORE = "CC(=O)N(CCOC[*:2])C1=NN2C=CC=CC2=C1C3=CC=[*:1]C=C3"
core = Chem.MolFromSmiles(CORE)
if not core:
    sys.exit("Bad core SMILES")

SDF_DIRS = ["docking/emap_enum_round1", "docking/emap_enum_round2"]
# bad variable defined as a core that is not exclusive to the enumeration rounds - same core must be used throughout rounds
bad = []
total = 0

for d in SDF_DIRS:
    if not os.path.isdir(d): continue
    for sdf in sorted(glob.glob(os.path.join(d, "*.sdf"))):
        suppl = Chem.SDMolSupplier(sdf, removeHs=False)
        for mol in suppl:
            if mol is None: continue
            total += 1
            if not mol.HasSubstructMatch(core):
                name = mol.GetProp("_Name") if mol.HasProp("_Name") else os.path.basename(sdf)
                bad.append((name, sdf))

# validation prints given by ChatGPT - OPENAI 2025.
print(f"Checked {total} molecules.")
if bad:
    print(f"Found {len(bad)} without the exact core:")
    for name, sdf in bad[:30]:
        print(f"  - {name}  ({sdf})")
    sys.exit(1)
else:
    print("All molecules contain the Round1–2 core.")
