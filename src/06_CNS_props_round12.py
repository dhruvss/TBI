from pathlib import Path
import csv

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors

# Repository paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKING_DIR = PROJECT_ROOT / "docking"

IN_DIRS = [
    DOCKING_DIR / "emap_enum_round1",
    DOCKING_DIR / "emap_enum_round2",
]

OUT_CSV = DOCKING_DIR / "round12_CNS.csv"
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# CNS gate applied here with the log_gate function, which tells us the threshold TPSA and clogP values for penalizing borderline non-permeable and poor permeability values through BBB
def log_gate(tpsa, clogp):
    if tpsa < 90 and 0 < clogp < 5: return "Brain"
    if tpsa < 120 and -0.5 < clogp < 6: return "Border"
    return "Poor"
# EFFLUX risk estimated through a penalty gate using clogP, TPSA, molecular weight and tert-butyl thresholds and scaled by 0-2 for penalty gating in final MPO calcs
def efflux(mol, tpsa, hbd, hba, clogp, mw, rb):
    risk=[]
    if clogp>4.5: risk.append("high_logP")
    if tpsa>90 or hbd>=2 or hba>=8: risk.append("high_polarity")
    if mw>520 or rb>8: risk.append("size_flex")
    tert = Chem.MolFromSmarts("[NX3]([#6])([#6])[#6]")
    if mol.HasSubstructMatch(tert): risk.append("tertiary_amine")
    return "low" if not risk else ";".join(risk)
# LogS estimation script using quasi-ESOL methods where clogP was used rather than logD, aromatic proportion ap was estimated through the sum of all aromatic groups
# overall regression equation 0.16 - 0.63*clogp - 0.0062*mw + 0.066*rb - 0.74*ap is intended to provide a rough estimate of solubility based on these key properties.
def logs_esol_est(mol):
    clogp = Crippen.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    rb = rdMolDescriptors.CalcNumRotatableBonds(mol)
    arom = sum(1 for a in mol.GetAtoms() if a.GetIsAromatic())
    ap = arom / max(1, mol.GetNumAtoms())
    return 0.16 - 0.63*clogp - 0.0062*mw + 0.066*rb - 0.74*ap

rows=[] # rows of CSV final defined by the parameters of each property for all 1926 analogs
for d in IN_DIRS:
    if not os.path.isdir(d): continue
    for sdf in sorted(glob.glob(os.path.join(d,"*.sdf"))):
        for mol in Chem.SDMolSupplier(sdf, removeHs=False):
            if mol is None: continue
            name = mol.GetProp("_Name") if mol.HasProp("_Name") else Path(sdf).stem
            # RDKIT COMPUTATION of properties - referred to RDKit documentation for correct usage
            mw   = Descriptors.MolWt(mol)
            tpsa = rdMolDescriptors.CalcTPSA(mol)
            hbd  = rdMolDescriptors.CalcNumHBD(mol)
            hba  = rdMolDescriptors.CalcNumHBA(mol)
            rb   = rdMolDescriptors.CalcNumRotatableBonds(mol)
            clogp= Crippen.MolLogP(mol)
            logd = clogp
            gate = log_gate(tpsa, clogp)
            eff  = efflux(mol, tpsa, hbd, hba, clogp, mw, rb)
            logs = logs_esol_est(mol)
            # rows of CSV appended with all parameters calced for each molecule with CNS gates and MPO applied
            rows.append({
                "ligand_id": name,
                "source_round": source_round,
                "MW": round(mw, 2),
                "TPSA": round(tpsa, 2),
                "HBD": int(hbd),
                "HBA": int(hba),
                "RB": int(rb),
                "cLogP": round(clogp, 2),
                "logD": round(logd, 2),
                "CNS_gate": gate,
                "Efflux_risk": eff,
                "logS_EST": round(logs, 2),
            })
with open(OUT_CSV,"w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

print(f"[CNS] wrote {len(rows)} → {OUT_CSV}")
