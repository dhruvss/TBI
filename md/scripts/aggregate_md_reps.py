#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path("/Users/dhruv/Documents/Research/TBI-tracer/MD_runs_v2")
OUT = Path("/Users/dhruv/Documents/Research/TBI/md/results_summary/replicated_v2")
OUT.mkdir(parents=True, exist_ok=True)

CANDIDATES = ["A3", "A7", "A8", "A15", "AC-5216"]

SETUP_DIR = {
    c: ROOT / c / "openmm_setup_fine14_001"
    for c in CANDIDATES
}

RUN_DIRS = {
    1: "opencl_2fs_10ns",
    2: "opencl_2fs_10ns_rep2",
    3: "opencl_2fs_10ns_rep3",
}

REQUIRED = [
    "frame",
    "time_ps",
    "protein_backbone_rmsd_A",
    "ligand_heavy_rmsd_A",
    "fixed_pocket_contact_count_4A",
    "all_protein_contact_count_4A",
    "fixed_pocket_min_distance_A",
    "all_protein_min_distance_A",
    "ligand_COM_to_fixed_pocket_center_A",
]


def locate_metrics(run_dir: Path):
    matches = sorted(
        run_dir.glob("analysis_pbc_corrected/*trajectory_metrics*pbc*corrected*.csv")
    )

    if not matches:
        matches = sorted(
            run_dir.glob("analysis_pbc_corrected/*.csv")
        )

    good = []
    for f in matches:
        try:
            cols = pd.read_csv(f, nrows=2).columns.tolist()
            if all(x in cols for x in REQUIRED):
                good.append(f)
        except Exception:
            pass

    if len(good) == 0:
        raise FileNotFoundError(
            f"No corrected trajectory metrics CSV found in {run_dir}"
        )

    if len(good) > 1:
        print(f"WARNING: multiple candidates in {run_dir}")
        for g in good:
            print("   ", g)

    return good[0]


rows = []
per_frame_all = []

for candidate in CANDIDATES:
    for rep in [1, 2, 3]:

        run_dir = SETUP_DIR[candidate] / RUN_DIRS[rep]
        f = locate_metrics(run_dir)

        df = pd.read_csv(f)

        missing = [x for x in REQUIRED if x not in df.columns]
        if missing:
            raise ValueError(f"{f}: missing columns {missing}")

        df = df.sort_values("time_ps").reset_index(drop=True)

        if len(df) != 1000:
            print(f"WARNING: {candidate} rep{rep} has {len(df)} frames")

        df["candidate"] = candidate
        df["replicate"] = rep
        df["time_ns"] = df["time_ps"] / 1000.0

        per_frame_all.append(df)

        # Full trajectory
        full = df

        # Final 2 ns = >=8 ns
        final2 = df[df["time_ns"] >= 8.0]

        # Final 5 ns
        final5 = df[df["time_ns"] >= 5.0]

        # First 5 ns
        first5 = df[df["time_ns"] < 5.0]

        row = {
            "candidate": candidate,
            "replicate": rep,
            "source_file": str(f),

            "n_frames": len(df),

            "protein_rmsd_mean_A":
                full["protein_backbone_rmsd_A"].mean(),

            "protein_rmsd_final2ns_mean_A":
                final2["protein_backbone_rmsd_A"].mean(),

            "ligand_rmsd_mean_A":
                full["ligand_heavy_rmsd_A"].mean(),

            "ligand_rmsd_final2ns_mean_A":
                final2["ligand_heavy_rmsd_A"].mean(),

            "fixed_contacts_mean":
                full["fixed_pocket_contact_count_4A"].mean(),

            "fixed_contacts_final2ns_mean":
                final2["fixed_pocket_contact_count_4A"].mean(),

            "all_contacts_mean":
                full["all_protein_contact_count_4A"].mean(),

            "all_contacts_final2ns_mean":
                final2["all_protein_contact_count_4A"].mean(),

            "fixed_min_distance_mean_A":
                full["fixed_pocket_min_distance_A"].mean(),

            "fixed_min_distance_final2ns_mean_A":
                final2["fixed_pocket_min_distance_A"].mean(),

            "all_min_distance_mean_A":
                full["all_protein_min_distance_A"].mean(),

            "all_min_distance_final2ns_mean_A":
                final2["all_protein_min_distance_A"].mean(),

            "com_to_pocket_mean_A":
                full["ligand_COM_to_fixed_pocket_center_A"].mean(),

            "com_to_pocket_final2ns_mean_A":
                final2["ligand_COM_to_fixed_pocket_center_A"].mean(),

            "frames_fixed_contacts_ge5_pct":
                100 * (full["fixed_pocket_contact_count_4A"] >= 5).mean(),

            "frames_fixed_contacts_ge10_pct":
                100 * (full["fixed_pocket_contact_count_4A"] >= 10).mean(),

            "frames_all_contacts_ge5_pct":
                100 * (full["all_protein_contact_count_4A"] >= 5).mean(),

            "frames_all_contacts_ge10_pct":
                100 * (full["all_protein_contact_count_4A"] >= 10).mean(),

            # Temporal drift descriptors
            "fixed_contacts_first5ns_mean":
                first5["fixed_pocket_contact_count_4A"].mean(),

            "fixed_contacts_final5ns_mean":
                final5["fixed_pocket_contact_count_4A"].mean(),

            "fixed_contacts_delta_final_minus_first":
                final5["fixed_pocket_contact_count_4A"].mean()
                - first5["fixed_pocket_contact_count_4A"].mean(),

            "com_first5ns_mean_A":
                first5["ligand_COM_to_fixed_pocket_center_A"].mean(),

            "com_final5ns_mean_A":
                final5["ligand_COM_to_fixed_pocket_center_A"].mean(),

            "com_delta_final_minus_first_A":
                final5["ligand_COM_to_fixed_pocket_center_A"].mean()
                - first5["ligand_COM_to_fixed_pocket_center_A"].mean(),

            "ligand_rmsd_first5ns_mean_A":
                first5["ligand_heavy_rmsd_A"].mean(),

            "ligand_rmsd_final5ns_mean_A":
                final5["ligand_heavy_rmsd_A"].mean(),

            "ligand_rmsd_delta_final_minus_first_A":
                final5["ligand_heavy_rmsd_A"].mean()
                - first5["ligand_heavy_rmsd_A"].mean(),
        }

        rows.append(row)

rep = pd.DataFrame(rows)

candidate_summary = (
    rep.groupby("candidate")
       .agg(
           n_replicates=("replicate", "count"),

           fixed_contacts_mean=("fixed_contacts_mean", "mean"),
           fixed_contacts_sd=("fixed_contacts_mean", "std"),

           fixed_contacts_final2ns_mean=("fixed_contacts_final2ns_mean", "mean"),
           fixed_contacts_final2ns_sd=("fixed_contacts_final2ns_mean", "std"),

           contacts_ge10_pct_mean=("frames_fixed_contacts_ge10_pct", "mean"),
           contacts_ge10_pct_sd=("frames_fixed_contacts_ge10_pct", "std"),

           com_to_pocket_mean_A=("com_to_pocket_mean_A", "mean"),
           com_to_pocket_sd_A=("com_to_pocket_mean_A", "std"),

           com_to_pocket_final2ns_mean_A=("com_to_pocket_final2ns_mean_A", "mean"),
           com_to_pocket_final2ns_sd_A=("com_to_pocket_final2ns_mean_A", "std"),

           ligand_rmsd_mean_A=("ligand_rmsd_mean_A", "mean"),
           ligand_rmsd_sd_A=("ligand_rmsd_mean_A", "std"),

           ligand_rmsd_final2ns_mean_A=("ligand_rmsd_final2ns_mean_A", "mean"),
           ligand_rmsd_final2ns_sd_A=("ligand_rmsd_final2ns_mean_A", "std"),

           all_min_distance_mean_A=("all_min_distance_mean_A", "mean"),
           all_min_distance_sd_A=("all_min_distance_mean_A", "std"),

           protein_rmsd_mean_A=("protein_rmsd_mean_A", "mean"),
           protein_rmsd_sd_A=("protein_rmsd_mean_A", "std"),
       )
       .reset_index()
)

per_frame = pd.concat(per_frame_all, ignore_index=True)

rep.to_csv(
    OUT / "md_replicate_master_summary.csv",
    index=False
)

candidate_summary.to_csv(
    OUT / "md_candidate_replicate_summary.csv",
    index=False
)

per_frame.to_csv(
    OUT / "md_all_15_trajectories_per_frame.csv",
    index=False
)

primary = rep[
    [
        "candidate",
        "replicate",
        "fixed_contacts_mean",
        "com_to_pocket_mean_A",
        "frames_fixed_contacts_ge10_pct",
    ]
].copy()

primary.to_csv(
    OUT / "md_replicate_primary_endpoints.csv",
    index=False
)

print("\nReplicate-level master table:")
print(rep.to_string(index=False))

print("\nCandidate summary:")
print(candidate_summary.to_string(index=False))

print("\nSaved to:")
print(OUT)