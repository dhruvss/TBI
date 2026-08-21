#!/usr/bin/env python3

from pathlib import Path
import itertools
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path("/Users/dhruv/Documents/Research/TBI")
INFILE = ROOT / "md/results_summary/replicated_v2/md_replicate_master_summary.csv"
OUTDIR = ROOT / "md/results_summary/replicated_v2"
OUTDIR.mkdir(parents=True, exist_ok=True)

ORDER = ["A3", "A7", "A8", "A15", "AC-5216"]

PRIMARY = {
    "fixed_contacts_mean": "Fixed-pocket contacts",
    "com_to_pocket_mean_A": "COM-to-pocket distance",
    "frames_fixed_contacts_ge10_pct": "Frames with >=10 fixed-pocket contacts",
}

SECONDARY = {
    "ligand_rmsd_mean_A": "Ligand heavy-atom RMSD",
    "ligand_rmsd_final2ns_mean_A": "Ligand RMSD final 2 ns",
    "all_min_distance_mean_A": "All-protein minimum distance",
    "protein_rmsd_mean_A": "Protein backbone RMSD",
    "fixed_contacts_final2ns_mean": "Fixed-pocket contacts final 2 ns",
    "com_to_pocket_final2ns_mean_A": "COM-to-pocket distance final 2 ns",
    "fixed_contacts_delta_final_minus_first": "Fixed-pocket contact drift",
    "com_delta_final_minus_first_A": "COM-to-pocket drift",
    "ligand_rmsd_delta_final_minus_first_A": "Ligand RMSD drift",
}

ALL_ENDPOINTS = {**PRIMARY, **SECONDARY}

df = pd.read_csv(INFILE)

# ------------------------------------------------------------
# Validate design
# ------------------------------------------------------------

missing_candidates = [c for c in ORDER if c not in df["candidate"].unique()]
if missing_candidates:
    raise ValueError(f"Missing candidates: {missing_candidates}")

counts = df.groupby("candidate")["replicate"].nunique()

if not (counts == 3).all():
    raise ValueError(
        "Expected exactly 3 independent trajectories per candidate.\n"
        f"Observed:\n{counts}"
    )

missing_cols = [x for x in ALL_ENDPOINTS if x not in df.columns]
if missing_cols:
    raise ValueError(f"Missing endpoint columns: {missing_cols}")

print("\nReplicate counts:")
print(counts)
print(f"\nTotal independent trajectories: {len(df)}")


# ------------------------------------------------------------
# Effect-size functions
# ------------------------------------------------------------

def hedges_g(x, y):
    """
    Standardized mean difference with small-sample correction.

    Positive:
        metric higher in group x.
    Negative:
        metric lower in group x.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    nx = len(x)
    ny = len(y)

    sx2 = np.var(x, ddof=1)
    sy2 = np.var(y, ddof=1)

    pooled_var = (
        ((nx - 1) * sx2 + (ny - 1) * sy2)
        / (nx + ny - 2)
    )

    if pooled_var <= 0:
        return np.nan

    pooled_sd = np.sqrt(pooled_var)

    d = (np.mean(x) - np.mean(y)) / pooled_sd

    dfree = nx + ny - 2
    J = 1 - (3 / (4 * dfree - 1))

    return J * d


def cliffs_delta(x, y):
    """
    Nonparametric effect size.

    +1:
        every x observation exceeds every y observation.

    -1:
        every x observation is below every y observation.

    0:
        no directional separation.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    greater = 0
    lower = 0

    for a in x:
        for b in y:
            if a > b:
                greater += 1
            elif a < b:
                lower += 1

    return (greater - lower) / (len(x) * len(y))


def holm_adjust(pvalues):
    """
    Holm step-down family-wise error correction.
    """

    pvalues = np.asarray(pvalues, dtype=float)

    order = np.argsort(pvalues)
    sorted_p = pvalues[order]

    m = len(sorted_p)
    adjusted_sorted = np.empty(m)

    running_max = 0.0

    for i, p in enumerate(sorted_p):
        adj = min(1.0, (m - i) * p)
        running_max = max(running_max, adj)
        adjusted_sorted[i] = running_max

    adjusted = np.empty(m)
    adjusted[order] = adjusted_sorted

    return adjusted


# ------------------------------------------------------------
# 1. Descriptive replicate-level statistics
# ------------------------------------------------------------

desc_rows = []

for metric, label in ALL_ENDPOINTS.items():

    for candidate in ORDER:

        x = (
            df.loc[df["candidate"] == candidate, metric]
            .dropna()
            .astype(float)
            .values
        )

        desc_rows.append({
            "endpoint": metric,
            "endpoint_label": label,
            "candidate": candidate,
            "n_independent_trajectories": len(x),
            "replicate_1": x[0] if len(x) > 0 else np.nan,
            "replicate_2": x[1] if len(x) > 1 else np.nan,
            "replicate_3": x[2] if len(x) > 2 else np.nan,
            "mean": np.mean(x),
            "sd": np.std(x, ddof=1),
            "median": np.median(x),
            "min": np.min(x),
            "max": np.max(x),
            "range": np.max(x) - np.min(x),
        })

desc = pd.DataFrame(desc_rows)

desc.to_csv(
    OUTDIR / "md_replicate_descriptive_statistics.csv",
    index=False
)


# ------------------------------------------------------------
# 2. Kruskal-Wallis omnibus tests
#
# Exploratory only:
# n = 3 independent trajectories per candidate.
# ------------------------------------------------------------

omnibus_rows = []

for metric, label in ALL_ENDPOINTS.items():

    groups = [
        df.loc[df["candidate"] == candidate, metric]
        .dropna()
        .astype(float)
        .values
        for candidate in ORDER
    ]

    H, p = stats.kruskal(*groups)

    omnibus_rows.append({
        "endpoint": metric,
        "endpoint_label": label,
        "test": "Kruskal-Wallis",
        "n_groups": len(groups),
        "n_per_group": 3,
        "H_statistic": H,
        "p_value": p,
        "analysis_status": "exploratory",
    })

omnibus = pd.DataFrame(omnibus_rows)

omnibus.to_csv(
    OUTDIR / "md_replicate_omnibus_tests.csv",
    index=False
)


# ------------------------------------------------------------
# 3. Pairwise exact Mann-Whitney U tests
# ------------------------------------------------------------

pairwise_rows = []

for metric, label in ALL_ENDPOINTS.items():

    for c1, c2 in itertools.combinations(ORDER, 2):

        x = (
            df.loc[df["candidate"] == c1, metric]
            .dropna()
            .astype(float)
            .values
        )

        y = (
            df.loc[df["candidate"] == c2, metric]
            .dropna()
            .astype(float)
            .values
        )

        U, p = stats.mannwhitneyu(
            x,
            y,
            alternative="two-sided",
            method="exact",
        )

        pairwise_rows.append({
            "endpoint": metric,
            "endpoint_label": label,
            "candidate_1": c1,
            "candidate_2": c2,
            "n_1": len(x),
            "n_2": len(y),

            "mean_1": np.mean(x),
            "mean_2": np.mean(y),
            "mean_difference_1_minus_2":
                np.mean(x) - np.mean(y),

            "median_1": np.median(x),
            "median_2": np.median(y),

            "mann_whitney_U": U,
            "exact_p_value": p,

            "hedges_g_1_minus_2":
                hedges_g(x, y),

            "cliffs_delta_1_vs_2":
                cliffs_delta(x, y),

            "analysis_status": "exploratory",
        })

pairwise = pd.DataFrame(pairwise_rows)


# ------------------------------------------------------------
# Holm correction within each endpoint
# ------------------------------------------------------------

pairwise["holm_p_all_pairs"] = np.nan

for metric in pairwise["endpoint"].unique():

    mask = pairwise["endpoint"] == metric

    pairwise.loc[
        mask,
        "holm_p_all_pairs"
    ] = holm_adjust(
        pairwise.loc[mask, "exact_p_value"].values
    )

pairwise.to_csv(
    OUTDIR / "md_replicate_pairwise_all_statistics.csv",
    index=False
)


# ------------------------------------------------------------
# 4. Benchmark-focused comparisons vs AC-5216
#
# These are the most biologically relevant pairwise comparisons.
# Holm correction is performed only across the four analog-vs-reference
# comparisons within each endpoint.
# ------------------------------------------------------------

reference_rows = []

for metric, label in ALL_ENDPOINTS.items():

    ref = (
        df.loc[df["candidate"] == "AC-5216", metric]
        .dropna()
        .astype(float)
        .values
    )

    endpoint_rows = []

    for candidate in ["A3", "A7", "A8", "A15"]:

        x = (
            df.loc[df["candidate"] == candidate, metric]
            .dropna()
            .astype(float)
            .values
        )

        U, p = stats.mannwhitneyu(
            x,
            ref,
            alternative="two-sided",
            method="exact",
        )

        endpoint_rows.append({
            "endpoint": metric,
            "endpoint_label": label,
            "analog": candidate,
            "reference": "AC-5216",

            "analog_mean": np.mean(x),
            "reference_mean": np.mean(ref),

            "mean_difference_analog_minus_reference":
                np.mean(x) - np.mean(ref),

            "analog_median": np.median(x),
            "reference_median": np.median(ref),

            "mann_whitney_U": U,
            "exact_p_value": p,

            "hedges_g_analog_minus_reference":
                hedges_g(x, ref),

            "cliffs_delta_analog_vs_reference":
                cliffs_delta(x, ref),
        })

    raw_p = [row["exact_p_value"] for row in endpoint_rows]
    adjusted = holm_adjust(raw_p)

    for row, adj in zip(endpoint_rows, adjusted):
        row["holm_p_vs_reference"] = adj
        row["analysis_status"] = "exploratory"
        reference_rows.append(row)

reference = pd.DataFrame(reference_rows)

reference.to_csv(
    OUTDIR / "md_replicate_vs_AC5216_statistics.csv",
    index=False
)


# ------------------------------------------------------------
# 5. Primary endpoint outputs only
# ------------------------------------------------------------

primary_desc = desc[
    desc["endpoint"].isin(PRIMARY.keys())
].copy()

primary_omnibus = omnibus[
    omnibus["endpoint"].isin(PRIMARY.keys())
].copy()

primary_ref = reference[
    reference["endpoint"].isin(PRIMARY.keys())
].copy()

primary_desc.to_csv(
    OUTDIR / "md_primary_endpoint_descriptive_statistics.csv",
    index=False
)

primary_omnibus.to_csv(
    OUTDIR / "md_primary_endpoint_omnibus_tests.csv",
    index=False
)

primary_ref.to_csv(
    OUTDIR / "md_primary_endpoint_vs_AC5216_statistics.csv",
    index=False
)


# ------------------------------------------------------------
# 6. Replicate consistency table
#
# Reports ranking across the three trajectories for each endpoint.
# No significance testing.
# ------------------------------------------------------------

consistency_rows = []

for metric, label in PRIMARY.items():

    tmp = df[
        ["candidate", "replicate", metric]
    ].copy()

    for rep in sorted(tmp["replicate"].unique()):

        r = tmp[tmp["replicate"] == rep].copy()

        ascending = metric == "com_to_pocket_mean_A"

        r["rank"] = r[metric].rank(
            method="average",
            ascending=ascending,
        )

        for _, row in r.iterrows():

            consistency_rows.append({
                "endpoint": metric,
                "endpoint_label": label,
                "candidate": row["candidate"],
                "replicate": rep,
                "value": row[metric],
                "rank_within_replicate": row["rank"],
            })

consistency = pd.DataFrame(consistency_rows)

consistency.to_csv(
    OUTDIR / "md_primary_endpoint_replicate_rank_consistency.csv",
    index=False
)


# ------------------------------------------------------------
# Console output
# ------------------------------------------------------------

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

print("\n" + "=" * 90)
print("PRIMARY ENDPOINT DESCRIPTIVE STATISTICS")
print("=" * 90)

print(
    primary_desc[
        [
            "endpoint_label",
            "candidate",
            "replicate_1",
            "replicate_2",
            "replicate_3",
            "mean",
            "sd",
            "median",
            "min",
            "max",
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 90)
print("PRIMARY ENDPOINT KRUSKAL-WALLIS TESTS")
print("Exploratory only; independent trajectory is the unit of replication.")
print("=" * 90)

print(
    primary_omnibus[
        [
            "endpoint_label",
            "H_statistic",
            "p_value",
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 90)
print("PRIMARY ENDPOINT COMPARISONS VS AC-5216")
print("Exact Mann-Whitney + Holm correction + effect sizes")
print("=" * 90)

print(
    primary_ref[
        [
            "endpoint_label",
            "analog",
            "analog_mean",
            "reference_mean",
            "mean_difference_analog_minus_reference",
            "exact_p_value",
            "holm_p_vs_reference",
            "hedges_g_analog_minus_reference",
            "cliffs_delta_analog_vs_reference",
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 90)
print("FILES WRITTEN")
print("=" * 90)

for name in [
    "md_replicate_descriptive_statistics.csv",
    "md_replicate_omnibus_tests.csv",
    "md_replicate_pairwise_all_statistics.csv",
    "md_replicate_vs_AC5216_statistics.csv",
    "md_primary_endpoint_descriptive_statistics.csv",
    "md_primary_endpoint_omnibus_tests.csv",
    "md_primary_endpoint_vs_AC5216_statistics.csv",
    "md_primary_endpoint_replicate_rank_consistency.csv",
]:
    print(OUTDIR / name)