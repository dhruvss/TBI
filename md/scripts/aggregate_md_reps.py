#!/usr/bin/env python3
"""Aggregate prespecified MD endpoints at the independent-trajectory level."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

ANALYSIS_VERSION = "md-replicate-pipeline-1.0"
CANDIDATES = ("A3", "A7", "A8", "A15", "AC-5216")
EXPECTED_REPLICATES = (1, 2, 3, 4, 5)
EXPECTED_FRAMES = 1000
EXPECTED_TIME_PS = np.arange(1, EXPECTED_FRAMES + 1, dtype=float) * 10.0
REQUIRED_FRAME_COLUMNS = (
    "frame", "time_ps", "protein_backbone_rmsd_A", "ligand_heavy_rmsd_A",
    "fixed_pocket_contact_count_4A", "all_protein_contact_count_4A",
    "fixed_pocket_min_distance_A", "all_protein_min_distance_A",
    "ligand_COM_to_fixed_pocket_center_A",
)
PRIMARY_ENDPOINTS = (
    "fixed_contacts_mean", "com_to_pocket_mean_A",
    "frames_fixed_contacts_ge10_pct",
)


def run_directory_name(replicate: int) -> str:
    return "opencl_2fs_10ns" if replicate == 1 else f"opencl_2fs_10ns_rep{replicate}"


def locate_metrics(run_dir: Path) -> Path:
    """Return the sole valid corrected metrics CSV; ambiguity is fatal."""
    preferred = sorted(run_dir.glob("analysis_pbc_corrected/*trajectory_metrics*pbc*corrected*.csv"))
    matches = preferred or sorted(run_dir.glob("analysis_pbc_corrected/*.csv"))
    valid: list[Path] = []
    failures: list[str] = []
    for path in matches:
        try:
            columns = pd.read_csv(path, nrows=0).columns
        except Exception as exc:
            failures.append(f"{path}: {exc}")
            continue
        if set(REQUIRED_FRAME_COLUMNS).issubset(columns):
            valid.append(path)
    if not valid:
        detail = f" Read failures: {'; '.join(failures)}" if failures else ""
        raise FileNotFoundError(f"No valid corrected trajectory metrics CSV in {run_dir}.{detail}")
    if len(valid) != 1:
        raise ValueError(f"Ambiguous metrics CSVs in {run_dir}: {', '.join(map(str, valid))}")
    return valid[0]


def validate_frame_table(df: pd.DataFrame, candidate: str, replicate: int, source: Path) -> pd.DataFrame:
    missing = sorted(set(REQUIRED_FRAME_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"{source}: missing columns {missing}")
    frame = df.loc[:, REQUIRED_FRAME_COLUMNS].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError(f"{source}: frame metrics contain nonfinite values")
    if len(frame) != EXPECTED_FRAMES:
        raise ValueError(f"{candidate} replicate {replicate}: expected {EXPECTED_FRAMES} frames, found {len(frame)}")
    frame = frame.sort_values("time_ps", kind="stable").reset_index(drop=True)
    if frame["frame"].nunique() != EXPECTED_FRAMES:
        raise ValueError(f"{candidate} replicate {replicate}: frame identifiers are not unique")
    times = frame["time_ps"].to_numpy(dtype=float)
    if not np.allclose(times, EXPECTED_TIME_PS, rtol=0.0, atol=1e-3):
        raise ValueError(
            f"{candidate} replicate {replicate}: expected 10 ps sampling from 10 to 10000 ps; "
            f"observed {times[0]:.6g} to {times[-1]:.6g} ps"
        )
    return frame


def infer_seed(run_dir: Path) -> int | None:
    """Read a recorded seed when present; never infer one from replicate number."""
    patterns = (r"random[_ -]?seed\s*[:=]\s*(\d+)", r"seed\s*[:=]\s*(\d+)")
    for path in sorted(run_dir.glob("*summary*.txt")) + sorted(run_dir.glob("*.txt")):
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))
    return None


def summarize_trajectory(df: pd.DataFrame, candidate: str, replicate: int, source: Path) -> dict[str, object]:
    time_ns = df["time_ps"] / 1000.0
    final2, first5, final5 = df.loc[time_ns >= 8.0], df.loc[time_ns < 5.0], df.loc[time_ns >= 5.0]
    contacts = df["fixed_pocket_contact_count_4A"]
    return {
        "candidate": candidate, "replicate": replicate,
        "source_file": str(source.resolve()), "n_frames": len(df),
        "protein_rmsd_mean_A": df["protein_backbone_rmsd_A"].mean(),
        "protein_rmsd_final2ns_mean_A": final2["protein_backbone_rmsd_A"].mean(),
        "ligand_rmsd_mean_A": df["ligand_heavy_rmsd_A"].mean(),
        "ligand_rmsd_final2ns_mean_A": final2["ligand_heavy_rmsd_A"].mean(),
        "fixed_contacts_mean": contacts.mean(),
        "fixed_contacts_final2ns_mean": final2["fixed_pocket_contact_count_4A"].mean(),
        "all_contacts_mean": df["all_protein_contact_count_4A"].mean(),
        "all_contacts_final2ns_mean": final2["all_protein_contact_count_4A"].mean(),
        "fixed_min_distance_mean_A": df["fixed_pocket_min_distance_A"].mean(),
        "fixed_min_distance_final2ns_mean_A": final2["fixed_pocket_min_distance_A"].mean(),
        "all_min_distance_mean_A": df["all_protein_min_distance_A"].mean(),
        "all_min_distance_final2ns_mean_A": final2["all_protein_min_distance_A"].mean(),
        "com_to_pocket_mean_A": df["ligand_COM_to_fixed_pocket_center_A"].mean(),
        "com_to_pocket_final2ns_mean_A": final2["ligand_COM_to_fixed_pocket_center_A"].mean(),
        "frames_fixed_contacts_ge5_pct": 100.0 * (contacts >= 5).mean(),
        "frames_fixed_contacts_ge10_pct": 100.0 * (contacts >= 10).mean(),
        "frames_all_contacts_ge5_pct": 100.0 * (df["all_protein_contact_count_4A"] >= 5).mean(),
        "frames_all_contacts_ge10_pct": 100.0 * (df["all_protein_contact_count_4A"] >= 10).mean(),
        "fixed_contacts_first5ns_mean": first5["fixed_pocket_contact_count_4A"].mean(),
        "fixed_contacts_final5ns_mean": final5["fixed_pocket_contact_count_4A"].mean(),
        "fixed_contacts_delta_final_minus_first": final5["fixed_pocket_contact_count_4A"].mean() - first5["fixed_pocket_contact_count_4A"].mean(),
        "com_first5ns_mean_A": first5["ligand_COM_to_fixed_pocket_center_A"].mean(),
        "com_final5ns_mean_A": final5["ligand_COM_to_fixed_pocket_center_A"].mean(),
        "com_delta_final_minus_first_A": final5["ligand_COM_to_fixed_pocket_center_A"].mean() - first5["ligand_COM_to_fixed_pocket_center_A"].mean(),
        "ligand_rmsd_first5ns_mean_A": first5["ligand_heavy_rmsd_A"].mean(),
        "ligand_rmsd_final5ns_mean_A": final5["ligand_heavy_rmsd_A"].mean(),
        "ligand_rmsd_delta_final_minus_first_A": final5["ligand_heavy_rmsd_A"].mean() - first5["ligand_heavy_rmsd_A"].mean(),
    }


def validate_design(rep: pd.DataFrame) -> pd.DataFrame:
    required = {"candidate", "replicate", *PRIMARY_ENDPOINTS}
    missing = sorted(required - set(rep.columns))
    if missing:
        raise ValueError(f"Replicate table missing columns: {missing}")
    observed = set(rep["candidate"])
    if observed != set(CANDIDATES):
        raise ValueError(f"Candidate set mismatch: expected {list(CANDIDATES)}, observed {sorted(observed)}")
    if rep.duplicated(["candidate", "replicate"]).any():
        raise ValueError("Duplicate candidate-replicate keys detected")
    for candidate in CANDIDATES:
        ids = set(rep.loc[rep["candidate"] == candidate, "replicate"])
        if ids != set(EXPECTED_REPLICATES):
            raise ValueError(f"{candidate}: expected replicate IDs {list(EXPECTED_REPLICATES)}, observed {sorted(ids)}")
    if not np.isfinite(rep[list(PRIMARY_ENDPOINTS)].to_numpy(dtype=float)).all():
        raise ValueError("Primary endpoint values must all be finite")
    order = {candidate: i for i, candidate in enumerate(CANDIDATES)}
    return rep.assign(_order=rep["candidate"].map(order)).sort_values(
        ["_order", "replicate"], kind="stable"
    ).drop(columns="_order").reset_index(drop=True)


def aggregate(input_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    observed_candidates = {path.name for path in input_root.iterdir() if path.is_dir()}
    if observed_candidates != set(CANDIDATES):
        raise ValueError(
            f"Input candidate set mismatch: expected {list(CANDIDATES)}, "
            f"observed {sorted(observed_candidates)}"
        )
    rows, frames, provenance = [], [], []
    for candidate in CANDIDATES:
        setup = input_root / candidate / "openmm_setup_fine14_001"
        for replicate in EXPECTED_REPLICATES:
            run_dir = setup / run_directory_name(replicate)
            source = locate_metrics(run_dir)
            frame = validate_frame_table(pd.read_csv(source), candidate, replicate, source)
            rows.append(summarize_trajectory(frame, candidate, replicate, source))
            frame = frame.assign(candidate=candidate, replicate=replicate, time_ns=frame["time_ps"] / 1000.0)
            frames.append(frame)
            provenance.append({
                "candidate": candidate, "replicate": replicate, "seed": infer_seed(run_dir),
                "source_file": str(source.resolve()), "frame_count": len(frame),
                "time_min_ps": frame["time_ps"].min(), "time_max_ps": frame["time_ps"].max(),
                "analysis_script": Path(__file__).name, "analysis_version": ANALYSIS_VERSION,
            })
    rep = validate_design(pd.DataFrame(rows))
    return rep, pd.concat(frames, ignore_index=True), pd.DataFrame(provenance)


def write_outputs(rep: pd.DataFrame, per_frame: pd.DataFrame, manifest: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    primary = ["candidate", "replicate", *PRIMARY_ENDPOINTS]
    rep.to_csv(outdir / "md_replicate_master_summary.csv", index=False)
    rep[primary].to_csv(outdir / "md_replicate_primary_endpoints.csv", index=False)
    per_frame.to_csv(outdir / "md_all_trajectories_per_frame.csv", index=False)
    candidate_order = {candidate: index for index, candidate in enumerate(CANDIDATES)}
    manifest.assign(_order=manifest["candidate"].map(candidate_order)).sort_values(
        ["_order", "replicate"], kind="stable"
    ).drop(columns="_order").to_csv(
        outdir / "md_replicate_provenance_manifest.csv", index=False
    )


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=repo.parent / "TBI-tracer" / "MD_runs_v2")
    parser.add_argument("--outdir", type=Path, default=repo / "md" / "results_summary" / "replicated_v2")
    args = parser.parse_args()
    rep, per_frame, manifest = aggregate(args.input_root.expanduser().resolve())
    write_outputs(rep, per_frame, manifest, args.outdir.expanduser().resolve())
    print(f"Validated and aggregated {len(rep)} independent trajectories to {args.outdir}")


if __name__ == "__main__":
    main()
