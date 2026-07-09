#!/usr/bin/env python3
"""
make_openff_sdf_from_template_and_pdbqt.py

Create an OpenFF-ready SDF by taking correct ligand chemistry from a template
SDF and replacing heavy-atom coordinates with the selected Vina PDBQT pose.

This is needed because PDBQT/PDB conversions often lose aromaticity and bond
orders, causing OpenFF/RDKit to detect invalid radicals.

For AC-5216:
    Template chemistry: PubChem SDF
    Pose coordinates: docking/fine_all_rounds/out_pdbqt/AC5216_out.pdbqt, MODEL 1

Assumption:
    Heavy atom order in the template SDF matches heavy atom order in the PDBQT.
    This is plausible for AC-5216 because the PDBQT REMARK name is PubChem CID
    6433109 and the ligand appears to have been prepared from the same source.
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


def parse_pdbqt_model_coords(pdbqt_path: Path, model_number: int = 1):
    """
    Extract ATOM/HETATM coordinates from the selected MODEL in a Vina PDBQT.

    Returns:
        coords: list[(x, y, z)]
        atom_names: list[str]
        atom_types: list[str]
    """
    coords = []
    atom_names = []
    atom_types = []

    in_model = False
    saw_model_records = False

    with pdbqt_path.open() as f:
        for line in f:
            if line.startswith("MODEL"):
                saw_model_records = True
                parts = line.split()
                current_model = int(parts[1]) if len(parts) > 1 else None
                in_model = current_model == model_number
                continue

            if line.startswith("ENDMDL"):
                if in_model:
                    break
                in_model = False
                continue

            if saw_model_records and not in_model:
                continue

            if line.startswith(("ATOM", "HETATM")):
                atom_name = line[12:16].strip()
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                except ValueError:
                    parts = line.split()
                    x, y, z = map(float, parts[5:8])

                # PDBQT atom type is usually the last whitespace token.
                parts = line.split()
                atom_type = parts[-1] if parts else ""

                coords.append((x, y, z))
                atom_names.append(atom_name)
                atom_types.append(atom_type)

    if not coords:
        fail(f"No coordinates found in {pdbqt_path} for model {model_number}")

    return coords, atom_names, atom_types


def read_single_template_sdf(template_sdf: Path) -> Chem.Mol:
    supplier = Chem.SDMolSupplier(str(template_sdf), removeHs=False)

    mols = [m for m in supplier if m is not None]

    if len(mols) != 1:
        fail(f"Expected exactly one molecule in template SDF, found {len(mols)}")

    mol = mols[0]

    try:
        Chem.SanitizeMol(mol)
    except Exception as exc:
        fail(f"Template SDF failed RDKit sanitization: {exc}")

    return mol


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Use template SDF chemistry and PDBQT pose coordinates to create OpenFF-ready SDF."
    )

    parser.add_argument(
        "--template-sdf",
        required=True,
        help="Correct-chemistry template SDF, e.g. PubChem AC-5216 SDF.",
    )

    parser.add_argument(
        "--pose-pdbqt",
        required=True,
        help="Vina output PDBQT containing selected docked pose.",
    )

    parser.add_argument(
        "--model",
        type=int,
        default=1,
        help="Vina MODEL number to extract. Default: 1.",
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Output OpenFF-ready docked-pose SDF.",
    )

    args = parser.parse_args()

    template_sdf = Path(args.template_sdf).expanduser().resolve()
    pose_pdbqt = Path(args.pose_pdbqt).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()

    if not template_sdf.is_file():
        fail(f"Missing template SDF: {template_sdf}")

    if not pose_pdbqt.is_file():
        fail(f"Missing pose PDBQT: {pose_pdbqt}")

    print(f"Template SDF: {template_sdf}")
    print(f"Pose PDBQT: {pose_pdbqt}")
    print(f"Selected MODEL: {args.model}")

    mol = read_single_template_sdf(template_sdf)

    # Remove hydrogens first so heavy-atom coordinate replacement is simple.
    mol_no_h = Chem.RemoveHs(mol, sanitize=True)

    heavy_atoms = [a for a in mol_no_h.GetAtoms() if a.GetAtomicNum() > 1]
    pdbqt_coords, pdbqt_atom_names, pdbqt_atom_types = parse_pdbqt_model_coords(
        pose_pdbqt,
        args.model,
    )

    print(f"Template heavy atoms: {len(heavy_atoms)}")
    print(f"PDBQT pose atoms: {len(pdbqt_coords)}")

    if len(heavy_atoms) != len(pdbqt_coords):
        fail(
            "Heavy atom count mismatch. Cannot safely assign PDBQT coordinates "
            "to template SDF by atom order.\n"
            f"Template heavy atoms: {len(heavy_atoms)}\n"
            f"PDBQT atoms: {len(pdbqt_coords)}"
        )

    conf = Chem.Conformer(mol_no_h.GetNumAtoms())

    for idx, (x, y, z) in enumerate(pdbqt_coords):
        conf.SetAtomPosition(idx, (float(x), float(y), float(z)))

    mol_no_h.RemoveAllConformers()
    mol_no_h.AddConformer(conf, assignId=True)

    # Add hydrogens with coordinates inferred from heavy atoms.
    mol_h = Chem.AddHs(mol_no_h, addCoords=True)

    try:
        Chem.SanitizeMol(mol_h)
    except Exception as exc:
        fail(f"Sanitization failed after coordinate replacement and hydrogen addition: {exc}")

    radical_atoms = [
        atom.GetIdx()
        for atom in mol_h.GetAtoms()
        if atom.GetNumRadicalElectrons() != 0
    ]

    if radical_atoms:
        fail(f"Radical atoms remain after repair: {radical_atoms}")

    out.parent.mkdir(parents=True, exist_ok=True)

    writer = Chem.SDWriter(str(out))
    writer.write(mol_h)
    writer.close()

    n_h = sum(1 for atom in mol_h.GetAtoms() if atom.GetAtomicNum() == 1)

    print(f"Wrote: {out}")
    print(f"Final atoms: {mol_h.GetNumAtoms()}")
    print(f"Explicit hydrogens: {n_h}")
    print("Done.")


if __name__ == "__main__":
    main()
