#!/usr/bin/env python3
"""
orient_tspo_ligand_for_membrane.py

Orient TSPO and ligand coordinates for membrane building.

OpenMM Modeller.addMembrane assumes the membrane is in the XY plane and that
the membrane-spanning axis of the protein is approximately aligned with Z.

This script:
    1. Reads a protein PDB.
    2. Estimates the main protein axis using PCA on C-alpha coordinates.
    3. Rotates the protein so that that axis aligns with the Z-axis.
    4. Applies the same rotation/translation to the ligand SDF conformer.
    5. Centers the protein around the origin.
    6. Writes oriented protein PDB and oriented ligand SDF.

This is a pragmatic first-pass orientation step for an AlphaFold-derived TSPO
model when CHARMM-GUI/OPM orientation is unavailable.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
from rdkit import Chem


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_pdb_atoms(path: Path):
    atoms = []

    with path.open() as f:
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                except ValueError:
                    continue

                atom_name = line[12:16].strip()
                atoms.append(
                    {
                        "line": line.rstrip("\n"),
                        "atom_name": atom_name,
                        "coord": np.array([x, y, z], dtype=float),
                    }
                )

    if not atoms:
        fail(f"No atoms found in PDB: {path}")

    return atoms


def write_pdb_atoms(path: Path, atoms, new_coords):
    lines = []

    for atom, coord in zip(atoms, new_coords):
        line = atom["line"]
        x, y, z = coord

        newline = (
            line[:30]
            + f"{x:8.3f}{y:8.3f}{z:8.3f}"
            + line[54:]
        )

        lines.append(newline + "\n")

    lines.append("END\n")
    path.write_text("".join(lines))


def rotation_matrix_from_vectors(a, b):
    """
    Return rotation matrix that rotates vector a to vector b.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    v = np.cross(a, b)
    c = np.dot(a, b)

    if np.isclose(c, 1.0):
        return np.eye(3)

    if np.isclose(c, -1.0):
        # 180 degree rotation around any vector orthogonal to a.
        orth = np.array([1.0, 0.0, 0.0])

        if abs(np.dot(a, orth)) > 0.9:
            orth = np.array([0.0, 1.0, 0.0])

        v = np.cross(a, orth)
        v = v / np.linalg.norm(v)

        vx = np.array(
            [
                [0, -v[2], v[1]],
                [v[2], 0, -v[0]],
                [-v[1], v[0], 0],
            ]
        )

        return np.eye(3) + 2 * vx @ vx

    s = np.linalg.norm(v)

    vx = np.array(
        [
            [0, -v[2], v[1]],
            [v[2], 0, -v[0]],
            [-v[1], v[0], 0],
        ]
    )

    r = np.eye(3) + vx + vx @ vx * ((1 - c) / (s**2))

    return r


def orient_coords(coords, center, rotation):
    return (coords - center) @ rotation.T


def main():
    parser = argparse.ArgumentParser(
        description="Orient TSPO protein and ligand SDF for membrane building."
    )

    parser.add_argument("--protein-pdb", required=True)
    parser.add_argument("--ligand-sdf", required=True)
    parser.add_argument("--out-protein-pdb", required=True)
    parser.add_argument("--out-ligand-sdf", required=True)
    parser.add_argument(
        "--axis",
        choices=["pc1", "pc2", "pc3"],
        default="pc1",
        help="Principal component to align with Z. Default pc1.",
    )

    args = parser.parse_args()

    protein_pdb = Path(args.protein_pdb).expanduser().resolve()
    ligand_sdf = Path(args.ligand_sdf).expanduser().resolve()
    out_protein = Path(args.out_protein_pdb).expanduser().resolve()
    out_ligand = Path(args.out_ligand_sdf).expanduser().resolve()

    if not protein_pdb.is_file():
        fail(f"Missing protein PDB: {protein_pdb}")

    if not ligand_sdf.is_file():
        fail(f"Missing ligand SDF: {ligand_sdf}")

    atoms = parse_pdb_atoms(protein_pdb)

    all_coords = np.array([a["coord"] for a in atoms])

    ca_coords = np.array(
        [
            a["coord"]
            for a in atoms
            if a["atom_name"] == "CA"
        ]
    )

    if len(ca_coords) < 10:
        fail("Too few C-alpha atoms found for PCA orientation")

    center = ca_coords.mean(axis=0)
    centered_ca = ca_coords - center

    cov = np.cov(centered_ca.T)
    eigvals, eigvecs = np.linalg.eigh(cov)

    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    axis_idx = {"pc1": 0, "pc2": 1, "pc3": 2}[args.axis]
    chosen_axis = eigvecs[:, axis_idx]

    # Choose sign so more positive-Z orientation is deterministic.
    if chosen_axis[2] < 0:
        chosen_axis = -chosen_axis

    rotation = rotation_matrix_from_vectors(chosen_axis, np.array([0.0, 0.0, 1.0]))

    oriented_protein_coords = orient_coords(all_coords, center, rotation)

    out_protein.parent.mkdir(parents=True, exist_ok=True)
    write_pdb_atoms(out_protein, atoms, oriented_protein_coords)

    supplier = Chem.SDMolSupplier(str(ligand_sdf), removeHs=False)
    mols = [m for m in supplier if m is not None]

    if len(mols) != 1:
        fail(f"Expected exactly one molecule in ligand SDF, found {len(mols)}")

    mol = mols[0]
    conf = mol.GetConformer()

    ligand_coords = []

    for i in range(mol.GetNumAtoms()):
        p = conf.GetAtomPosition(i)
        ligand_coords.append([p.x, p.y, p.z])

    ligand_coords = np.array(ligand_coords, dtype=float)
    oriented_ligand_coords = orient_coords(ligand_coords, center, rotation)

    for i, coord in enumerate(oriented_ligand_coords):
        conf.SetAtomPosition(i, tuple(float(x) for x in coord))

    out_ligand.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(out_ligand))
    writer.write(mol)
    writer.close()

    print("Orientation complete.")
    print(f"Protein input: {protein_pdb}")
    print(f"Ligand input: {ligand_sdf}")
    print(f"Protein output: {out_protein}")
    print(f"Ligand output: {out_ligand}")
    print("")
    print("PCA eigenvalues:", eigvals)
    print("Chosen axis:", args.axis)
    print("Chosen axis vector before rotation:", chosen_axis)
    print("")
    print("Next visual check:")
    print(f"    pymol {out_protein} {out_ligand}")


if __name__ == "__main__":
    main()
