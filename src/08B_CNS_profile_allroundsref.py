
# Date created: 2025-12-04
import os

from pathlib import Path
import csv
import sys

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKING_DIR = PROJECT_ROOT / "docking"

IN_ALL = DOCKING_DIR / "all_rounds_smiles.csv"
OUT_CSV = DOCKING_DIR / "master_stats.csv"

# AC-5216 reference constants
AC_ID      = "AC-5216_emapunil"
AC_SMILES  = "CCN(CC1=CC=CC=C1)C(=O)CN2C3=NC(=NC=C3N(C2=O)C)C4=CC=CC=C4"
AC_LOGD74  = 3.3
AC_KI_NOTE = "Ki = 2.4 nM"
AC_EDOCK   = "-6.228"      

# R function of read.csv translated to Python that checks each round CSV for each column and places it along with master_stats.csv
# AI was used to create this code snippet, taken from previous analysis.R
def read_csv(path: str):
    with open(path, newline="") as f:
        txt = f.read()
    if txt and txt[0] == "\ufeff":
        txt = txt.lstrip("\ufeff")
    lines = txt.splitlines()
    rdr = csv.DictReader(lines)
    rows = []
    for row in rdr:
        clean = {}
        for k, v in row.items():
            if k is None:
                continue
            key = k.strip().lower()
            val = (v or "").strip()
            clean[key] = val
        rows.append(clean)
    return rows
rows = read_csv(str(IN_ALL))


def write_csv(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in header])


def norm_keys(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isalnum()).lower()

# Used RDKit documentation to reach this method - https://www.rdkit.org/docs/source/rdkit.Chem.Descriptors.html#module-rdkit.Chem.Descriptors
# Crippen's mlogP used here - ties into mlogD prpl used in fP calculations for PKsim
def properties(smiles: str):
    m = Chem.MolFromSmiles(smiles)
    if not m:
        return None
    mw   = Descriptors.MolWt(m)
    tpsa = rdMolDescriptors.CalcTPSA(m)
    hbd  = rdMolDescriptors.CalcNumHBD(m)
    hba  = rdMolDescriptors.CalcNumHBA(m)
    rotb = rdMolDescriptors.CalcNumRotatableBonds(m)
    clogp= Crippen.MolLogP(m)
    return mw, tpsa, hbd, hba, rotb, clogp
# Delaney et al. ESOL
def esol_logS_est(clogp, mw, rotb):
    return 0.16 - 0.63*clogp - 0.0062*mw + 0.066*rotb
# logD estimation based on clogP and TPSA - proxy based on Shityakov et al. for logBB studies (BBB permeability)
def logD_est(clogp, tpsa):
    return clogp - (tpsa/120.0)

# efflux risk heuristic estimation based on key properties and substructure alerts for P-gp efflux, scaled to a 0-2 risk score for penalty gating in MPO calcs
def efflux_risk_Pgp(mw, logd74, hbd, hba, tpsa):
    r = 0
    if mw > 500 or logd74 > 4.0: r += 1
    if mw > 550 or logd74 > 4.5: r += 1
    if hbd > 1 or hba > 9 or tpsa >= 90: r += 1
    return min(r, 2)


def MPO_score_BANDS(x, good, ok):
    lo_g, hi_g = good
    lo_o, hi_o = ok
    if x >= lo_g and x <= hi_g: return 1.0
    if x >= lo_o and x <= hi_o: return 0.5
    return 0.0

# IAEA FRAMEWORK with TECDOC 2052 as basis for the multi-parametric optimization, MPO was originally theorized by Wager et al. for radiotracer research
# TE-2052 was the comprehensive parameter weighting study that I used to determine penalty gates
# Wager et al. MPO function + TE-2052 stats weights was the overall MPO pipeline
def cns_mpo_IAEA(clogp, logd74, mw, tpsa, hbd, pka=None):
    terms = []
    if clogp is not None: terms.append(MPO_score_BANDS(clogp, (1.5,4.0), (1.0,4.5)))
    if logd74 is not None: terms.append(MPO_score_BANDS(logd74,(1.5,4.0),(1.0,4.5)))
    if mw is not None:     terms.append(MPO_score_BANDS(mw,   (300,500),(250,550)))
    if tpsa is not None:   terms.append(1.0 if tpsa < 70 else (0.5 if tpsa < 90 else 0.0))
    if hbd is not None:    terms.append(1.0 if hbd == 0 else (0.5 if hbd == 1 else 0.0))
    if pka is not None:    terms.append(MPO_score_BANDS(pka,(7.5,10.5),(6.5,11.5)))
    if not terms: return None
    return (sum(terms)/len(terms))*6.0

# function loading of docking energies
def norm_id(x):
    """
    Normalize ligand IDs so docking IDs and analog-library IDs match
    across CSVs, filenames, and Vina output names.
    """
    if x is None:
        return ""

    x = str(x).strip()
    x = x.replace(",", "__")
    x = x.replace(" ", "")
    x = x.replace(".pdbqt", "")
    x = x.replace("_out", "")
    x = x.replace("_fine", "")
    x = x.replace("_coarse", "")

    return x.lower()

def load_Edocks():
    ID_KEYS = ("ligand_id", "name", "id", "ligand")
    E_KEYS = ("affinity_kcal_per_mol", "e_dock", "energy", "affinity", "score")

    energy_by_norm = {}
    candidates = []

    for root, _, files in os.walk(DOCKING_DIR):
        for fn in files:
            low = fn.lower()
            if low.endswith(".csv") and "fail" not in low and "results_round" in low:
                candidates.append(os.path.join(root, fn))
    picked = 0
    for fp in candidates:
        rows = read_csv(fp)
        if not rows:
            continue
        first = rows[0]
        id_key = next((k for k in ID_KEYS if k in first), None)
        e_key  = next((k for k in E_KEYS  if k in first), None)
        if not id_key:
            continue
        if not e_key:
            # fallback: first numeric column
            for k, v in first.items():
                if k == id_key:
                    continue
                try:
                    float(v)
                    e_key = k
                    break
                except Exception:
                    pass
        if not e_key:
            continue

        for r in rows:
            lid = r.get(id_key, "")
            e   = r.get(e_key, "")
            if not lid or not e:
                continue
            try:
                float(e)
            except Exception:
                continue
            energy_by_norm[norm_id(lid)] = e
            picked += 1

    print(f"[merge] energies loaded: {picked} from {len(candidates)} files")
    return energy_by_norm

# main file finder for the all_rounds_smiles and each of the round csvs - merges it all into a master_stats.csv for further big data normalization with enumeration
# AI was used to write this code snippet - ChatGPT, OpenAI, 5.2 version. 
if not IN_ALL.is_file():
    sys.exit(f"Missing {IN_ALL} (expected columns: round,ligand_id,smiles)")
    base_rows = read_csv(IN_ALL)
    print(f"[debug] base_rows loaded: {len(base_rows)}")
    if not base_rows:
        sys.exit("No rows in all_rounds_smiles.csv")

    energy_by_norm = load_Edocks()

    out_rows = []
    for r in base_rows:
        lig = (r.get("ligand_id") or r.get("ligand") or r.get("name") or r.get("id") or "").strip()
        smi = (r.get("smiles")    or r.get("smi")   or "").strip()
        rnd = (r.get("round")     or "").strip()

        if not lig or not smi:
            continue

        props = properties(smi)
        if props is None:
            continue
        mw, tpsa, hbd, hba, rotb, clogp = props

        # measured logD if present just as a safety net for AC5216 value - that is the only value that has a measured logD
        logd_meas = None
        if r.get("logd7.4"):
            try:
                logd_meas = float(r["logd7.4"])
            except Exception:
                logd_meas = None

        logd_est = None if logd_meas is not None else logD_est(clogp, tpsa)
        logd_use = logd_meas if logd_meas is not None else logd_est
        logS   = esol_logS_est(clogp, mw, rotb)
        efflux = efflux_risk_Pgp(mw, logd_use if logd_use is not None else 0.0, hbd, hba, tpsa)
        mpo    = cns_mpo_IAEA(clogp, logd_use, mw, tpsa, hbd)
        edock  = energy_by_norm.get(norm_id(lig), "")

        out_rows.append({
            "round": rnd,
            "ligand_id": lig,
            "smiles": smi,
            "MW": f"{mw:.3f}",
            "cLogP": f"{clogp:.3f}",
            "logD7.4": f"{logd_meas:.3f}" if logd_meas is not None else "",
            "logD7.4_est": f"{logd_est:.3f}" if logd_est is not None else "",
            "TPSA": f"{tpsa:.3f}",
            "HBD": str(int(hbd)),
            "HBA": str(int(hba)),
            "RotB": str(int(rotb)),
            "logS_ESOL_est": f"{logS:.3f}",
            "efflux_risk_0to2": str(efflux),
            "E_dock": edock,
            "CNS_MPO_TE2052": f"{mpo:.3f}" if mpo is not None else "",
            "Ki_note": ""
        })

    print(f"[debug] out_rows from analogs: {len(out_rows)}")

    # append AC-5216 reference row
    if AC_SMILES:
        props = properties(AC_SMILES)
        if props:
            mw, tpsa, hbd, hba, rotb, clogp = props
            logS = esol_logS_est(clogp, mw, rotb)
            mpo = cns_mpo_IAEA(clogp, AC_LOGD74, mw, tpsa, hbd)
            efflux = efflux_risk_Pgp(mw, AC_LOGD74, hbd, hba, tpsa)
            out_rows.append({
                "round": "REF",
                "ligand_id": AC_ID,
                "smiles": AC_SMILES,
                "MW": f"{mw:.3f}",
                "cLogP": f"{clogp:.3f}",
                "logD7.4": f"{AC_LOGD74:.3f}",
                "logD7.4_est": "",
                "TPSA": f"{tpsa:.3f}",
                "HBD": str(int(hbd)),
                "HBA": str(int(hba)),
                "RotB": str(int(rotb)),
                "logS_ESOL_est": f"{logS:.3f}",
                "efflux_risk_0to2": str(efflux),
                "E_dock": AC_EDOCK,
                "CNS_MPO_TE2052": f"{mpo:.3f}" if mpo is not None else "",
                "Ki_note": AC_KI_NOTE
            })

    header = [
        "round","ligand_id","smiles",
        "MW","cLogP","logD7.4","logD7.4_est",
        "TPSA","HBD","HBA","RotB",
        "logS_ESOL_est","efflux_risk_0to2",
        "E_dock","CNS_MPO_TE2052","Ki_note"
    ]
    write_csv(OUT_CSV, out_rows, header)
    print(f"Wrote {OUT_CSV} with {len(out_rows)} rows")
