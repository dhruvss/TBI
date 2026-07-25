#!/usr/bin/env python3
"""
analyze_openmm_trajectory_v2.py

PBC-safe analysis of an OpenMM protein-ligand membrane trajectory.

Key corrections relative to the original analyzer:
1. Reconstructs protein and ligand as whole fragments.
2. Places the ligand in the nearest periodic image to the original pocket.
3. Aligns the reconstructed complex to frame 0.
4. Computes Euclidean distances after alignment without reusing the unrotated box.
5. Separates fixed-pocket contacts from all-protein contacts.
6. Tracks ligand COM distance to the fixed pocket center.
7. Optionally tracks two user-defined ligand anchor groups.

This script is intended for publication-grade analysis of A3, A7, AC-5216,
and any additional retained candidate trajectories.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import MDAnalysis as mda
from MDAnalysis.analysis.rms import rmsd
from MDAnalysis.lib.distances import distance_array
from MDAnalysis.transformations import unwrap


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def ensure_file(path: Path, label: str) -> None:
    if not path.is_file():
        fail(f"Missing {label}: {path}")


def triclinic_vectors(dimensions: np.ndarray) -> np.ndarray:
    """Return 3x3 box vectors in Angstrom from MDAnalysis dimensions."""
    if dimensions is None or len(dimensions) < 6:
        fail("Trajectory frame has no valid periodic box dimensions")

    lx, ly, lz, alpha, beta, gamma = map(float, dimensions[:6])
    if min(lx, ly, lz) <= 0:
        fail(f"Invalid box lengths: {dimensions[:3]}")

    a = np.array([lx, 0.0, 0.0])
    gamma_r = np.deg2rad(gamma)
    beta_r = np.deg2rad(beta)
    alpha_r = np.deg2rad(alpha)

    b = np.array([ly * np.cos(gamma_r), ly * np.sin(gamma_r), 0.0])
    cx = lz * np.cos(beta_r)
    cy = lz * (np.cos(alpha_r) - np.cos(beta_r) * np.cos(gamma_r)) / np.sin(gamma_r)
    cz_sq = max(lz * lz - cx * cx - cy * cy, 0.0)
    c = np.array([cx, cy, np.sqrt(cz_sq)])

    return np.vstack([a, b, c])


def nearest_image_shift(
    source_center: np.ndarray,
    target_center: np.ndarray,
    dimensions: np.ndarray,
) -> np.ndarray:
    """
    Translation that places source_center in the periodic image nearest target_center.
    Works for orthorhombic and triclinic cells.
    """
    box = triclinic_vectors(dimensions)
    inv_box = np.linalg.inv(box)
    delta = source_center - target_center
    frac = delta @ inv_box
    frac_mic = frac - np.round(frac)
    delta_mic = frac_mic @ box
    return delta_mic - delta


def kabsch_transform(mobile: np.ndarray, reference: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return rotation R and translation t so mobile @ R + t aligns to reference."""
    mob_center = mobile.mean(axis=0)
    ref_center = reference.mean(axis=0)

    mob0 = mobile - mob_center
    ref0 = reference - ref_center

    cov = mob0.T @ ref0
    u, _, vt = np.linalg.svd(cov)
    d = np.sign(np.linalg.det(u @ vt))
    correction = np.diag([1.0, 1.0, d])
    rotation = u @ correction @ vt
    translation = ref_center - mob_center @ rotation
    return rotation, translation


def contact_count(a: np.ndarray, b: np.ndarray, cutoff: float) -> int:
    if len(a) == 0 or len(b) == 0:
        return 0
    return int(np.sum(distance_array(a, b) <= cutoff))


def minimum_distance(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0 or len(b) == 0:
        return np.nan
    return float(np.min(distance_array(a, b)))


def center_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a.mean(axis=0) - b.mean(axis=0)))


def save_plot(df: pd.DataFrame, y: str, out: Path, ylabel: str, title: str) -> None:
    plt.figure(figsize=(7.2, 4.5))
    plt.plot(df["time_ps"], df[y], linewidth=1.4)
    plt.xlabel("Time (ps)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out, dpi=300)
    plt.close()


def main() -> None:
    p = argparse.ArgumentParser(description="PBC-safe OpenMM trajectory analysis")
    p.add_argument("--topology-pdb", required=True)
    p.add_argument("--trajectory-dcd", required=True)
    p.add_argument("--log-csv", required=False, default="")
    p.add_argument("--outdir", required=True)
    p.add_argument("--ligand-resname", default="UNK")
    p.add_argument("--contact-cutoff-a", type=float, default=4.0)
    p.add_argument("--pocket-definition-cutoff-a", type=float, default=6.0)
    p.add_argument("--frame-stride", type=int, default=1)
    p.add_argument(
        "--anchor1-selection",
        default="",
        help='Optional ligand atom selection, e.g. "resname UNK and name C1 C2 C3 C4 C5 C6"',
    )
    p.add_argument(
        "--anchor2-selection",
        default="",
        help='Optional second ligand atom selection',
    )
    p.add_argument(
        "--write-aligned-dcd",
        action="store_true",
        help="Write reconstructed and protein-aligned trajectory",
    )
    args = p.parse_args()

    topology = Path(args.topology_pdb).expanduser().resolve()
    trajectory = Path(args.trajectory_dcd).expanduser().resolve()
    log_csv = Path(args.log_csv).expanduser().resolve() if args.log_csv else None
    outdir = Path(args.outdir).expanduser().resolve()

    ensure_file(topology, "topology PDB")
    ensure_file(trajectory, "trajectory DCD")
    if log_csv:
        ensure_file(log_csv, "OpenMM log CSV")
    outdir.mkdir(parents=True, exist_ok=True)

    u = mda.Universe(str(topology), str(trajectory))
    protein = u.select_atoms("protein")
    backbone = u.select_atoms("protein and backbone")
    protein_heavy = u.select_atoms("protein and not name H*")
    ligand = u.select_atoms(f"resname {args.ligand_resname}")
    ligand_heavy = u.select_atoms(f"resname {args.ligand_resname} and not name H*")

    if len(backbone) == 0:
        fail("No protein backbone atoms selected")
    if len(protein_heavy) == 0:
        fail("No protein heavy atoms selected")
    if len(ligand_heavy) == 0:
        fail(f"No ligand heavy atoms selected for resname {args.ligand_resname}")

    anchor1 = u.select_atoms(args.anchor1_selection) if args.anchor1_selection else None
    anchor2 = u.select_atoms(args.anchor2_selection) if args.anchor2_selection else None

    # Bond-based unwrapping is applied to both fragments before image placement.
    unwrap_protein = unwrap(protein)
    unwrap_ligand = unwrap(ligand)

    # Build the reconstructed frame-0 reference and define the fixed pocket.
    #
    # Important: the ligand may begin in a different periodic image from the
    # protein after bond-based unwrapping. Therefore, define the initial pocket
    # using minimum-image distances first, then translate the ligand into the
    # image nearest that pocket.
    u.trajectory[0]
    unwrap_protein(u.trajectory.ts)
    unwrap_ligand(u.trajectory.ts)

    initial_distances = distance_array(
        ligand_heavy.positions,
        protein_heavy.positions,
        box=u.trajectory.ts.dimensions,
    )
    near_protein_atom_indices = np.unique(
        np.where(initial_distances <= args.pocket_definition_cutoff_a)[1]
    )

    if len(near_protein_atom_indices) == 0:
        min_idx = np.unravel_index(
            np.argmin(initial_distances),
            initial_distances.shape,
        )
        nearest_distance = float(initial_distances[min_idx])
        fail(
            "No protein atoms found within "
            f"{args.pocket_definition_cutoff_a:.2f} A of the ligand in frame 0. "
            f"Minimum periodic ligand-protein distance was {nearest_distance:.3f} A. "
            "Check ligand residue selection and topology."
        )

    initial_near = protein_heavy[near_protein_atom_indices]
    pocket_residues = initial_near.residues
    pocket_heavy = pocket_residues.atoms.select_atoms("not name H*")

    ligand_shift = nearest_image_shift(
        ligand_heavy.center_of_geometry(),
        pocket_heavy.center_of_geometry(),
        u.trajectory.ts.dimensions,
    )
    ligand.translate(ligand_shift)

    ref_backbone = backbone.positions.copy()
    ref_ligand = ligand_heavy.positions.copy()
    ref_pocket_center = pocket_heavy.positions.mean(axis=0)

    pocket_residue_text = ", ".join(
        f"{r.resname}{r.resid}" for r in pocket_residues
    )
    (outdir / "fixed_pocket_residues.txt").write_text(
        f"Pocket definition cutoff: {args.pocket_definition_cutoff_a:.2f} A\n"
        f"Residues: {pocket_residue_text}\n"
    )

    writer = None
    if args.write_aligned_dcd:
        writer = mda.Writer(
            str(outdir / "trajectory_reconstructed_aligned.dcd"),
            n_atoms=u.atoms.n_atoms,
        )

    rows = []

    for ts in u.trajectory[:: args.frame_stride]:
        unwrap_protein(ts)
        unwrap_ligand(ts)

        # Place ligand nearest the fixed pocket in the current reconstructed protein image.
        shift = nearest_image_shift(
            ligand_heavy.center_of_geometry(),
            pocket_heavy.center_of_geometry(),
            ts.dimensions,
        )
        ligand.translate(shift)

        # Align all atoms using the protein backbone.
        rotation, translation = kabsch_transform(backbone.positions, ref_backbone)
        u.atoms.positions = u.atoms.positions @ rotation + translation

        prot_rmsd = rmsd(backbone.positions, ref_backbone, center=False, superposition=False)
        lig_rmsd = rmsd(ligand_heavy.positions, ref_ligand, center=False, superposition=False)

        pocket_contacts = contact_count(
            ligand_heavy.positions,
            pocket_heavy.positions,
            args.contact_cutoff_a,
        )
        all_contacts = contact_count(
            ligand_heavy.positions,
            protein_heavy.positions,
            args.contact_cutoff_a,
        )

        pocket_min = minimum_distance(ligand_heavy.positions, pocket_heavy.positions)
        protein_min = minimum_distance(ligand_heavy.positions, protein_heavy.positions)

        lig_com_to_pocket = float(
            np.linalg.norm(ligand_heavy.positions.mean(axis=0) - ref_pocket_center)
        )

        row = {
            "frame": int(ts.frame),
            "time_ps": float(ts.time),
            "protein_backbone_rmsd_A": prot_rmsd,
            "ligand_heavy_rmsd_A": lig_rmsd,
            "fixed_pocket_contact_count_4A": pocket_contacts,
            "all_protein_contact_count_4A": all_contacts,
            "fixed_pocket_min_distance_A": pocket_min,
            "all_protein_min_distance_A": protein_min,
            "ligand_COM_to_fixed_pocket_center_A": lig_com_to_pocket,
        }

        if anchor1 is not None and len(anchor1):
            row["anchor1_COM_to_fixed_pocket_center_A"] = float(
                np.linalg.norm(anchor1.positions.mean(axis=0) - ref_pocket_center)
            )
            row["anchor1_min_distance_to_fixed_pocket_A"] = minimum_distance(
                anchor1.positions, pocket_heavy.positions
            )

        if anchor2 is not None and len(anchor2):
            row["anchor2_COM_to_fixed_pocket_center_A"] = float(
                np.linalg.norm(anchor2.positions.mean(axis=0) - ref_pocket_center)
            )
            row["anchor2_min_distance_to_fixed_pocket_A"] = minimum_distance(
                anchor2.positions, pocket_heavy.positions
            )

        rows.append(row)

        if writer is not None:
            writer.write(u.atoms)

    if writer is not None:
        writer.close()

    df = pd.DataFrame(rows)
    metrics_path = outdir / "trajectory_metrics_pbc_corrected.csv"
    df.to_csv(metrics_path, index=False)

    summary = [
        "PBC-corrected trajectory analysis",
        "=================================",
        f"Topology: {topology}",
        f"Trajectory: {trajectory}",
        f"Ligand residue: {args.ligand_resname}",
        f"Frames analyzed: {len(df)}",
        f"Fixed pocket residues: {pocket_residue_text}",
        "",
        "Whole trajectory:",
        f"Protein backbone RMSD mean: {df['protein_backbone_rmsd_A'].mean():.3f} A",
        f"Ligand RMSD mean: {df['ligand_heavy_rmsd_A'].mean():.3f} A",
        f"Fixed-pocket contacts mean: {df['fixed_pocket_contact_count_4A'].mean():.2f}",
        f"All-protein contacts mean: {df['all_protein_contact_count_4A'].mean():.2f}",
        f"Fixed-pocket min distance mean: {df['fixed_pocket_min_distance_A'].mean():.3f} A",
        f"All-protein min distance mean: {df['all_protein_min_distance_A'].mean():.3f} A",
        f"Ligand COM-to-pocket mean: {df['ligand_COM_to_fixed_pocket_center_A'].mean():.3f} A",
        "",
        "Occupancy fractions:",
        f"Fixed-pocket contacts >=5: {(df['fixed_pocket_contact_count_4A'] >= 5).mean():.4f}",
        f"Fixed-pocket contacts >=10: {(df['fixed_pocket_contact_count_4A'] >= 10).mean():.4f}",
        f"All-protein contacts >=5: {(df['all_protein_contact_count_4A'] >= 5).mean():.4f}",
        f"All-protein contacts >=10: {(df['all_protein_contact_count_4A'] >= 10).mean():.4f}",
        f"Fixed-pocket min distance <=4 A: {(df['fixed_pocket_min_distance_A'] <= 4).mean():.4f}",
        f"All-protein min distance <=4 A: {(df['all_protein_min_distance_A'] <= 4).mean():.4f}",
        "",
        "Final frame:",
        df.tail(1).to_string(index=False),
    ]

    if log_csv:
        log = pd.read_csv(log_csv)
        log.columns = [c.strip().strip('"') for c in log.columns]
        if "Temperature (K)" in log.columns:
            summary.extend([
                "",
                f"Temperature mean: {log['Temperature (K)'].mean():.3f} K",
                f"Temperature final: {log['Temperature (K)'].iloc[-1]:.3f} K",
            ])

    (outdir / "trajectory_summary_pbc_corrected.txt").write_text("\n".join(summary) + "\n")

    save_plot(
        df, "protein_backbone_rmsd_A",
        outdir / "protein_backbone_rmsd_corrected.png",
        "RMSD (A)", "Protein backbone RMSD",
    )
    save_plot(
        df, "ligand_heavy_rmsd_A",
        outdir / "ligand_rmsd_corrected.png",
        "RMSD (A)", "Ligand RMSD after PBC reconstruction and protein alignment",
    )
    save_plot(
        df, "fixed_pocket_contact_count_4A",
        outdir / "fixed_pocket_contacts.png",
        "Contact count", "Ligand contacts with fixed frame-0 pocket",
    )
    save_plot(
        df, "all_protein_contact_count_4A",
        outdir / "all_protein_contacts.png",
        "Contact count", "Ligand contacts with all protein atoms",
    )
    save_plot(
        df, "ligand_COM_to_fixed_pocket_center_A",
        outdir / "ligand_COM_to_pocket.png",
        "Distance (A)", "Ligand COM distance to fixed pocket center",
    )

    print(f"Wrote: {metrics_path}")
    print(f"Wrote: {outdir / 'trajectory_summary_pbc_corrected.txt'}")
    print("DONE")


if __name__ == "__main__":
    main()
