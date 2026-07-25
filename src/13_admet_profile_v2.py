#!/usr/bin/env python3
"""
13_admet_profile_v2.py

Transparent ADMET profile merger for the canonical TSPO analog set.

This replaces the historical composite ADMET scoring workflow. It does not
calculate z-scores, weighted penalties, an overall decision score, or an MD
ranking. Synthetic accessibility is retained only as a separate
developability field.

Default inputs, relative to the repository root:
    ADMET/pkCSM.csv
    ADMET/swissadme.csv

Default outputs:
    ADMET/admet_raw_merged_v2.csv
    ADMET/admet_canonical_profile_v2.csv
    ADMET/admet_duplicate_audit_v2.csv
    ADMET/admet_identity_audit_v2.csv

Expected canonical record labels:
    A1-A15, A1_2, A8_2, AC-5216
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import pandas as pd

try:
    from rdkit import Chem
except Exception as exc:
    Chem = None
    RDKIT_IMPORT_ERROR = exc
else:
    RDKIT_IMPORT_ERROR = None


CANONICAL_RECORD_ORDER = (
    [f"A{i}" for i in range(1, 9)]
    + ["A1_2"]
    + [f"A{i}" for i in range(9, 14)]
    + ["A8_2", "A14", "A15", "AC-5216"]
)
PRIMARY_CANONICAL_ORDER = [f"A{i}" for i in range(1, 16)] + ["AC-5216"]
DUPLICATE_PARENT = {"A1_2": "A1", "A8_2": "A8"}

PKCSM_REQUIRED = [
    "BBB permeability",
    "CNS permeability",
    "P-glycoprotein substrate",
    "AMES toxicity",
    "hERG I inhibitor",
    "hERG II inhibitor",
    "Hepatotoxicity",
]
SWISS_REQUIRED = [
    "Canonical SMILES",
    "MW",
    "TPSA",
    "Consensus Log P",
    "ESOL Log S",
    "BBB permeant",
    "Pgp substrate",
    "PAINS #alerts",
    "Brenk #alerts",
    "Synthetic Accessibility",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def repo_root_from_script() -> Path:
    here = Path(__file__).resolve()
    if here.parent.name == "src":
        return here.parents[1]
    return Path.cwd().resolve()


def clean_yes_no(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"yes", "y", "true", "1"}:
        return "Yes"
    if text.lower() in {"no", "n", "false", "0"}:
        return "No"
    return text


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def require_columns(df: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        fail(f"{label} is missing required columns: {missing}")


def normalize_record_id(value: str) -> str:
    text = str(value).strip().replace(" ", "")
    if text.upper() in {"AC5216", "AC-5216"}:
        return "AC-5216"
    if text.upper() == "A1_2":
        return "A1_2"
    if text.upper() == "A8_2":
        return "A8_2"
    match = re.fullmatch(r"A(\d+)", text, flags=re.IGNORECASE)
    if match:
        return f"A{int(match.group(1))}"
    return str(value).strip()


def infer_record_ids(df: pd.DataFrame, source: str) -> pd.Series:
    for column in ["Compound", "Analog", "Candidate", "ID", "Name"]:
        if column in df.columns:
            normalized = df[column].astype(str).str.strip().map(normalize_record_id)
            if set(normalized).issubset(set(CANONICAL_RECORD_ORDER)):
                return normalized

    if "Molecule" in df.columns:
        labels = df["Molecule"].astype(str).str.strip()
        direct = labels.map(normalize_record_id)
        if set(direct).issubset(set(CANONICAL_RECORD_ORDER)):
            return direct

        numbers = []
        for value in labels:
            match = re.search(r"(\d+)", value)
            if not match:
                break
            numbers.append(int(match.group(1)))

        if numbers == list(range(1, 19)):
            return pd.Series(CANONICAL_RECORD_ORDER, index=df.index)

    fail(
        f"Could not infer canonical record IDs for {source}. "
        "Add a Compound or Analog column using A1-A15, A1_2, A8_2, AC-5216."
    )


def canonicalize_smiles(smiles: str) -> tuple[str, str]:
    if Chem is None:
        fail(f"RDKit is required for identity validation: {RDKIT_IMPORT_ERROR}")
    mol = Chem.MolFromSmiles(str(smiles).strip())
    if mol is None:
        fail(f"RDKit could not parse SMILES: {smiles}")
    return Chem.MolToSmiles(mol, canonical=True), Chem.MolToInchiKey(mol)


def classify_bbb(row: pd.Series) -> str:
    logbb = row["BBB permeability"]
    logps = row["CNS permeability"]
    swiss = row["BBB permeant"]
    pk_support = (
        pd.notna(logbb)
        and pd.notna(logps)
        and float(logbb) > -1.0
        and float(logps) > -3.0
    )
    if swiss == "Yes" and pk_support:
        return "Concordant supportive"
    if swiss == "No" and not pk_support:
        return "Concordant nonsupportive"
    return "Discordant"


def classify_pgp(row: pd.Series) -> str:
    pk = row["P-glycoprotein substrate"]
    swiss = row["Pgp substrate"]
    if pk == "Yes" and swiss == "Yes":
        return "Concordant substrate"
    if pk == "No" and swiss == "No":
        return "Concordant non-substrate"
    return "Discordant"


def safety_alerts(row: pd.Series) -> str:
    alerts = []
    for column, label in [
        ("AMES toxicity", "Ames"),
        ("hERG I inhibitor", "hERG I"),
        ("hERG II inhibitor", "hERG II"),
        ("Hepatotoxicity", "Hepatotoxicity"),
    ]:
        if row[column] == "Yes":
            alerts.append(label)
    return "; ".join(alerts) if alerts else "None"


def compound_sort_key(record_id: str) -> tuple[int, int]:
    if record_id == "AC-5216":
        return (999, 0)
    if record_id == "A1_2":
        return (1, 1)
    if record_id == "A8_2":
        return (8, 1)
    match = re.fullmatch(r"A(\d+)", record_id)
    if match:
        return (int(match.group(1)), 0)
    return (500, 0)


def main() -> None:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(
        description="Create a transparent canonical ADMET profile without composite scoring."
    )
    parser.add_argument("--pkcsm", default=str(root / "ADMET" / "pkCSM.csv"))
    parser.add_argument("--swissadme", default=str(root / "ADMET" / "swissadme.csv"))
    parser.add_argument("--outdir", default=str(root / "ADMET"))
    args = parser.parse_args()

    pk_path = Path(args.pkcsm).expanduser().resolve()
    sw_path = Path(args.swissadme).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()

    if not pk_path.is_file():
        fail(f"Missing pkCSM file: {pk_path}")
    if not sw_path.is_file():
        fail(f"Missing SwissADME file: {sw_path}")

    pk = pd.read_csv(pk_path)
    sw = pd.read_csv(sw_path)
    require_columns(pk, PKCSM_REQUIRED, "pkCSM.csv")
    require_columns(sw, SWISS_REQUIRED, "swissadme.csv")

    pk = pk.copy()
    sw = sw.copy()
    pk["Record_ID"] = infer_record_ids(pk, "pkCSM.csv")
    sw["Record_ID"] = infer_record_ids(sw, "swissadme.csv")

    if pk["Record_ID"].duplicated().any():
        fail(f"pkCSM duplicated labels: {pk.loc[pk['Record_ID'].duplicated(False), 'Record_ID'].tolist()}")
    if sw["Record_ID"].duplicated().any():
        fail(f"SwissADME duplicated labels: {sw.loc[sw['Record_ID'].duplicated(False), 'Record_ID'].tolist()}")

    expected = set(CANONICAL_RECORD_ORDER)
    if set(pk["Record_ID"]) != expected:
        fail(
            "pkCSM record set does not match expected 18 records.\n"
            f"Missing: {sorted(expected - set(pk['Record_ID']))}\n"
            f"Unexpected: {sorted(set(pk['Record_ID']) - expected)}"
        )
    if set(sw["Record_ID"]) != expected:
        fail(
            "SwissADME record set does not match expected 18 records.\n"
            f"Missing: {sorted(expected - set(sw['Record_ID']))}\n"
            f"Unexpected: {sorted(set(sw['Record_ID']) - expected)}"
        )

    merged = pk.merge(
        sw,
        on="Record_ID",
        how="inner",
        suffixes=("_pkCSM", "_SwissADME"),
        validate="one_to_one",
    )

    for column in [
        "P-glycoprotein substrate",
        "AMES toxicity",
        "hERG I inhibitor",
        "hERG II inhibitor",
        "Hepatotoxicity",
        "BBB permeant",
        "Pgp substrate",
    ]:
        merged[column] = merged[column].map(clean_yes_no)

    for column in [
        "BBB permeability",
        "CNS permeability",
        "MW",
        "TPSA",
        "Consensus Log P",
        "ESOL Log S",
        "PAINS #alerts",
        "Brenk #alerts",
        "Synthetic Accessibility",
    ]:
        merged[column] = to_numeric(merged[column])

    canonical_smiles = []
    inchikeys = []
    for smiles in merged["Canonical SMILES"]:
        canonical, key = canonicalize_smiles(smiles)
        canonical_smiles.append(canonical)
        inchikeys.append(key)

    merged["RDKit_Canonical_SMILES"] = canonical_smiles
    merged["InChIKey"] = inchikeys
    merged["Canonical_ID"] = merged["Record_ID"].map(lambda x: DUPLICATE_PARENT.get(x, x))
    merged["Duplicate_Status"] = merged["Record_ID"].map(
        lambda x: (
            f"Technical duplicate of {DUPLICATE_PARENT[x]}"
            if x in DUPLICATE_PARENT
            else "Primary canonical record"
        )
    )

    for duplicate, parent in DUPLICATE_PARENT.items():
        duplicate_key = merged.loc[merged["Record_ID"] == duplicate, "InChIKey"].iloc[0]
        parent_key = merged.loc[merged["Record_ID"] == parent, "InChIKey"].iloc[0]
        if duplicate_key != parent_key:
            fail(f"{duplicate} does not match {parent} by InChIKey")

    merged["BBB_Model_Consensus"] = merged.apply(classify_bbb, axis=1)
    merged["Pgp_Model_Consensus"] = merged.apply(classify_pgp, axis=1)
    merged["Safety_Alerts"] = merged.apply(safety_alerts, axis=1)
    merged["Medicinal_Chemistry_Alerts"] = (
        "PAINS="
        + merged["PAINS #alerts"].fillna(0).astype(int).astype(str)
        + "; Brenk="
        + merged["Brenk #alerts"].fillna(0).astype(int).astype(str)
    )
    merged["Synthetic_Accessibility_Use"] = (
        "Separate synthesis/developability field; excluded from ADMET ranking"
    )

    merged["__sort"] = merged["Record_ID"].map(compound_sort_key)
    merged = merged.sort_values("__sort").drop(columns="__sort")

    raw_columns = [
        "Record_ID",
        "Canonical_ID",
        "Duplicate_Status",
        "RDKit_Canonical_SMILES",
        "InChIKey",
        "BBB permeability",
        "CNS permeability",
        "BBB permeant",
        "BBB_Model_Consensus",
        "P-glycoprotein substrate",
        "Pgp substrate",
        "Pgp_Model_Consensus",
        "Consensus Log P",
        "TPSA",
        "ESOL Log S",
        "AMES toxicity",
        "hERG I inhibitor",
        "hERG II inhibitor",
        "Hepatotoxicity",
        "Safety_Alerts",
        "PAINS #alerts",
        "Brenk #alerts",
        "Medicinal_Chemistry_Alerts",
        "Synthetic Accessibility",
        "Synthetic_Accessibility_Use",
        "MW",
    ]

    outdir.mkdir(parents=True, exist_ok=True)
    raw_out = outdir / "admet_raw_merged_v2.csv"
    profile_out = outdir / "admet_canonical_profile_v2.csv"
    duplicate_out = outdir / "admet_duplicate_audit_v2.csv"
    identity_out = outdir / "admet_identity_audit_v2.csv"

    merged[raw_columns].to_csv(raw_out, index=False)

    primary = merged[merged["Record_ID"].isin(PRIMARY_CANONICAL_ORDER)].copy()
    primary["__sort"] = primary["Record_ID"].map(compound_sort_key)
    primary = primary.sort_values("__sort").drop(columns="__sort")
    primary[raw_columns].to_csv(profile_out, index=False)

    duplicate_rows = []
    compare_columns = [
        "BBB permeability",
        "CNS permeability",
        "BBB permeant",
        "P-glycoprotein substrate",
        "Pgp substrate",
        "Consensus Log P",
        "TPSA",
        "ESOL Log S",
        "AMES toxicity",
        "hERG I inhibitor",
        "hERG II inhibitor",
        "Hepatotoxicity",
        "PAINS #alerts",
        "Brenk #alerts",
        "Synthetic Accessibility",
    ]
    for duplicate, parent in DUPLICATE_PARENT.items():
        drow = merged.loc[merged["Record_ID"] == duplicate].iloc[0]
        prow = merged.loc[merged["Record_ID"] == parent].iloc[0]
        for column in compare_columns:
            same = (pd.isna(drow[column]) and pd.isna(prow[column])) or drow[column] == prow[column]
            duplicate_rows.append(
                {
                    "Canonical_ID": parent,
                    "Primary_Record": parent,
                    "Duplicate_Record": duplicate,
                    "Endpoint": column,
                    "Primary_Value": prow[column],
                    "Duplicate_Value": drow[column],
                    "Exact_Match": "Yes" if same else "No",
                    "Interpretation": (
                        ""
                        if same
                        else "Identical structure yielded discordant prediction; treat as model/run uncertainty"
                    ),
                }
            )
    pd.DataFrame(duplicate_rows).to_csv(duplicate_out, index=False)

    identity = merged[
        [
            "Record_ID",
            "Canonical_ID",
            "Duplicate_Status",
            "RDKit_Canonical_SMILES",
            "InChIKey",
        ]
    ].copy()
    identity["Identity_Check"] = "Passed"
    identity.to_csv(identity_out, index=False)

    print(f"Wrote: {raw_out}")
    print(f"Wrote: {profile_out}")
    print(f"Wrote: {duplicate_out}")
    print(f"Wrote: {identity_out}")
    print("No composite ADMET score was calculated.")


if __name__ == "__main__":
    main()
