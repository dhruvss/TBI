#!/usr/bin/env python3
"""Regression tests for the prespecified PBPK weight sensitivity analysis."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import analyze_pbpk_weight_sensitivity as analysis  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "processed_data_supplements" / "Supplementary Table - Pharmacokinetics.csv"


class WeightTests(unittest.TestCase):
    def test_exact_scenario_set_and_weight_constraints(self) -> None:
        scenarios = analysis.build_scenario_weights()
        self.assertEqual(tuple(scenarios), analysis.SCENARIO_ORDER)
        self.assertEqual(len(scenarios), 8)
        for weights in scenarios.values():
            self.assertAlmostEqual(sum(weights.values()), 1.0, places=14)
        for scenario, omitted in analysis.SCENARIO_OMISSIONS.items():
            self.assertEqual(scenarios[scenario][omitted], 0.0)
        for weight in scenarios["equal_weights"].values():
            self.assertEqual(weight, 1.0 / 6.0)

    def test_docking_is_reversed_desirability(self) -> None:
        data = pd.read_csv(SOURCE)
        analogs, reference = analysis.validate_source(data)
        components, _ = analysis.fixed_components(analogs, reference)
        expected = -(analogs["dock_score"] - analogs["dock_score"].mean()) / analogs["dock_score"].std(ddof=1)
        np.testing.assert_allclose(components["docking"], expected, rtol=0.0, atol=1e-14)


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = pd.read_csv(SOURCE)
        cls.scores, cls.summary, cls.reference = analysis.run_sensitivity(cls.data)

    def test_baseline_reconstruction(self) -> None:
        stored = self.data.loc[self.data["ligand_id"] != analysis.REFERENCE_ID].set_index("ligand_id")["Final_Weighted_Score"]
        baseline = self.scores.loc[self.scores["scenario"] == "baseline"].set_index("ligand_id")["score"]
        self.assertLessEqual(float((baseline - stored).abs().max()), analysis.BASELINE_TOLERANCE)

    def test_primary_population_and_reference_exclusion(self) -> None:
        self.assertEqual(self.scores["ligand_id"].nunique(), 17)
        self.assertEqual(len(self.scores), 17 * 8)
        self.assertNotIn(analysis.REFERENCE_ID, set(self.scores["ligand_id"]))
        self.assertEqual(set(self.reference["ligand_id"]), {analysis.REFERENCE_ID})
        self.assertEqual(len(self.reference), 8)

    def test_summary_and_ranks_are_complete(self) -> None:
        self.assertEqual(tuple(self.summary["scenario"]), analysis.SCENARIO_ORDER)
        self.assertEqual(list(self.summary.columns), [
            "scenario", "spearman_rho_vs_baseline", "top3_overlap", "top5_overlap"
        ])
        for _, group in self.scores.groupby("scenario"):
            self.assertEqual(sorted(group["rank"]), list(range(1, 18)))

    def test_tie_breaking_is_deterministic(self) -> None:
        ids = pd.Series(["ligand_b", "ligand_a", "ligand_c"])
        scores = pd.Series([1.0, 1.0, 0.0])
        ranks = analysis.deterministic_ranks(ids, scores)
        self.assertEqual(ranks.tolist(), [2, 1, 3])

    def test_spearman_is_rank_correlation_only(self) -> None:
        baseline = pd.Series([1, 2, 3, 4])
        self.assertAlmostEqual(
            analysis.spearman_rank_correlation(baseline, baseline), 1.0
        )
        self.assertAlmostEqual(
            analysis.spearman_rank_correlation(baseline, pd.Series([4, 3, 2, 1])),
            -1.0,
        )


if __name__ == "__main__":
    unittest.main()
