#!/usr/bin/env python3

import json
import time
from pathlib import Path

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rdkit import Chem
from rdkit.Chem import Crippen, rdMolDescriptors


OUTDIR = Path("ADMET/ref_logd_proxy_correlation")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Experimental logD values from reference table.
# PBR-111 and DAA1106 are retained for descriptor retrieval but excluded from correlation.
REFS = [
    {
        "tracer": "PK11195",
        "pubchem_queries": ["PK11195", "PK 11195", "Ro5-4864"],
        "experimental_logD7_4": 4.58,
        "logD_note": "Pike 2009; Shah et al. 1994",
    },
    {
        "tracer": "DPA-713",
        "pubchem_queries": ["DPA-713"],
        "experimental_logD7_4": 2.41,
        "logD_note": "Owen et al. displayed/reported value; Luu et al. 2022 secondary extrapolated support",
    },
    {
        "tracer": "PBR-28",
        "pubchem_queries": ["PBR28", "PBR-28"],
        "experimental_logD7_4": 3.01,
        "logD_note": "Imaizumi et al. 2009",
    },
    {
        "tracer": "GE-180",
        "pubchem_queries": ["GE-180", "flutriciclamide"],
        "experimental_logD7_4": 2.95,
        "logD_note": "Wadsworth et al. 2012; Wickstrom et al. 2014",
    },
    {
        "tracer": "AC-5216",
        "pubchem_queries": ["AC-5216", "emapunil", "XBD173"],
        "experimental_logD7_4": 3.30,
        "logD_note": "Zhang et al. 2021",
    },
    {
        "tracer": "PBR-111",
        "pubchem_queries": ["PBR111", "PBR-111"],
        "experimental_logD7_4": np.nan,
        "logD_note": "NA in reference table",
    },
    {
        "tracer": "PBR-O6",
        "pubchem_queries": ["PBR06", "PBR-06", "PBR O6", "PBR-O6"],
        "experimental_logD7_4": 4.05,
        "logD_note": "Imaizumi et al. 2009",
    },
    {
        "tracer": "DAA1106",
        "pubchem_queries": ["DAA1106", "DAA-1106"],
        "experimental_logD7_4": np.nan,
        "logD_note": "NA in reference table",
    },
]


def pug_get_json(url):
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return None
    return r.json()


def resolve_pubchem(query):
    q = requests.utils.quote(query)
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{q}/cids/JSON"
    data = pug_get_json(url)
    if not data:
        return None
    try:
        return data["IdentifierList"]["CID"][0]
    except Exception:
        return None


def fetch_properties(cid):
    props = "CanonicalSMILES,IsomericSMILES,XLogP,TPSA,MolecularFormula,MolecularWeight"
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{props}/JSON"
    data = pug_get_json(url)
    if not data:
        return None
    try:
        return data["PropertyTable"]["Properties"][0]
    except Exception:
        return None


def fetch_pubchem_sdf_mol(cid):
    """Fetch PubChem 2D SDF and parse with RDKit."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF"
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return None
    mol = Chem.MolFromMolBlock(r.text, sanitize=True, removeHs=False)
    return mol


def mol_from_smiles(smiles):
    if not smiles or not isinstance(smiles, str):
        return None
    mol = Chem.MolFromSmiles(smiles)
    return mol


def pearson(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    xr = pd.Series(x).rank(method="average")
    yr = pd.Series(y).rank(method="average")
    return pearson(xr, yr)


rows = []

for ref in REFS:
    cid = None
    used_query = None
    props = None

    for query in ref["pubchem_queries"]:
        cid = resolve_pubchem(query)
        if cid is not None:
            props = fetch_properties(cid)
            if props is not None:
                used_query = query
                break
        time.sleep(0.2)

    row = {
        "tracer": ref["tracer"],
        "pubchem_query_used": used_query,
        "pubchem_cid": cid,
        "experimental_logD7_4": ref["experimental_logD7_4"],
        "logD_note": ref["logD_note"],
        "pubchem_fetch_status": "ok" if props else "failed",
    }

    if props:
        smiles = props.get("CanonicalSMILES") or props.get("IsomericSMILES")
        mol = mol_from_smiles(smiles)

        # Some PubChem property responses omit SMILES even when XLogP/TPSA are present.
        # Fall back to PubChem SDF parsing so RDKit descriptors are still reproducible.
        if mol is None and cid is not None:
            mol = fetch_pubchem_sdf_mol(cid)

        row.update(
            {
                "canonical_smiles": smiles,
                "pubchem_XLogP": props.get("XLogP", np.nan),
                "pubchem_TPSA": props.get("TPSA", np.nan),
                "molecular_formula": props.get("MolecularFormula"),
                "molecular_weight": props.get("MolecularWeight", np.nan),
            }
        )

        if mol is not None:
            rdkit_clogP = float(Crippen.MolLogP(mol))
            rdkit_TPSA = float(rdMolDescriptors.CalcTPSA(mol))
            row.update(
                {
                    "rdkit_clogP": rdkit_clogP,
                    "rdkit_TPSA": rdkit_TPSA,
                    "logD7_4_EST_rdkit": rdkit_clogP - rdkit_TPSA / 120.0,
                }
            )
        else:
            row.update(
                {
                    "rdkit_clogP": np.nan,
                    "rdkit_TPSA": np.nan,
                    "logD7_4_EST_rdkit": np.nan,
                }
            )
    else:
        row.update(
            {
                "canonical_smiles": None,
                "pubchem_XLogP": np.nan,
                "pubchem_TPSA": np.nan,
                "molecular_formula": None,
                "molecular_weight": np.nan,
                "rdkit_clogP": np.nan,
                "rdkit_TPSA": np.nan,
                "logD7_4_EST_rdkit": np.nan,
            }
        )

    rows.append(row)


df = pd.DataFrame(rows)

# PubChem-based polarity-adjusted proxy.
# This is useful if RDKit SMILES parsing fails but PubChem XLogP/TPSA are available.
if "pubchem_XLogP" in df.columns and "pubchem_TPSA" in df.columns:
    df["logD7_4_EST_pubchem"] = pd.to_numeric(df["pubchem_XLogP"], errors="coerce") - (
        pd.to_numeric(df["pubchem_TPSA"], errors="coerce") / 120.0
    )
else:
    df["logD7_4_EST_pubchem"] = np.nan

df.to_csv(OUTDIR / "reference_tracer_descriptors.csv", index=False)


def correlation_block(label, data):
    out = []
    out.append(f"## {label}")
    out.append("")

    predictors = ["logD7_4_EST_rdkit", "logD7_4_EST_pubchem", "rdkit_clogP", "pubchem_XLogP"]

    plot_clean = None

    for pred in predictors:
        clean = data.dropna(subset=["experimental_logD7_4", pred]).copy()

        out.append(f"{pred} vs experimental_logD7_4")
        out.append(f"n = {len(clean)}")

        if len(clean) >= 3:
            x = clean[pred].astype(float)
            y = clean["experimental_logD7_4"].astype(float)
            mae = float(np.mean(np.abs(x - y)))
            rmse = float(np.sqrt(np.mean((x - y) ** 2)))

            out.append(f"  Pearson r:  {pearson(x, y):.3f}")
            out.append(f"  Spearman r: {spearman(x, y):.3f}")
            out.append(f"  MAE:        {mae:.3f}")
            out.append(f"  RMSE:       {rmse:.3f}")

            if pred == "logD7_4_EST_rdkit":
                plot_clean = clean.copy()
        else:
            out.append("  Not enough usable tracers for correlation.")

        out.append("")
        out.append("  Tracers included:")
        if len(clean) > 0:
            cols = ["tracer", "experimental_logD7_4", "rdkit_clogP", "rdkit_TPSA", "logD7_4_EST_rdkit", "pubchem_XLogP", "pubchem_TPSA", "logD7_4_EST_pubchem"]
            out.append(clean[cols].to_string(index=False))
        else:
            out.append("  None")
        out.append("")

    if plot_clean is None:
        plot_clean = data.dropna(subset=["experimental_logD7_4", "logD7_4_EST_rdkit"]).copy()

    return "\n".join(out), plot_clean


all_text, all_clean = correlation_block("All tracers with experimental logD", df)
no_dpa_text, no_dpa_clean = correlation_block("Sensitivity analysis excluding DPA-713 because one secondary source was extrapolated", df[df["tracer"] != "DPA-713"])

summary = "\n\n".join([all_text, no_dpa_text])
(OUTDIR / "reference_logd_correlation_summary.txt").write_text(summary + "\n")

print(summary)


def scatter_plot(clean, pred, outname, title):
    if len(clean) < 3:
        return

    x = clean[pred].astype(float)
    y = clean["experimental_logD7_4"].astype(float)

    plt.figure(figsize=(5.5, 4.5))
    plt.scatter(x, y)

    for _, r in clean.iterrows():
        plt.annotate(r["tracer"], (r[pred], r["experimental_logD7_4"]), fontsize=8, xytext=(4, 4), textcoords="offset points")

    lo = float(min(x.min(), y.min())) - 0.3
    hi = float(max(x.max(), y.max())) + 0.3
    plt.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1)

    plt.xlabel(pred)
    plt.ylabel("Experimental logD7.4")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(OUTDIR / outname, dpi=300)
    plt.close()


scatter_plot(all_clean, "logD7_4_EST_pubchem", "scatter_experimental_vs_logD7_4_EST_pubchem_all.png", "Experimental logD7.4 vs PubChem polarity-adjusted proxy")
scatter_plot(all_clean, "rdkit_clogP", "scatter_experimental_vs_rdkit_clogP_all.png", "Experimental logD7.4 vs RDKit clogP")
scatter_plot(no_dpa_clean, "logD7_4_EST_pubchem", "scatter_experimental_vs_logD7_4_EST_pubchem_no_DPA713.png", "Experimental logD7.4 vs PubChem proxy, excluding DPA-713")

print(f"\nWrote outputs to: {OUTDIR}")
