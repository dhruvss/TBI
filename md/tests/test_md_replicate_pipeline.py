#!/usr/bin/env python3
"""Regression tests for the prespecified replicate-level MD pipeline."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import aggregate_md_reps as aggregation  # noqa: E402
import analyze_md_replicate_statistics as statistics  # noqa: E402


def valid_replicate_table() -> pd.DataFrame:
    rows = []
    for candidate_index, candidate in enumerate(statistics.CANDIDATES):
        for replicate in statistics.EXPECTED_REPLICATES:
            base = candidate_index + replicate / 10.0
            row = {"candidate": candidate, "replicate": replicate}
            for endpoint_index, endpoint in enumerate({**statistics.PRIMARY, **statistics.SECONDARY}):
                row[endpoint] = base + endpoint_index
            rows.append(row)
    return pd.DataFrame(rows)


class EffectSizeTests(unittest.TestCase):
    def test_holm_adjustment(self) -> None:
        observed = statistics.holm_adjust([0.01, 0.04, 0.03, 0.20])
        np.testing.assert_allclose(observed, [0.04, 0.09, 0.09, 0.20])

    def test_cliffs_delta_direction(self) -> None:
        self.assertEqual(statistics.cliffs_delta(np.array([3, 4]), np.array([1, 2])), 1.0)
        self.assertEqual(statistics.cliffs_delta(np.array([1, 2]), np.array([3, 4])), -1.0)

    def test_hedges_g_direction(self) -> None:
        self.assertGreater(statistics.hedges_g(np.array([3, 4, 5]), np.array([0, 1, 2])), 0.0)
        self.assertLess(statistics.hedges_g(np.array([0, 1, 2]), np.array([3, 4, 5])), 0.0)

    def test_mann_whitney_method_records_cross_group_ties(self) -> None:
        _, _, no_tie_method, no_ties = statistics.mann_whitney_prespecified(
            np.array([1, 2, 3]), np.array([4, 5, 6])
        )
        _, _, tie_method, ties = statistics.mann_whitney_prespecified(
            np.array([1, 2, 3]), np.array([3, 4, 5])
        )
        self.assertEqual((no_tie_method, no_ties), ("exact", False))
        self.assertEqual((tie_method, ties), ("asymptotic_tie_corrected", True))


class DesignValidationTests(unittest.TestCase):
    def test_duplicate_trajectory_rejected(self) -> None:
        df = pd.concat([valid_replicate_table(), valid_replicate_table().iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            statistics.validate_replicate_table(df)

    def test_missing_trajectory_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "25 rows"):
            statistics.validate_replicate_table(valid_replicate_table().iloc[:-1])

    def test_candidate_set_rejected(self) -> None:
        df = valid_replicate_table()
        df.loc[df["candidate"] == "A3", "candidate"] = "A99"
        with self.assertRaisesRegex(ValueError, "Candidate set mismatch"):
            statistics.validate_replicate_table(df)

    def test_replicate_ids_rejected(self) -> None:
        df = valid_replicate_table()
        df.loc[(df["candidate"] == "A3") & (df["replicate"] == 5), "replicate"] = 6
        with self.assertRaisesRegex(ValueError, "expected replicate IDs"):
            statistics.validate_replicate_table(df)

    def test_frame_level_inference_rejected(self) -> None:
        df = valid_replicate_table().assign(frame=0)
        with self.assertRaisesRegex(ValueError, "Frame-level input is prohibited"):
            statistics.validate_replicate_table(df)

    def test_rows_are_sorted_by_replicate(self) -> None:
        shuffled = valid_replicate_table().sample(frac=1.0, random_state=7)
        validated = statistics.validate_replicate_table(shuffled)
        for candidate in statistics.CANDIDATES:
            self.assertEqual(
                validated.loc[validated["candidate"] == candidate, "replicate"].tolist(),
                list(statistics.EXPECTED_REPLICATES),
            )

    def test_inference_is_primary_only_and_reference_only(self) -> None:
        df = statistics.validate_replicate_table(valid_replicate_table())
        omnibus = statistics.primary_omnibus_tests(df)
        pairwise = statistics.primary_reference_tests(df)
        self.assertEqual(set(omnibus["endpoint"]), set(statistics.PRIMARY))
        self.assertEqual(set(pairwise["endpoint"]), set(statistics.PRIMARY))
        self.assertEqual(set(pairwise["reference"]), {statistics.REFERENCE})
        self.assertEqual(len(pairwise), len(statistics.PRIMARY) * len(statistics.ANALOGS))
        self.assertTrue((pairwise.groupby("endpoint").size() == 4).all())


class InputValidationTests(unittest.TestCase):
    def test_ambiguous_metrics_csv_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            analysis = Path(tmp) / "analysis_pbc_corrected"
            analysis.mkdir()
            empty = pd.DataFrame(columns=aggregation.REQUIRED_FRAME_COLUMNS)
            empty.to_csv(analysis / "trajectory_metrics_pbc_corrected_a.csv", index=False)
            empty.to_csv(analysis / "trajectory_metrics_pbc_corrected_b.csv", index=False)
            with self.assertRaisesRegex(ValueError, "Ambiguous"):
                aggregation.locate_metrics(Path(tmp))

    def test_incomplete_frame_coverage_rejected(self) -> None:
        frame = pd.DataFrame({
            column: np.arange(aggregation.EXPECTED_FRAMES, dtype=float)
            for column in aggregation.REQUIRED_FRAME_COLUMNS
        })
        frame["time_ps"] = aggregation.EXPECTED_TIME_PS
        frame.loc[999, "time_ps"] = 9990.0
        with self.assertRaisesRegex(ValueError, "expected 10 ps sampling"):
            aggregation.validate_frame_table(frame, "A3", 1, Path("synthetic.csv"))


if __name__ == "__main__":
    unittest.main()
