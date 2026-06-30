# ~/Documents/Research/TBI-tracer/src/enumerate_emapunil.py
# First enumeration script for emapunil analogs (AC5216, C23H23N5O2) - 32 analogs based on 8 R1 and 4 R2 variations.
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, Crippen, Lipinski, rdMolDescriptors
from rdkit.Chem.rdmolfiles import SDWriter
import os, csv, itertools, pathlib, random

from pathlib import Path
import csv
import itertools

# Repository paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKING_DIR = PROJECT_ROOT / "docking"
OUT_DIR = DOCKING_DIR / "emap_enum_round1"

OUT_DIR.mkdir(parents=True, exist_ok=True)
# AI defined the seed term for embedded 3d testing values - wasn't actually used in the final script
RNG_SEED = 1337

# CNS window (for annotation only; we DO NOT filter), defined based on typical CNS properties and MPO framework (Wager et al, IAEA TECDOC-2052)
CNS_MAX_MW    = 490.0
CNS_TPSA_MIN  = 30.0
CNS_TPSA_MAX  = 95.0
CNS_HBD_MAX   = 1
CNS_HBA_MAX   = 6
CNS_RB_MAX    = 8
CNS_CLOGP_MIN = 2.0
CNS_CLOGP_MAX = 4.2
# --------------------------------------------------------------

random.seed(RNG_SEED)
pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

# AC-5216 template with replaceable parts:
# Parent: CCN(Cc1ccccc1)C(=O)Cn2c3c(cnc(n3)c4ccccc4)n(c2=O)C
# We replace:
#   - R1 inside N( … ) : default "Cc1ccccc1" - heterocyclic nitrogen at purine nucleus
#   - R2 after c2=O    : default "C" - terminal benzyl group at end
TEMPLATE = "CCN({R1})C(=O)Cn2c3c(cnc(n3)c4ccccc4)n(c2=O){R2}"

R1_LIST = [
    ("Bn",        "Cc1ccccc1"),
    ("Bn-4F",     "Cc1ccc(F)cc1"),
    ("Bn-3,5diF", "Cc1c(F)cc(F)cc1"),
    ("Bn-4CF3",   "Cc1ccc(C(F)(F)F)cc1"),
    ("Bn-4OCF3",  "Cc1ccc(OC(F)(F)F)cc1"),
    ("Bn-4OMe",   "Cc1ccc(OC)cc1"),
    ("Bn-4OCHF2", "Cc1ccc(OC(F)F)cc1"),
    ("Bn-4CN",    "Cc1ccc(C#N)cc1"),
]

R2_LIST = [
    ("Me",      "C"),
    ("Et",      "CC"),
    ("CH2F",    "CF"),
    ("CH2CH2F", "CCF"),
]

def cns_window(p):
    return (p["MW"] <= CNS_MAX_MW and
            CNS_TPSA_MIN <= p["TPSA"] <= CNS_TPSA_MAX and
            p["HBD"] <= CNS_HBD_MAX and
            p["HBA"] <= CNS_HBA_MAX and
            p["RB"]  <= CNS_RB_MAX and
            CNS_CLOGP_MIN <= p["cLogP"] <= CNS_CLOGP_MAX)
# Embedded 3D was not used in the overall script, checked by CNS window instead - 3D conformers NOT NEEDED.
# def embed3d_or_none(m):
    mh = Chem.AddHs(m)
    ps = AllChem.ETKDGv3(); ps.randomSeed = RNG_SEED
    try:
        code = AllChem.EmbedMolecule(mh, ps)
        if code == 0:
            # UFF or MMFF minimize if possible
            try:
                if AllChem.UFFHasAllMoleculeParams(mh):
                    AllChem.UFFOptimizeMolecule(mh, maxIters=400)
                else:
                    props = AllChem.MMFFGetMoleculeProperties(mh, mmffVariant="MMFF94s")
                    if props:
                        AllChem.MMFFOptimizeMolecule(mh, mmffVariant="MMFF94s", maxIters=400)
            except Exception:
                pass
            return Chem.RemoveHs(mh), True
    except Exception:
        pass
    # fall back: no 3D, return original (Open Babel will gen3d later)
    return m, False
# RDKit documentation was the key source for the calcs - check the descriptors module for the properties
# Lipinski's rule of 5 for drug discovery was the primary rule used for the hydrogen bond donors and acceptors (counts)
def calc_props(name, m):
    return dict(
        name=name,
        smiles=Chem.MolToSmiles(m),
        MW=Descriptors.MolWt(m),
        TPSA=rdMolDescriptors.CalcTPSA(m),
        HBD=Lipinski.NumHDonors(m),
        HBA=Lipinski.NumHAcceptors(m),
        RB=Lipinski.NumRotatableBonds(m),
        cLogP=Crippen.MolLogP(m)
    )
# file paths defined, manually validate by putting into sheets and running regex
smi_path = os.path.join(OUT_DIR, "emapunil_enum.smi")
csv_path = os.path.join(OUT_DIR, "emapunil_enum_props.csv")
summary  = os.path.join(OUT_DIR, "SUMMARY.txt")

rows=[]; smi_lines=[]; total=0; wrote=0; n3d=0
# Embedded 3D auxiliary lines - 3D conformers were first used as a CNS gating measure, but I decided to focus completely on physchem
# This allowed for better statistical weighting when looking at TBI pathology in particular.
for (r1n, r1s), (r2n, r2s) in itertools.product(R1_LIST, R2_LIST):
    total += 1
    name = f"emap_{r1n}_{r2n}"
    smi  = TEMPLATE.format(R1=r1s, R2=r2s)
    m = Chem.MolFromSmiles(smi)
    if m is None:
        continue
    m.SetProp("_Name", name)
    m3d, ok3d = embed3d_or_none(m)
    props = calc_props(name, m3d)
    props["passes_cns_window"] = in_cns_window(props)
    props["embedded3d"]        = bool(ok3d)
    sdf_path = os.path.join(OUT_DIR, f"{name}.sdf")
    w = SDWriter(sdf_path); w.write(m3d); w.close()
    rows.append(props); wrote += 1; n3d += int(ok3d)
    smi_lines.append(f"{props['smiles']} {name}")

# write outputs
with open(smi_path, "w") as f:
    f.write("\n".join(smi_lines))

with open(csv_path, "w", newline="") as f:
    cols = ["name","smiles","MW","TPSA","HBD","HBA","RB","cLogP","passes_cns_window","embedded3d"]
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows: w.writerow({k: r[k] for k in cols})

with open(summary, "w") as f:
    f.write(f"Enumerated R1xR2 combos: {total}\n")
    f.write(f"Wrote SDFs (all):        {wrote}\n")
    f.write(f"Embedded 3D via RDKit:   {n3d}\n")
    f.write(f"SDFs directory:          {OUT_DIR}\n")
    f.write(f"SMILES:                   {smi_path}\n")
    f.write(f"Properties CSV:           {csv_path}\n")
# Validation messages done through AI, ChatGPT, OpenAI, 5.2 version - done just as an auxiliary check rather than a hard val snippet.
print(f"Enumerated {total}; wrote {wrote} SDFs ({n3d} with RDKit 3D)")
print(f"SDFs in: {OUT_DIR}")
print(f"SMILES:  {smi_path}")
print(f"CSV:     {csv_path}")
