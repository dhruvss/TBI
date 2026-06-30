# round3_cns_props.py
# 12/4/2025 date created
import os, sys, csv
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors

from pathlib import Path
import sys
import csv

# Repository paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROUND3_DIR = PROJECT_ROOT / "docking" / "emap_enum_round3"

SRC = ROUND3_DIR / "round3_max.csv"
OUT_PROPS = ROUND3_DIR / "props_round3.csv"

if not SRC.is_file():
    sys.exit(f"Missing Round 3 input CSV: {SRC}")
with SRC.open(newline="") as f:
with OUT_PROPS.open("w", newline="") as f:

# KEEP_TXT = os.path.join(BASE, "round3_cns_lead.txt") - originally used, but manually calculated and selected later after regex gate was applied in Sheets.
# KEEP_SMI = os.path.join(BASE, "round3_cns_lead.smi")

TPSA_MAX = 90.0
LOGP_MIN, LOGP_MAX = 0.0, 5.0
MW_MAX = 450.0
HBD_MAX = 2
HBA_MAX = 6
ROTB_MAX = 8
# used RDKit documentation - https://www.rdkit.org/docs/source/rdkit.Chem.Descriptors.html#module-rdkit.Chem.Descriptors - descriptor module
# cns pass gate defined here - MPO key with the MAX and MIN variables for each parameter
# variables defined first, function created based on descriptors in RDkit for each structure that was considered valid in the descriptor algorithm
# normalized keys created later for ligand IDs
def props(m):
    return (
        Descriptors.MolWt(m),
        rdMolDescriptors.CalcTPSA(m),
        Crippen.MolLogP(m),
        rdMolDescriptors.CalcNumHBD(m),
        rdMolDescriptors.CalcNumHBA(m),
        rdMolDescriptors.CalcNumRotatableBonds(m),
    )

def pass_cns(mw, tpsa, logp, hbd, hba, rotb):
    if not (LOGP_MIN <= logp <= LOGP_MAX): return False
    if tpsa > TPSA_MAX: return False
    if mw > MW_MAX: return False
    if hbd > HBD_MAX: return False
    if hba > HBA_MAX: return False
    if rotb > ROTB_MAX: return False
    return True

with open(SRC) as f:
    r = csv.DictReader(f)
    rows = list(r)

name_key = "ligand_id" if "ligand_id" in rows[0] else ("name" if "name" in rows[0] else None)
smi_key = "smiles" if "smiles" in rows[0] else ("smi" if "smi" in rows[0] else None)
if not name_key or not smi_key:
    sys.exit("round3_max.csv must have columns for name/ligand_id and smiles.")

out_rows = []
keepers = []

for row in rows:
    name = row[name_key].strip()
    smi = row[smi_key].strip()
    m = Chem.MolFromSmiles(smi)
    if m is None:
        continue
    mw, tpsa, logp, hbd, hba, rotb = props(m)
    keep = pass_cns(mw, tpsa, logp, hbd, hba, rotb)
    out_rows.append([name, smi, mw, tpsa, logp, hbd, hba, rotb, int(keep)])
    if keep:
        keepers.append((name, smi))

with open(OUT_PROPS, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ligand_id","smiles","MW","TPSA","cLogP","HBD","HBA","RotB","CNS_keep"])
    w.writerows(out_rows)

# with open(KEEP_TXT, "w") as f:
    for name, _ in keepers:
        f.write(f"{name}\n")

# with open(KEEP_SMI, "w") as f:
    for name, smi in keepers:
        f.write(f"{smi} {name}\n")

print(f"wrote {OUT_PROPS}")
# print(f"wrote {KEEP_TXT}")
# print(f"wrote {KEEP_SMI}")
# KEEP TXT AND SMI REMOVED - UNNECESSARY as they were manually created on the sheets template instead for master_stats based on tailored stats weights
