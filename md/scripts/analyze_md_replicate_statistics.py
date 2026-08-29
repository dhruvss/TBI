#!/usr/bin/env python3
"""Prespecified exploratory statistics for independent TSPO MD trajectories.

Only the three prespecified primary endpoints receive inferential tests. The
analysis contains no data-dependent endpoint selection or significance-driven
branching. Secondary endpoints are descriptive only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ANALYSIS_VERSION = "md-replicate-pipeline-1.0"
CANDIDATES = ("A3", "A7", "A8", "A15", "AC-5216")
ANALOGS = CANDIDATES[:-1]
REFERENCE = "AC-5216"
EXPECTED_REPLICATES = (1, 2, 3, 4, 5)
EXPECTED_FRAMES = 1000

PRIMARY = {
    "fixed_contacts_mean": "Mean fixed-pocket contact count",
    "com_to_pocket_mean_A": "Mean ligand COM-to-fixed-pocket-center distance",
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
FIGURE_LABELS = {
    "fixed_contacts_mean": "Mean fixed-pocket\ncontact count",
    "com_to_pocket_mean_A": "Mean COM-to-pocket-center\ndistance (Å)",
    "frames_fixed_contacts_ge10_pct": "Frames with ≥10 fixed-pocket\ncontacts (%)",
}


def validate_replicate_table(df: pd.DataFrame) -> pd.DataFrame:
    """Enforce the independent-trajectory design and reject frame-level input."""
    if {"frame", "time_ps", "time_ns"}.intersection(df.columns):
        raise ValueError("Frame-level input is prohibited for inferential statistics")
    required = {"candidate", "replicate", *PRIMARY, *SECONDARY}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Replicate table missing columns: {missing}")
    observed = set(df["candidate"])
    if observed != set(CANDIDATES):
        raise ValueError(f"Candidate set mismatch: expected {list(CANDIDATES)}, observed {sorted(observed)}")
    if df.duplicated(["candidate", "replicate"]).any():
        raise ValueError("Duplicate candidate-replicate keys detected")
    if len(df) != len(CANDIDATES) * len(EXPECTED_REPLICATES):
        raise ValueError("Expected exactly one row per independent trajectory (25 rows total)")
    for candidate in CANDIDATES:
        ids = set(df.loc[df["candidate"] == candidate, "replicate"])
        if ids != set(EXPECTED_REPLICATES):
            raise ValueError(f"{candidate}: expected replicate IDs {list(EXPECTED_REPLICATES)}, observed {sorted(ids)}")
    endpoints = list(PRIMARY) + list(SECONDARY)
    if not np.isfinite(df[endpoints].to_numpy(dtype=float)).all():
        raise ValueError("All primary and secondary endpoint values must be finite")
    order = {candidate: i for i, candidate in enumerate(CANDIDATES)}
    return df.assign(_order=df["candidate"].map(order)).sort_values(
        ["_order", "replicate"], kind="stable"
    ).drop(columns="_order").reset_index(drop=True)


def validate_provenance(manifest: pd.DataFrame) -> None:
    required = {
        "candidate", "replicate", "seed", "source_file", "frame_count",
        "time_min_ps", "time_max_ps", "analysis_script", "analysis_version",
    }
    missing = sorted(required - set(manifest.columns))
    if missing:
        raise ValueError(f"Provenance manifest missing columns: {missing}")
    keys = manifest[["candidate", "replicate"]]
    validate_keys = pd.DataFrame({
        "candidate": np.repeat(CANDIDATES, len(EXPECTED_REPLICATES)),
        "replicate": list(EXPECTED_REPLICATES) * len(CANDIDATES),
    })
    if keys.duplicated().any() or set(map(tuple, keys.to_numpy())) != set(map(tuple, validate_keys.to_numpy())):
        raise ValueError("Provenance candidate-replicate keys do not match the 5 x 5 design")
    if not (manifest["frame_count"] == EXPECTED_FRAMES).all():
        raise ValueError("Provenance must report exactly 1000 frames per trajectory")
    if not np.allclose(manifest["time_min_ps"], 10.0, rtol=0.0, atol=1e-3):
        raise ValueError("Provenance time_min_ps must be 10 ps for every trajectory")
    if not np.allclose(manifest["time_max_ps"], 10000.0, rtol=0.0, atol=1e-3):
        raise ValueError("Provenance time_max_ps must be 10000 ps for every trajectory")


def holm_adjust(pvalues: list[float] | np.ndarray) -> np.ndarray:
    pvalues = np.asarray(pvalues, dtype=float)
    if pvalues.ndim != 1 or len(pvalues) == 0 or not np.isfinite(pvalues).all():
        raise ValueError("Holm adjustment requires a nonempty finite one-dimensional array")
    if ((pvalues < 0.0) | (pvalues > 1.0)).any():
        raise ValueError("P-values must lie in [0, 1]")
    order = np.argsort(pvalues, kind="stable")
    adjusted_sorted = np.maximum.accumulate(
        np.minimum(1.0, (len(pvalues) - np.arange(len(pvalues))) * pvalues[order])
    )
    adjusted = np.empty_like(adjusted_sorted)
    adjusted[order] = adjusted_sorted
    return adjusted


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Positive values mean observations in x tend to exceed observations in y."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    comparisons = x[:, None] - y[None, :]
    return float((np.sum(comparisons > 0) - np.sum(comparisons < 0)) / comparisons.size)


def hedges_g(x: np.ndarray, y: np.ndarray) -> float:
    """Bias-corrected standardized mean difference; positive means x > y."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    nx, ny = len(x), len(y)
    degrees_freedom = nx + ny - 2
    pooled_variance = ((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / degrees_freedom
    if pooled_variance <= 0.0:
        return np.nan
    correction = 1.0 - 3.0 / (4.0 * degrees_freedom - 1.0)
    return float(correction * (np.mean(x) - np.mean(y)) / np.sqrt(pooled_variance))


def mann_whitney_prespecified(x: np.ndarray, y: np.ndarray) -> tuple[float, float, str, bool]:
    """Use exact inference absent cross-group ties; otherwise tie-corrected asymptotics."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    cross_group_ties = bool(np.intersect1d(x, y).size)
    method = "asymptotic_tie_corrected" if cross_group_ties else "exact"
    scipy_method = "asymptotic" if cross_group_ties else "exact"
    result = stats.mannwhitneyu(x, y, alternative="two-sided", method=scipy_method)
    return float(result.statistic), float(result.pvalue), method, cross_group_ties


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for endpoint, label in {**PRIMARY, **SECONDARY}.items():
        endpoint_class = "primary" if endpoint in PRIMARY else "secondary"
        for candidate in CANDIDATES:
            values = df.loc[df["candidate"] == candidate, endpoint].to_numpy(dtype=float)
            rows.append({
                "endpoint": endpoint, "endpoint_label": label,
                "endpoint_class": endpoint_class, "candidate": candidate,
                "n_independent_trajectories": len(values), "mean": np.mean(values),
                "sd": np.std(values, ddof=1), "median": np.median(values),
                "min": np.min(values), "max": np.max(values),
                "analysis_type": "descriptive",
            })
    return pd.DataFrame(rows)


def primary_omnibus_tests(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for endpoint, label in PRIMARY.items():
        groups = [df.loc[df["candidate"] == candidate, endpoint].to_numpy(dtype=float) for candidate in CANDIDATES]
        result = stats.kruskal(*groups)
        rows.append({
            "endpoint": endpoint, "endpoint_label": label, "test": "Kruskal-Wallis",
            "n_groups": len(CANDIDATES), "n_per_group": len(EXPECTED_REPLICATES),
            "H_statistic": result.statistic, "p_value": result.pvalue,
            "analysis_status": "exploratory",
        })
    return pd.DataFrame(rows)


def primary_reference_tests(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for endpoint, label in PRIMARY.items():
        reference = df.loc[df["candidate"] == REFERENCE, endpoint].to_numpy(dtype=float)
        endpoint_rows = []
        for analog in ANALOGS:
            values = df.loc[df["candidate"] == analog, endpoint].to_numpy(dtype=float)
            u_value, p_value, method, ties = mann_whitney_prespecified(values, reference)
            endpoint_rows.append({
                "endpoint": endpoint, "endpoint_label": label, "analog": analog,
                "reference": REFERENCE, "n_analog": len(values), "n_reference": len(reference),
                "analog_mean": np.mean(values), "reference_mean": np.mean(reference),
                "mean_difference_analog_minus_reference": np.mean(values) - np.mean(reference),
                "analog_median": np.median(values), "reference_median": np.median(reference),
                "mann_whitney_U": u_value, "two_sided_p_value": p_value,
                "mann_whitney_method": method, "cross_group_ties_present": ties,
                "hedges_g_analog_minus_reference": hedges_g(values, reference),
                "cliffs_delta_analog_vs_reference": cliffs_delta(values, reference),
                "holm_family": "four analog-vs-AC-5216 comparisons within endpoint",
                "analysis_status": "exploratory",
            })
        adjusted = holm_adjust([row["two_sided_p_value"] for row in endpoint_rows])
        for row, adjusted_p in zip(endpoint_rows, adjusted):
            row["holm_adjusted_p_value"] = adjusted_p
            rows.append(row)
    return pd.DataFrame(rows)


def make_primary_figure(df: pd.DataFrame, output_stem: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.2), constrained_layout=True)
    offsets = np.linspace(-0.16, 0.16, len(EXPECTED_REPLICATES))
    colors = ["#3B6FB6", "#4C956C", "#8C6BB1", "#D17A22", "#555555"]
    for axis, (endpoint, _) in zip(axes, PRIMARY.items()):
        for position, (candidate, color) in enumerate(zip(CANDIDATES, colors)):
            values = df.loc[df["candidate"] == candidate].sort_values("replicate")[endpoint].to_numpy(dtype=float)
            axis.scatter(position + offsets, values, s=34, color=color, edgecolor="white", linewidth=0.5, zorder=3)
            mean, sd = np.mean(values), np.std(values, ddof=1)
            axis.errorbar(position, mean, yerr=sd, fmt="_", markersize=16, color="black", capsize=4, linewidth=1.3, zorder=4)
        axis.set_xticks(range(len(CANDIDATES)), CANDIDATES, rotation=35, ha="right")
        axis.set_ylabel(FIGURE_LABELS[endpoint])
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", color="#dddddd", linewidth=0.6, zorder=0)
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_stem.with_suffix(".png"), dpi=600, bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def run_analysis(infile: Path, manifest_file: Path, outdir: Path) -> None:
    df = validate_replicate_table(pd.read_csv(infile))
    validate_provenance(pd.read_csv(manifest_file))
    outdir.mkdir(parents=True, exist_ok=True)
    desc = descriptive_statistics(df)
    desc.to_csv(outdir / "md_endpoint_descriptive_statistics.csv", index=False)
    desc.loc[desc["endpoint_class"] == "primary"].to_csv(
        outdir / "md_primary_endpoint_descriptive_statistics.csv", index=False
    )
    desc.loc[desc["endpoint_class"] == "secondary"].to_csv(
        outdir / "md_secondary_endpoint_descriptive_statistics.csv", index=False
    )
    primary_omnibus_tests(df).to_csv(outdir / "md_primary_endpoint_omnibus_tests.csv", index=False)
    primary_reference_tests(df).to_csv(outdir / "md_primary_endpoint_vs_AC-5216_statistics.csv", index=False)
    make_primary_figure(df, outdir / "md_primary_endpoints_replicate_values")


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    default_out = repo / "md" / "results_summary" / "replicated_v2"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--infile", type=Path, default=default_out / "md_replicate_master_summary.csv")
    parser.add_argument("--manifest", type=Path, default=default_out / "md_replicate_provenance_manifest.csv")
    parser.add_argument("--outdir", type=Path, default=default_out)
    args = parser.parse_args()
    run_analysis(args.infile.resolve(), args.manifest.resolve(), args.outdir.resolve())
    print(f"Completed prespecified primary analysis ({ANALYSIS_VERSION}) in {args.outdir}")


if __name__ == "__main__":
    main()
