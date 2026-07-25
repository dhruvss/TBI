#!/usr/bin/env python3
"""
12_admet_consensus.py

Merge pkCSM and SwissADME exports for A1-A17 plus AC-5216 and generate
an auditable ADMET triage table for downstream MD candidate selection.

Expected input files, relative to repository root:
    ADMET/pkCSM.csv
    ADMET/swissadme.csv

Expected SwissADME row mapping:
    Molecule 1  -> A1
    Molecule 2  -> A2
    ...
    Molecule 17 -> A17
    Molecule 18 -> AC-5216

Outputs:
    ADMET/admet_consensus_scored.csv
    ADMET/admet_decision_ranking.csv
    ADMET/admet_mapping_audit.csv

Important:
    These scores are only for in silico candidate triage. They are not
    experimental ADMET validation and should not be interpreted as absolute
    probabilities of safety, BBB penetration, or PET tracer success.
"""

from __future__ import annotations

from pathlib import Path
import sys
import re
import numpy as np
import pandas as pd


def repo_root_from_script() -> Path:
    """
    Resolve repository root assuming this script lives in src/.
    If run from somewhere else, fall back to the current working directory.
    """
    here = Path(__file__).resolve()

    if here.parent.name == "src":
        return here.parents[1]

    return Path.cwd().resolve()


PROJECT_ROOT = repo_root_from_script()
ADMET_DIR = PROJECT_ROOT / "ADMET"

PKCSM_PATH = ADMET_DIR / "pkCSM.csv"
SWISS_PATH = ADMET_DIR / "swissadme.csv"

OUT_SCORED = ADMET_DIR / "admet_consensus_scored.csv"
OUT_RANKING = ADMET_DIR / "admet_decision_ranking.csv"
OUT_AUDIT = ADMET_DIR / "admet_mapping_audit.csv"


def fail(msg: str) -> None:
    sys.exit(f"ERROR: {msg}")


def clean_yes_no(x) -> str:
    """
    Normalize categorical Yes/No fields while preserving nonstandard text.
    """
    if pd.isna(x):
        return ""

    s = str(x).strip()

    if s.lower() in {"yes", "y", "true", "1"}:
        return "Yes"

    if s.lower() in {"no", "n", "false", "0"}:
        return "No"

    return s


def to_num(series: pd.Series) -> pd.Series:
    """
    Convert a column to numeric, coercing non-numeric values such as 'n/d'
    to NaN.
    """
    return pd.to_numeric(series, errors="coerce")


def zscore(series: pd.Series) -> pd.Series:
    """
    Population z-score across the candidate set.

    If the column is constant or nearly all missing, return 0 for all rows
    rather than creating NaNs that contaminate the summed score.
    """
    s = to_num(series)
    mean = s.mean(skipna=True)
    sd = s.std(skipna=True, ddof=0)

    if pd.isna(sd) or sd == 0:
        return pd.Series(np.zeros(len(s)), index=s.index)

    return (s - mean) / sd


def molecule_to_compound(mol: str) -> str:
    """
    SwissADME exports rows as 'Molecule 1', 'Molecule 2', etc.

    User-verified mapping:
        Molecule 1-17 -> A1-A17
        Molecule 18   -> AC-5216
    """
    m = re.search(r"(\d+)", str(mol))

    if not m:
        fail(f"Could not parse SwissADME Molecule label: {mol}")

    n = int(m.group(1))

    if 1 <= n <= 17:
        return f"A{n}"

    if n == 18:
        return "AC-5216"

    fail(f"Unexpected SwissADME Molecule number: {n}")


def require_columns(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]

    if missing:
        fail(f"{label} is missing required columns: {missing}")


def compound_sort_key(compound: str) -> int:
    """
    Sort A1...A17 numerically, then AC-5216.
    """
    c = str(compound)
    m = re.fullmatch(r"A(\d+)", c)

    if m:
        return int(m.group(1))

    if c == "AC-5216":
        return 999

    return 500


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not PKCSM_PATH.is_file():
        fail(f"Missing pkCSM input file: {PKCSM_PATH}")

    if not SWISS_PATH.is_file():
        fail(f"Missing SwissADME input file: {SWISS_PATH}")

    pk = pd.read_csv(PKCSM_PATH)
    sw = pd.read_csv(SWISS_PATH)

    pk_required = [
        "Analog",
        "BBB permeability",
        "CNS permeability",
        "P-glycoprotein substrate",
        "AMES toxicity",
        "hERG I inhibitor",
        "hERG II inhibitor",
        "Hepatotoxicity",
    ]

    sw_required = [
        "Molecule",
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

    require_columns(pk, pk_required, "pkCSM.csv")
    require_columns(sw, sw_required, "swissadme.csv")

    pk = pk.copy()
    sw = sw.copy()

    pk["Compound"] = pk["Analog"].astype(str).str.strip()
    sw["Compound"] = sw["Molecule"].apply(molecule_to_compound)

    expected = [f"A{i}" for i in range(1, 18)] + ["AC-5216"]

    pk_seen = pk["Compound"].tolist()
    sw_seen = sw["Compound"].tolist()

    if pk_seen != expected:
        fail(
            "pkCSM row order or labels do not match expected A1-A17, AC-5216.\n"
            f"Observed: {pk_seen}"
        )

    if sw_seen != expected:
        fail(
            "SwissADME mapped row order does not match expected A1-A17, AC-5216.\n"
            f"Observed: {sw_seen}"
        )

    return pk, sw


def build_consensus(pk: pd.DataFrame, sw: pd.DataFrame) -> pd.DataFrame:
    merged = pk.merge(
        sw,
        on="Compound",
        how="inner",
        suffixes=("_pkcsm", "_swiss"),
        validate="one_to_one",
    )

    if len(merged) != 18:
        fail(f"Expected 18 merged compounds, got {len(merged)}")

    cat_cols = [
        "P-glycoprotein substrate",
        "AMES toxicity",
        "hERG I inhibitor",
        "hERG II inhibitor",
        "Hepatotoxicity",
        "BBB permeant",
        "Pgp substrate",
    ]

    for c in cat_cols:
        merged[c] = merged[c].apply(clean_yes_no)

    numeric_cols = [
        "BBB permeability",
        "CNS permeability",
        "Consensus Log P",
        "TPSA",
        "ESOL Log S",
        "Synthetic Accessibility",
        "PAINS #alerts",
        "Brenk #alerts",
        "MW",
    ]

    for c in numeric_cols:
        merged[c] = to_num(merged[c])

    # Continuous scoring:
    #
    # Each component is oriented so that higher means "better" for this
    # CNS/PET-tracer triage problem.
    #
    # BBB permeability:
    #   Higher pkCSM logBB is treated as more favorable.
    #
    # CNS permeability:
    #   Higher pkCSM logPS is treated as more favorable.
    #
    # Consensus LogP:
    #   Moderate lipophilicity is preferred. This script rewards closeness
    #   to 2.7 rather than rewarding unlimited increases in LogP.
    #
    # TPSA:
    #   Lower TPSA is generally more favorable for BBB penetration.
    #
    # ESOL LogS:
    #   Higher/more positive LogS is treated as better solubility.
    #
    # Synthetic Accessibility:
    #   Lower SwissADME SA is treated as easier synthesis.
    #
    # These are relative z-scores across this 18-compound set.
    merged["score_BBB_pkcsm_z"] = zscore(merged["BBB permeability"])
    merged["score_CNS_pkcsm_z"] = zscore(merged["CNS permeability"])

    logp_target = 2.7
    merged["logp_distance_from_target"] = (
        merged["Consensus Log P"] - logp_target
    ).abs()
    merged["score_logp_fit_z"] = zscore(-merged["logp_distance_from_target"])

    merged["score_TPSA_z"] = zscore(-merged["TPSA"])
    merged["score_ESOL_z"] = zscore(merged["ESOL Log S"])
    merged["score_synth_access_z"] = zscore(-merged["Synthetic Accessibility"])

    component_cols = [
        "score_BBB_pkcsm_z",
        "score_CNS_pkcsm_z",
        "score_logp_fit_z",
        "score_TPSA_z",
        "score_ESOL_z",
        "score_synth_access_z",
    ]

    merged["continuous_score"] = merged[component_cols].mean(axis=1)

    # Categorical penalties:
    #
    # AMES Yes              +2
    # Hepatotoxicity Yes    +2
    # hERG I Yes            +2
    # hERG II Yes           +1
    # PAINS alerts          +1 per alert
    # Brenk alerts          +0.5 per alert
    # SwissADME BBB No      +1
    #
    # P-gp is not penalized because pkCSM and SwissADME disagree scaffold-wide.
    # It is reported separately as pgp_consensus.
    merged["penalty_ames"] = np.where(
        merged["AMES toxicity"] == "Yes",
        2.0,
        0.0,
    )

    merged["penalty_hepatotoxicity"] = np.where(
        merged["Hepatotoxicity"] == "Yes",
        2.0,
        0.0,
    )

    merged["penalty_hERG_I"] = np.where(
        merged["hERG I inhibitor"] == "Yes",
        2.0,
        0.0,
    )

    merged["penalty_hERG_II"] = np.where(
        merged["hERG II inhibitor"] == "Yes",
        1.0,
        0.0,
    )

    merged["penalty_PAINS"] = merged["PAINS #alerts"].fillna(0) * 1.0
    merged["penalty_Brenk"] = merged["Brenk #alerts"].fillna(0) * 0.5

    merged["penalty_BBB_swiss_no"] = np.where(
        merged["BBB permeant"] == "No",
        1.0,
        0.0,
    )

    penalty_cols = [
        "penalty_ames",
        "penalty_hepatotoxicity",
        "penalty_hERG_I",
        "penalty_hERG_II",
        "penalty_PAINS",
        "penalty_Brenk",
        "penalty_BBB_swiss_no",
    ]

    merged["categorical_penalty"] = merged[penalty_cols].sum(axis=1)

    # The 0.35 factor keeps categorical warnings important without letting
    # universal scaffold-level flags, especially hERG II, dominate everything.
    merged["decision_score"] = (
        merged["continuous_score"] - 0.35 * merged["categorical_penalty"]
    )

    def pgp_label(row) -> str:
        pk_pgp = row["P-glycoprotein substrate"]
        sw_pgp = row["Pgp substrate"]

        if pk_pgp == sw_pgp:
            if pk_pgp == "Yes":
                return "Concordant P-gp substrate"

            if pk_pgp == "No":
                return "Concordant not P-gp substrate"

            return "Concordant unknown"

        return "Discordant"

    def bbb_label(row) -> str:
        sw_bbb = row["BBB permeant"]
        pk_bbb = row["BBB permeability"]
        pk_cns = row["CNS permeability"]

        # Coarse pkCSM support rule:
        # logBB > -1 and CNS permeability > -3 are treated as supportive.
        pk_supports = (
            pd.notna(pk_bbb)
            and pk_bbb > -1.0
            and pd.notna(pk_cns)
            and pk_cns > -3.0
        )

        if sw_bbb == "Yes" and pk_supports:
            return "Concordant favorable"

        if sw_bbb == "No" and not pk_supports:
            return "Concordant unfavorable"

        return "Discordant"

    merged["pgp_consensus"] = merged.apply(pgp_label, axis=1)
    merged["bbb_consensus"] = merged.apply(bbb_label, axis=1)

    role = {}

    for c in merged["Compound"]:
        role[c] = "Not selected for first-pass MD"

    role["AC-5216"] = "MD reference scaffold"
    role["A15"] = "MD lead: strongest ADMET/developability consensus"
    role["A3"] = "MD comparator: balanced clean-toxicity candidate"
    role["A7"] = "MD comparator: PBPK exposure-maximized stress test"
    role["A17"] = "Backup ADMET alternate"

    merged["md_panel_role"] = merged["Compound"].map(role)

    return merged


def write_outputs(
    merged: pd.DataFrame,
    pk: pd.DataFrame,
    sw: pd.DataFrame,
) -> None:
    ADMET_DIR.mkdir(parents=True, exist_ok=True)

    scored_cols = [
        "Compound",
        "Molecule",
        "Analog",
        "Canonical SMILES",
        "MW",
        "BBB permeability",
        "CNS permeability",
        "BBB permeant",
        "P-glycoprotein substrate",
        "Pgp substrate",
        "pgp_consensus",
        "bbb_consensus",
        "Consensus Log P",
        "TPSA",
        "ESOL Log S",
        "Synthetic Accessibility",
        "AMES toxicity",
        "hERG I inhibitor",
        "hERG II inhibitor",
        "Hepatotoxicity",
        "PAINS #alerts",
        "Brenk #alerts",
        "score_BBB_pkcsm_z",
        "score_CNS_pkcsm_z",
        "score_logp_fit_z",
        "score_TPSA_z",
        "score_ESOL_z",
        "score_synth_access_z",
        "continuous_score",
        "penalty_ames",
        "penalty_hepatotoxicity",
        "penalty_hERG_I",
        "penalty_hERG_II",
        "penalty_PAINS",
        "penalty_Brenk",
        "penalty_BBB_swiss_no",
        "categorical_penalty",
        "decision_score",
        "md_panel_role",
    ]

    scored = merged[scored_cols].copy()
    scored["__sort_key"] = scored["Compound"].apply(compound_sort_key)
    scored = scored.sort_values("__sort_key").drop(columns=["__sort_key"])
    scored.to_csv(OUT_SCORED, index=False)

    ranking_cols = [
        "Compound",
        "decision_score",
        "continuous_score",
        "categorical_penalty",
        "bbb_consensus",
        "pgp_consensus",
        "BBB permeability",
        "CNS permeability",
        "BBB permeant",
        "AMES toxicity",
        "hERG I inhibitor",
        "hERG II inhibitor",
        "Hepatotoxicity",
        "PAINS #alerts",
        "Brenk #alerts",
        "md_panel_role",
    ]

    ranking = merged[ranking_cols].copy()
    ranking = ranking.sort_values(
        ["decision_score", "continuous_score"],
        ascending=[False, False],
    )
    ranking.to_csv(OUT_RANKING, index=False)

    audit = pd.DataFrame(
        {
            "SwissADME_Molecule": sw["Molecule"],
            "Mapped_Compound": sw["Compound"],
            "pkCSM_Analog": pk["Compound"],
            "SwissADME_Canonical_SMILES": sw["Canonical SMILES"],
        }
    )

    audit["Mapping_OK"] = audit["Mapped_Compound"] == audit["pkCSM_Analog"]
    audit.to_csv(OUT_AUDIT, index=False)


def main() -> None:
    print(f"Repository root: {PROJECT_ROOT}")
    print(f"ADMET directory: {ADMET_DIR}")
    print(f"Reading: {PKCSM_PATH}")
    print(f"Reading: {SWISS_PATH}")

    pk, sw = load_inputs()
    merged = build_consensus(pk, sw)
    write_outputs(merged, pk, sw)

    print(f"Wrote: {OUT_SCORED}")
    print(f"Wrote: {OUT_RANKING}")
    print(f"Wrote: {OUT_AUDIT}")

    print("\nTop decision-ranking rows:")

    top = pd.read_csv(OUT_RANKING).head(8)

    print(
        top[
            [
                "Compound",
                "decision_score",
                "continuous_score",
                "categorical_penalty",
                "md_panel_role",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()