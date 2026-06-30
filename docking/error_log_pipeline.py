#!/usr/bin/env python3

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors

INPUT_CSV  = "error_log.csv"
OUTPUT_CSV = "error_log_recomputed.csv"

# SAME FRAMEWORK AS CNS_PROFILE_ALLROUNDSREF.PY
# This is for the 5 lead candidates out of 17 that had a smiles mismatch which caused them to pass the CNS Gate
# With this new framework, these analogs were shown to actually fail the CNS gate when their SMILES were corrected
# AI was used to write this code snippet - ChatGPT, OpenAI, 5.2 version. This was done as a time-saving measure, as this error needed to be corrected with the same framework as the original MPO pipeline.
def logD74_estimate(clogp, tpsa):
    return float(clogp) - (float(tpsa) / 120.0)

def esol_logS_est(clogp, mw, rotb):
    return 0.16 - 0.63 * float(clogp) - 0.0062 * float(mw) + 0.066 * float(rotb)

def efflux_risk_0to2(mw, logd74, hbd, hba, tpsa):
    r = 0
    if mw > 500 or logd74 > 4.0:
        r += 1
    if mw > 550 or logd74 > 4.5:
        r += 1
    if hbd > 1 or hba > 9 or tpsa >= 90:
        r += 1
    return min(r, 2)

def band_score(x, ideal, outer):
    x = float(x)
    ideal_lo, ideal_hi = ideal
    outer_lo, outer_hi = outer
    if x < outer_lo or x > outer_hi:
        return 0.0
    if ideal_lo <= x <= ideal_hi:
        return 1.0
    if x < ideal_lo:
        return (x - outer_lo) / (ideal_lo - outer_lo)
    return (outer_hi - x) / (outer_hi - ideal_hi)

def cns_mpo_te2052(clogp, logd74, mw, tpsa, hbd, pka=None):
    terms = []
    terms.append(band_score(clogp, (1.5, 4.0), (1.0, 4.5)))
    terms.append(band_score(logd74, (1.5, 4.0), (1.0, 4.5)))
    terms.append(band_score(mw, (300, 500), (250, 550)))
    terms.append(1.0 if tpsa < 70 else (0.5 if tpsa < 90 else 0.0))
    terms.append(1.0 if hbd == 0 else (0.5 if hbd == 1 else 0.0))
    if pka is not None:
        terms.append(band_score(pka, (7.5, 10.5), (6.5, 11.5)))
    return (sum(terms) / len(terms)) * 6.0

def main():
    df = pd.read_csv(INPUT_CSV)

    for col in [
        "MW", "cLogP", "logD7.4_est", "TPSA", "HBD", "HBA", "RotB",
        "logS_ESOL_est", "efflux_risk_0to2", "CNS_MPO_TE2052"
    ]:
        if col not in df.columns:
            df[col] = None

    for i, row in df.iterrows():
        smi = str(row["smiles"])
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            raise ValueError(f"Invalid SMILES at row {i}: {smi}")

        mw   = Descriptors.MolWt(mol)
        tpsa = rdMolDescriptors.CalcTPSA(mol)
        hbd  = rdMolDescriptors.CalcNumHBD(mol)
        hba  = rdMolDescriptors.CalcNumHBA(mol)
        rotb = rdMolDescriptors.CalcNumRotatableBonds(mol)
        clogp= Crippen.MolLogP(mol)

        logd = logD74_estimate(clogp, tpsa)
        logs = esol_logS_est(clogp, mw, rotb)
        eff  = efflux_risk_0to2(mw, logd, hbd, hba, tpsa)
        mpo  = cns_mpo_te2052(clogp, logd, mw, tpsa, hbd)

        df.at[i, "MW"] = mw
        df.at[i, "cLogP"] = clogp
        df.at[i, "logD7.4_est"] = logd
        df.at[i, "TPSA"] = tpsa
        df.at[i, "HBD"] = hbd
        df.at[i, "HBA"] = hba
        df.at[i, "RotB"] = rotb
        df.at[i, "logS_ESOL_est"] = logs
        df.at[i, "efflux_risk_0to2"] = eff
        df.at[i, "CNS_MPO_TE2052"] = mpo

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
