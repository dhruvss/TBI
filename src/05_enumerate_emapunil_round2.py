
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, Crippen, Lipinski, rdMolDescriptors
from rdkit.Chem.rdmolfiles import SDWriter

from pathlib import Path
import csv
import itertools

# Repository paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKING_DIR = PROJECT_ROOT / "docking"
OUT_DIR = DOCKING_DIR / "emap_enum_round2"

OUT_DIR.mkdir(parents=True, exist_ok=True)
RNG_SEED = 20251002

pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

TEMPLATE = "CCN({R1})C(=O)Cn2c3c(cnc(n3)c4ccccc4)n(c2=O){R2}"
# permutation list for R1 and R2 functional group substitutions which gives us 112 analog permutes from round 2 - focused on 
R1_LIST = [
    ("Bn","Cc1ccccc1"),
    ("Bn-4F","Cc1ccc(F)cc1"),
    ("Bn-3,5diF","Cc1c(F)cc(F)cc1"),
    ("Bn-3,4diF","Cc1c(F)ccc(F)c1"),
    ("Bn-4Cl","Cc1ccc(Cl)cc1"),
    ("Bn-3,4diCl","Cc1c(Cl)ccc(Cl)c1"),
    ("Bn-4Br","Cc1ccc(Br)cc1"),
    ("Bn-4CF3","Cc1ccc(C(F)(F)F)cc1"),
    ("Bn-4OCF3","Cc1ccc(OC(F)(F)F)cc1"),
    ("Bn-4OCHF2","Cc1ccc(OC(F)F)cc1"),
    ("Bn-4OMe","Cc1ccc(OC)cc1"),
    ("Bn-4iPr","Cc1ccc(C(C)C)cc1"),
    ("Bn-4CF2H","Cc1ccc(C(F)F)cc1"),
    ("Bn-4SF5","Cc1ccc(S(F)(F)(F)(F)F)cc1"),
]

R2_LIST = [
    ("Me","C"),
    ("Et","CC"),
    ("iPr","C(C)C"),
    ("cPr","C1CC1"),
    ("CH2F","CF"),
    ("CHF2","C(F)F"),
    ("CH2CH2F","CCF"),
    ("CH2CF3","CC(F)(F)(F)"),
]
# Embedded 3D conformer generation was used but not required for final analysis, this function was also written by OpenAI, ChatGPT 2025.
def embed3d(m):
    mh = Chem.AddHs(m)
    ps = AllChem.ETKDGv3(); ps.randomSeed = RNG_SEED
    code = AllChem.EmbedMolecule(mh, ps)
    if code != 0:
        return Chem.RemoveHs(mh), False
    try:
        props = AllChem.MMFFGetMoleculeProperties(mh, mmffVariant="MMFF94s")
        if props:
            AllChem.MMFFOptimizeMolecule(mh, mmffVariant="MMFF94s", maxIters=300)
        elif AllChem.UFFHasAllMoleculeParams(mh):
            AllChem.UFFOptimizeMolecule(mh, maxIters=300)
    except Exception:
        pass
    return Chem.RemoveHs(mh), True

def props_of(name, m):
    return dict(
        name=name,
        smiles=Chem.MolToSmiles(m),
        MW=Descriptors.MolWt(m),
        TPSA=rdMolDescriptors.CalcTPSA(m),
        HBD=Lipinski.NumHDonors(m),
        HBA=Lipinski.NumHAcceptors(m),
        RB=Lipinski.NumRotatableBonds(m),
        cLogP=Crippen.MolLogP(m),
    )

smi_path = os.path.join(OUT_DIR, "emapunil_enum_round2.smi")
csv_path = os.path.join(OUT_DIR, "emapunil_enum_round2_props.csv")
summary  = os.path.join(OUT_DIR, "SUMMARY_round2.txt")

rows=[]; smi_lines=[]; total=0; wrote=0; n3d=0
# smiles generated for the master_stats.csv starting from round 1, R1.
for (r1n, r1s) in R1_LIST:
    for (r2n, r2s) in R2_LIST:
        total += 1
        name = f"emap2_{r1n}_{r2n}"
        smi  = TEMPLATE.format(R1=r1s, R2=r2s)
        m = Chem.MolFromSmiles(smi)
        if m is None: 
            continue
        m.SetProp("_Name", name)
        m3d, ok = embed3d(m)
        p = props_of(name, m3d)
        p["embedded3d"] = bool(ok)
        SDWriter(os.path.join(OUT_DIR, f"{name}.sdf")).write(m3d)
        rows.append(p); n3d += int(ok); wrote += 1
        smi_lines.append(f"{p['smiles']} {name}")

open(smi_path,"w").write("\n".join(smi_lines))
# csv written here
import csv as _csv
with open(csv_path,"w",newline="") as f:
    cols=["name","smiles","MW","TPSA","HBD","HBA","RB","cLogP","embedded3d"]
    w=_csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in rows: w.writerow({k:r[k] for k in cols})
# Validation prints given by ChatGPT - OPENAI 2025
open(summary,"w").write(
    f"Enumerated R1xR2 combos: {total}\n"
    f"Wrote SDFs (all):        {wrote}\n"
    f"Embedded 3D via RDKit:   {n3d}\n"
    f"SDFs directory:          {OUT_DIR}\n"
    f"SMILES:                   {smi_path}\n"
    f"Properties CSV:           {csv_path}\n"
)
print(f"OK {total} SDFs -> {OUT_DIR}")
