#!/usr/bin/env python3
"""Run the prespecified eight-scenario PBPK ranking sensitivity analysis.

The 17 analogs define all z-score means and sample standard deviations. The
AC5216 reference is transformed with those fixed analog statistics but is not
included in primary ranks, correlations, or top-k overlap calculations.

Ranks are deterministic ordinal ranks: scores are sorted descending, then
ligand_id ascending as the explicit tie-breaker, and numbered 1 through 17.
No random search, optimization, resampling, or hypothesis testing is performed.
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ANALYSIS_VERSION = "pbpk-weight-sensitivity-1.0"
REFERENCE_ID = "AC5216_ref"
EXPECTED_ANALOGS = 17
BASELINE_TOLERANCE = 1e-8

COMPONENT_COLUMNS = OrderedDict([
    ("BP60", "Brain_Plasma_60min"),
    ("BP30", "Brain_Plasma_30min"),
    ("BP90", "Brain_Plasma_90min"),
    ("brain_AUC", "AUC_brain_tEnd"),
    ("CNS_MPO", "CNS_MPO"),
    ("docking", "dock_score"),
])
BASELINE_WEIGHTS = OrderedDict([
    ("BP60", 0.30),
    ("BP30", 0.15),
    ("BP90", 0.10),
    ("brain_AUC", 0.20),
    ("CNS_MPO", 0.15),
    ("docking", 0.10),
])
SCENARIO_OMISSIONS = OrderedDict([
    ("leave_out_BP60", "BP60"),
    ("leave_out_BP30", "BP30"),
    ("leave_out_BP90", "BP90"),
    ("leave_out_brain_AUC", "brain_AUC"),
    ("leave_out_CNS_MPO", "CNS_MPO"),
    ("leave_out_docking", "docking"),
])
SCENARIO_ORDER = (
    "baseline", "equal_weights", *SCENARIO_OMISSIONS.keys(),
)
REQUIRED_COLUMNS = {
    "ligand_id", "Final_Weighted_Score", *COMPONENT_COLUMNS.values(),
    "Washout_30_to_90", "Washout_Plasma_30_to_90",
}


def build_scenario_weights() -> OrderedDict[str, OrderedDict[str, float]]:
    scenarios: OrderedDict[str, OrderedDict[str, float]] = OrderedDict()
    scenarios["baseline"] = BASELINE_WEIGHTS.copy()
    scenarios["equal_weights"] = OrderedDict(
        (component, 1.0 / 6.0) for component in BASELINE_WEIGHTS
    )
    for scenario, omitted in SCENARIO_OMISSIONS.items():
        denominator = 1.0 - BASELINE_WEIGHTS[omitted]
        scenarios[scenario] = OrderedDict(
            (component, 0.0 if component == omitted else weight / denominator)
            for component, weight in BASELINE_WEIGHTS.items()
        )
    validate_scenario_weights(scenarios)
    return scenarios


def validate_scenario_weights(
    scenarios: OrderedDict[str, OrderedDict[str, float]],
) -> None:
    if tuple(scenarios) != SCENARIO_ORDER or len(scenarios) != 8:
        raise ValueError("The analysis must contain exactly the eight prespecified scenarios")
    expected_components = tuple(BASELINE_WEIGHTS)
    for scenario, weights in scenarios.items():
        if tuple(weights) != expected_components:
            raise ValueError(f"{scenario}: component set or order changed")
        values = np.asarray(list(weights.values()), dtype=float)
        if not np.isfinite(values).all() or (values < 0.0).any():
            raise ValueError(f"{scenario}: weights must be finite and nonnegative")
        if not np.isclose(values.sum(), 1.0, rtol=0.0, atol=1e-12):
            raise ValueError(f"{scenario}: continuous weights do not sum to 1")
    equal = np.asarray(list(scenarios["equal_weights"].values()))
    if not np.allclose(equal, 1.0 / 6.0, rtol=0.0, atol=1e-15):
        raise ValueError("equal_weights must assign exactly 1/6 to each component")
    for scenario, omitted in SCENARIO_OMISSIONS.items():
        if scenarios[scenario][omitted] != 0.0:
            raise ValueError(f"{scenario}: omitted component {omitted} is not zero")


def validate_source(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing = sorted(REQUIRED_COLUMNS - set(data.columns))
    if missing:
        raise ValueError(f"Source table is missing required columns: {missing}")
    if data["ligand_id"].isna().any() or data["ligand_id"].duplicated().any():
        raise ValueError("ligand_id values must be present and unique")
    reference = data.loc[data["ligand_id"] == REFERENCE_ID].copy()
    analogs = data.loc[data["ligand_id"] != REFERENCE_ID].copy()
    if len(reference) != 1:
        raise ValueError(f"Expected exactly one {REFERENCE_ID} row")
    if len(analogs) != EXPECTED_ANALOGS or len(data) != EXPECTED_ANALOGS + 1:
        raise ValueError("Expected exactly 17 analogs plus the separate AC5216 reference")
    numeric_columns = sorted(REQUIRED_COLUMNS - {"ligand_id"})
    numeric = data[numeric_columns].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("All scoring inputs and stored scores must be finite")
    data = data.copy()
    data[numeric_columns] = numeric
    return (
        data.loc[data["ligand_id"] != REFERENCE_ID].reset_index(drop=True),
        data.loc[data["ligand_id"] == REFERENCE_ID].reset_index(drop=True),
    )


def fixed_components(
    analogs: pd.DataFrame, reference: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create desirability z-scores using analog-only means and ddof=1 SDs."""
    analog_components = pd.DataFrame(index=analogs.index)
    reference_components = pd.DataFrame(index=reference.index)
    for component, column in COMPONENT_COLUMNS.items():
        mean = analogs[column].mean()
        standard_deviation = analogs[column].std(ddof=1)
        if not np.isfinite(standard_deviation) or standard_deviation <= 0.0:
            raise ValueError(f"{column}: analog sample standard deviation must be positive")
        direction = -1.0 if component == "docking" else 1.0
        analog_components[component] = direction * (analogs[column] - mean) / standard_deviation
        reference_components[component] = direction * (reference[column] - mean) / standard_deviation
    return analog_components, reference_components


def washout_penalties(data: pd.DataFrame) -> pd.Series:
    brain = np.where(
        (data["Washout_30_to_90"] < 0.15) | (data["Washout_30_to_90"] > 1.5),
        -0.2,
        0.0,
    )
    plasma = np.where(data["Washout_Plasma_30_to_90"] > 0.8, -0.1, 0.0)
    return pd.Series(brain + plasma, index=data.index, dtype=float)


def score_components(
    components: pd.DataFrame,
    penalties: pd.Series,
    weights: OrderedDict[str, float],
) -> pd.Series:
    weight_vector = np.asarray([weights[column] for column in components.columns])
    return pd.Series(
        components.to_numpy(dtype=float) @ weight_vector + penalties.to_numpy(dtype=float),
        index=components.index,
        dtype=float,
    )


def deterministic_ranks(ligand_ids: pd.Series, scores: pd.Series) -> pd.Series:
    """Descending ordinal ranks with ligand_id ascending as the tie-breaker."""
    ranking = pd.DataFrame({"ligand_id": ligand_ids, "score": scores})
    ranking = ranking.sort_values(
        ["score", "ligand_id"], ascending=[False, True], kind="stable"
    )
    ranking["rank"] = np.arange(1, len(ranking) + 1, dtype=int)
    return ranking["rank"].reindex(ligand_ids.index)


def spearman_rank_correlation(baseline_ranks: pd.Series, scenario_ranks: pd.Series) -> float:
    """Calculate rho as Pearson correlation of ranks, without hypothesis testing."""
    baseline = baseline_ranks.to_numpy(dtype=float)
    scenario = scenario_ranks.to_numpy(dtype=float)
    if len(baseline) != len(scenario) or len(baseline) < 2:
        raise ValueError("Rank vectors must have the same length and at least two values")
    return float(np.corrcoef(baseline, scenario)[0, 1])


def run_sensitivity(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analogs, reference = validate_source(data)
    analog_components, reference_components = fixed_components(analogs, reference)
    analog_penalties = washout_penalties(analogs)
    reference_penalties = washout_penalties(reference)
    scenarios = build_scenario_weights()

    baseline_scores = score_components(
        analog_components, analog_penalties, scenarios["baseline"]
    )
    difference = baseline_scores - analogs["Final_Weighted_Score"]
    maximum_error = float(difference.abs().max())
    if maximum_error > BASELINE_TOLERANCE:
        raise ValueError(
            f"Baseline reconstruction failed: maximum absolute error {maximum_error:.12g} "
            f"exceeds {BASELINE_TOLERANCE:.1g}"
        )

    baseline_ranks = deterministic_ranks(analogs["ligand_id"], baseline_scores)
    baseline_top3 = set(analogs.loc[baseline_ranks <= 3, "ligand_id"])
    baseline_top5 = set(analogs.loc[baseline_ranks <= 5, "ligand_id"])
    score_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []
    reference_rows: list[dict[str, object]] = []

    for scenario, weights in scenarios.items():
        scores = score_components(analog_components, analog_penalties, weights)
        ranks = deterministic_ranks(analogs["ligand_id"], scores)
        rho = spearman_rank_correlation(baseline_ranks, ranks)
        scenario_top3 = set(analogs.loc[ranks <= 3, "ligand_id"])
        scenario_top5 = set(analogs.loc[ranks <= 5, "ligand_id"])
        score_rows.append(pd.DataFrame({
            "ligand_id": analogs["ligand_id"],
            "scenario": scenario,
            "score": scores,
            "rank": ranks.astype(int),
        }))
        summary_rows.append({
            "scenario": scenario,
            "spearman_rho_vs_baseline": rho,
            "top3_overlap": len(baseline_top3 & scenario_top3),
            "top5_overlap": len(baseline_top5 & scenario_top5),
        })
        reference_score = score_components(
            reference_components, reference_penalties, weights
        ).iloc[0]
        reference_rows.append({
            "ligand_id": REFERENCE_ID,
            "scenario": scenario,
            "score": reference_score,
        })

    scores_and_ranks = pd.concat(score_rows, ignore_index=True)
    scenario_order = {scenario: index for index, scenario in enumerate(SCENARIO_ORDER)}
    scores_and_ranks = scores_and_ranks.assign(
        _scenario_order=scores_and_ranks["scenario"].map(scenario_order)
    ).sort_values(["_scenario_order", "rank"], kind="stable").drop(columns="_scenario_order")
    summary = pd.DataFrame(summary_rows)
    reference_scores = pd.DataFrame(reference_rows)
    return scores_and_ranks.reset_index(drop=True), summary, reference_scores


def make_rank_heatmap(scores_and_ranks: pd.DataFrame, output: Path) -> None:
    baseline_order = scores_and_ranks.loc[
        scores_and_ranks["scenario"] == "baseline"
    ].sort_values("rank")["ligand_id"]
    matrix = scores_and_ranks.pivot(index="ligand_id", columns="scenario", values="rank")
    matrix = matrix.loc[baseline_order, SCENARIO_ORDER]

    figure, axis = plt.subplots(figsize=(12.0, 8.0))
    image = axis.imshow(matrix.to_numpy(), cmap="viridis_r", vmin=1, vmax=17, aspect="auto")
    axis.set_xticks(np.arange(len(SCENARIO_ORDER)), SCENARIO_ORDER, rotation=35, ha="right")
    axis.set_yticks(np.arange(len(matrix.index)), matrix.index)
    axis.set_xlabel("Prespecified weighting scenario")
    axis.set_ylabel("Analog (ordered by baseline rank)")
    axis.set_title("PBPK analog ranks across prespecified weighting scenarios")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = int(matrix.iat[row, column])
            color = "white" if value <= 5 or value >= 14 else "black"
            axis.text(column, row, str(value), ha="center", va="center", color=color, fontsize=8)
    colorbar = figure.colorbar(image, ax=axis, pad=0.02)
    colorbar.set_label("Rank (1 = highest score)")
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(figure)


def write_outputs(
    scores_and_ranks: pd.DataFrame,
    summary: pd.DataFrame,
    reference_scores: pd.DataFrame,
    outdir: Path,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    scores_and_ranks.to_csv(outdir / "pbpk_sensitivity_scores_and_ranks.csv", index=False)
    summary.to_csv(outdir / "pbpk_sensitivity_scenario_summary.csv", index=False)
    reference_scores.to_csv(outdir / "pbpk_sensitivity_AC5216_reference.csv", index=False)
    make_rank_heatmap(scores_and_ranks, outdir / "pbpk_sensitivity_rank_heatmap.png")


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=repo / "processed_data_supplements" / "Supplementary Table - Pharmacokinetics.csv",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=repo / "PKSim" / "sensitivity_analysis",
    )
    args = parser.parse_args()
    scores, summary, reference = run_sensitivity(pd.read_csv(args.source.resolve()))
    write_outputs(scores, summary, reference, args.outdir.resolve())
    print(f"Completed {len(SCENARIO_ORDER)} prespecified scenarios ({ANALYSIS_VERSION})")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
