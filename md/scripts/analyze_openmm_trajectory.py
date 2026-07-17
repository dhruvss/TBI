#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import MDAnalysis as mda
from MDAnalysis.analysis import align
from MDAnalysis.analysis.rms import rmsd
from MDAnalysis.lib.distances import distance_array


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def ensure_file(path: Path, label: str) -> None:
    if not path.is_file():
        fail(f"Missing {label}: {path}")


def pairwise_min_distance(coords_a: np.ndarray, coords_b: np.ndarray, box=None) -> float:
    """
    Return minimum pairwise distance in Angstrom.
    Uses minimum-image periodic distances when box is provided.
    """
    if coords_a.size == 0 or coords_b.size == 0:
        return np.nan

    d = distance_array(coords_a, coords_b, box=box)
    return float(np.min(d))


def contact_count(coords_a: np.ndarray, coords_b: np.ndarray, cutoff_angstrom: float, box=None) -> int:
    """
    Count heavy-atom ligand-protein contacts below cutoff.
    Uses minimum-image periodic distances when box is provided.
    """
    if coords_a.size == 0 or coords_b.size == 0:
        return 0

    d = distance_array(coords_a, coords_b, box=box)
    return int(np.sum(d <= cutoff_angstrom))


def load_openmm_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.is_file():
        return pd.DataFrame()

    df = pd.read_csv(csv_path)

    # OpenMM StateDataReporter sometimes writes quoted headers.
    df.columns = [c.strip().strip('"') for c in df.columns]

    return df


def save_line_plot(df: pd.DataFrame, x: str, y: str, out: Path, title: str, ylabel: str) -> None:
    plt.figure(figsize=(7, 4.5))
    plt.plot(df[x], df[y], linewidth=1.8)
    plt.xlabel("Time (ps)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out, dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze OpenMM MD trajectory.")
    parser.add_argument("--topology-pdb", required=True, help="PDB topology/reference file")
    parser.add_argument("--trajectory-dcd", required=True, help="DCD trajectory")
    parser.add_argument("--log-csv", required=True, help="OpenMM CSV state log")
    parser.add_argument("--outdir", required=True, help="Output analysis directory")
    parser.add_argument("--ligand-resname", default="UNK", help="Ligand residue name")
    parser.add_argument("--contact-cutoff-a", type=float, default=4.0, help="Contact cutoff in Angstrom")
    parser.add_argument("--frame-stride", type=int, default=1, help="Analyze every Nth frame")
    args = parser.parse_args()

    topology_pdb = Path(args.topology_pdb).expanduser().resolve()
    trajectory_dcd = Path(args.trajectory_dcd).expanduser().resolve()
    log_csv = Path(args.log_csv).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()

    ensure_file(topology_pdb, "topology PDB")
    ensure_file(trajectory_dcd, "trajectory DCD")
    ensure_file(log_csv, "log CSV")

    outdir.mkdir(parents=True, exist_ok=True)

    print("=== Trajectory analysis ===")
    print(f"Topology PDB: {topology_pdb}")
    print(f"Trajectory DCD: {trajectory_dcd}")
    print(f"Log CSV: {log_csv}")
    print(f"Output directory: {outdir}")
    print(f"Ligand residue name: {args.ligand_resname}")

    u = mda.Universe(str(topology_pdb), str(trajectory_dcd))
    ref = mda.Universe(str(topology_pdb), str(trajectory_dcd))
    ref.trajectory[0]

    protein_backbone = u.select_atoms("protein and backbone")
    protein_heavy = u.select_atoms("protein and not name H*")
    ligand_heavy = u.select_atoms(f"resname {args.ligand_resname} and not name H*")

    ref_protein_backbone = ref.select_atoms("protein and backbone")
    ref_ligand_heavy = ref.select_atoms(f"resname {args.ligand_resname} and not name H*")

    if len(protein_backbone) == 0:
        fail("No protein backbone atoms selected")

    if len(protein_heavy) == 0:
        fail("No protein heavy atoms selected")

    if len(ligand_heavy) == 0:
        fail(f"No ligand heavy atoms selected for resname {args.ligand_resname}")

    print(f"Protein backbone atoms: {len(protein_backbone)}")
    print(f"Protein heavy atoms: {len(protein_heavy)}")
    print(f"Ligand heavy atoms: {len(ligand_heavy)}")

    # Reference coordinates from first frame.
    ref_backbone_coords = ref_protein_backbone.positions.copy()
    ref_ligand_coords = ref_ligand_heavy.positions.copy()

    metrics = []

    for ts in u.trajectory[::args.frame_stride]:
        # Align current frame to fixed frame-0 reference backbone in place.
        align.alignto(u, ref, select="protein and backbone", match_atoms=True)

        time_ps = float(ts.time)

        protein_rmsd = rmsd(
            protein_backbone.positions,
            ref_backbone_coords,
            center=True,
            superposition=False,
        )

        # Ligand RMSD after protein alignment.
        # Do not center/superpose the ligand itself, because we want pose displacement
        # relative to the protein frame, including translation within/out of the pocket.
        ligand_rmsd = rmsd(
            ligand_heavy.positions,
            ref_ligand_coords,
            center=False,
            superposition=False,
        )

        lig_coords = ligand_heavy.positions.copy()
        prot_coords = protein_heavy.positions.copy()

        box = ts.dimensions
        if box is None or len(box) < 6 or np.any(np.asarray(box[:3]) <= 0):
            box = None

        min_dist = pairwise_min_distance(lig_coords, prot_coords, box=box)
        contacts = contact_count(lig_coords, prot_coords, args.contact_cutoff_a, box=box)

        metrics.append(
            {
                "frame": int(ts.frame),
                "time_ps": time_ps,
                "protein_backbone_rmsd_A": protein_rmsd,
                "ligand_heavy_rmsd_A": ligand_rmsd,
                "ligand_protein_min_distance_A": min_dist,
                "ligand_protein_contact_count_4A": contacts,
            }
        )

        if ts.frame % 25 == 0:
            print(f"Analyzed frame {ts.frame}, time {time_ps:.1f} ps")

    metrics_df = pd.DataFrame(metrics)
    metrics_csv = outdir / "trajectory_metrics.csv"
    metrics_df.to_csv(metrics_csv, index=False)
    print(f"Wrote: {metrics_csv}")

    log_df = load_openmm_csv(log_csv)

    summary_lines = []
    summary_lines.append("Trajectory analysis summary")
    summary_lines.append("===========================")
    summary_lines.append("")
    summary_lines.append(f"Topology PDB: {topology_pdb}")
    summary_lines.append(f"Trajectory DCD: {trajectory_dcd}")
    summary_lines.append(f"Log CSV: {log_csv}")
    summary_lines.append(f"Ligand residue name: {args.ligand_resname}")
    summary_lines.append(f"Contact cutoff: {args.contact_cutoff_a} A")
    summary_lines.append(f"Frame stride: {args.frame_stride}")
    summary_lines.append("")
    summary_lines.append(f"Frames analyzed: {len(metrics_df)}")
    summary_lines.append(f"Final time analyzed: {metrics_df['time_ps'].iloc[-1]:.3f} ps")
    summary_lines.append("")
    summary_lines.append("Trajectory metrics:")
    summary_lines.append(f"Protein backbone RMSD mean: {metrics_df['protein_backbone_rmsd_A'].mean():.3f} A")
    summary_lines.append(f"Protein backbone RMSD final: {metrics_df['protein_backbone_rmsd_A'].iloc[-1]:.3f} A")
    summary_lines.append(f"Ligand heavy-atom RMSD mean: {metrics_df['ligand_heavy_rmsd_A'].mean():.3f} A")
    summary_lines.append(f"Ligand heavy-atom RMSD final: {metrics_df['ligand_heavy_rmsd_A'].iloc[-1]:.3f} A")
    summary_lines.append(f"Ligand-protein min distance mean: {metrics_df['ligand_protein_min_distance_A'].mean():.3f} A")
    summary_lines.append(f"Ligand-protein min distance final: {metrics_df['ligand_protein_min_distance_A'].iloc[-1]:.3f} A")
    summary_lines.append(f"Ligand-protein contacts mean: {metrics_df['ligand_protein_contact_count_4A'].mean():.1f}")
    summary_lines.append(f"Ligand-protein contacts final: {metrics_df['ligand_protein_contact_count_4A'].iloc[-1]:.1f}")

    if not log_df.empty:
        summary_lines.append("")
        summary_lines.append("OpenMM log metrics:")

        if "Temperature (K)" in log_df.columns:
            summary_lines.append(f"Temperature mean: {log_df['Temperature (K)'].mean():.3f} K")
            summary_lines.append(f"Temperature min: {log_df['Temperature (K)'].min():.3f} K")
            summary_lines.append(f"Temperature max: {log_df['Temperature (K)'].max():.3f} K")
            summary_lines.append(f"Temperature final: {log_df['Temperature (K)'].iloc[-1]:.3f} K")

        if "Potential Energy (kJ/mole)" in log_df.columns:
            summary_lines.append(f"Potential energy mean: {log_df['Potential Energy (kJ/mole)'].mean():.3f} kJ/mol")
            summary_lines.append(f"Potential energy final: {log_df['Potential Energy (kJ/mole)'].iloc[-1]:.3f} kJ/mol")

    summary_txt = outdir / "trajectory_summary.txt"
    summary_txt.write_text("\n".join(summary_lines) + "\n")
    print(f"Wrote: {summary_txt}")

    save_line_plot(
        metrics_df,
        "time_ps",
        "protein_backbone_rmsd_A",
        outdir / "protein_backbone_rmsd.png",
        "Protein backbone RMSD",
        "RMSD (A)",
    )

    save_line_plot(
        metrics_df,
        "time_ps",
        "ligand_heavy_rmsd_A",
        outdir / "ligand_heavy_rmsd.png",
        "Ligand heavy-atom RMSD after protein alignment",
        "RMSD (A)",
    )

    save_line_plot(
        metrics_df,
        "time_ps",
        "ligand_protein_min_distance_A",
        outdir / "ligand_protein_min_distance.png",
        "Minimum ligand-protein heavy-atom distance",
        "Distance (A)",
    )

    save_line_plot(
        metrics_df,
        "time_ps",
        "ligand_protein_contact_count_4A",
        outdir / "ligand_protein_contacts.png",
        "Ligand-protein heavy-atom contacts within 4 A",
        "Contact count",
    )

    print("Wrote plots.")
    print("DONE.")


if __name__ == "__main__":
    main()
