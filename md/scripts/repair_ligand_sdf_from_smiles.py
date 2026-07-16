#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def repo_root_from_script() -> Path:
    here = Path(__file__).resolve()

    if here.parent.name == "scripts" and here.parent.parent.name == "md":
        return here.parents[2]

    return Path.cwd().resolve()


def swiss_molecule_to_compound(label: str) -> str:
    m = re.search(r"(\d+)", str(label))

    if not m:
        fail(f"Could not parse SwissADME molecule label: {label}")

    n = int(m.group(1))

    if 1 <= n <= 17:
        return f"A{n}"

    if n == 18:
        return "AC-5216"

    fail(f"Unexpected SwissADME molecule number: {n}")


def get_smiles_from_swissadme(csv_path: Path, candidate: str) -> str:
    if not csv_path.is_file():
        fail(f"Missing SwissADME CSV: {csv_path}")

    df = pd.read_csv(csv_path)

    if "Molecule" not in df.columns or "Canonical SMILES" not in df.columns:
        fail("SwissADME CSV must contain 'Molecule' and 'Canonical SMILES' columns")

    df = df.copy()
    df["Compound"] = df["Molecule"].apply(swiss_molecule_to_compound)

    hit = df[df["Compound"] == candidate]

    if len(hit) != 1:
        fail(f"Expected exactly one SwissADME row for {candidate}, found {len(hit)}")

    smiles = str(hit.iloc[0]["Canonical SMILES"]).strip()

    if not smiles:
        fail(f"Empty Canonical SMILES for {candidate}")

    return smiles


def clear_radicals(mol: Chem.Mol) -> Chem.Mol:
    rw = Chem.RWMol(mol)

    for atom in rw.GetAtoms():
        atom.SetNumRadicalElectrons(0)

    return rw.GetMol()


def main() -> None:
    project_root = repo_root_from_script()

    parser = argparse.ArgumentParser(
        description="Repair docked ligand SDF using canonical SMILES bond orders."
    )

    parser.add_argument(
        "--candidate",
        required=True,
        help="Candidate ID, e.g. AC-5216, A15, A3, A7, A17.",
    )

    parser.add_argument(
        "--pose-pdb",
        required=True,
        help="Docked ligand pose PDB file generated from selected Vina mode.",
    )

    parser.add_argument(
        "--swissadme",
        default=str(project_root / "ADMET" / "swissadme.csv"),
        help="SwissADME CSV containing Canonical SMILES.",
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Output repaired SDF.",
    )

    args = parser.parse_args()

    pose_pdb = Path(args.pose_pdb).expanduser().resolve()
    swissadme = Path(args.swissadme).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()

    if not pose_pdb.is_file():
        fail(f"Missing pose PDB: {pose_pdb}")

    smiles = get_smiles_from_swissadme(swissadme, args.candidate)

    print(f"Candidate: {args.candidate}")
    print(f"Pose PDB: {pose_pdb}")
    print(f"SwissADME CSV: {swissadme}")
    print(f"SMILES: {smiles}")

    template = Chem.MolFromSmiles(smiles)

    if template is None:
        fail(f"RDKit could not parse SMILES for {args.candidate}: {smiles}")

    template = Chem.AddHs(template)

    pose = Chem.MolFromPDBFile(
        str(pose_pdb),
        removeHs=False,
        sanitize=False,
    )

    if pose is None:
        fail(f"RDKit could not read pose PDB: {pose_pdb}")

    pose = clear_radicals(pose)

    try:
        repaired = AllChem.AssignBondOrdersFromTemplate(template, pose)
    except Exception as exc:
        fail(
            "Could not assign bond orders from SMILES template to pose PDB. "
            "This usually means atom connectivity/order from the PDB conversion is incompatible. "
            f"RDKit error: {exc}"
        )

    repaired = clear_radicals(repaired)

    try:
        Chem.SanitizeMol(repaired)
    except Exception as exc:
        fail(f"RDKit sanitization failed after bond-order repair: {exc}")

    repaired = Chem.AddHs(repaired, addCoords=True)

    # Final sanity checks.
    radical_atoms = [
        atom.GetIdx()
        for atom in repaired.GetAtoms()
        if atom.GetNumRadicalElectrons() != 0
    ]

    if radical_atoms:
        fail(f"Radicals remain after repair at atom indices: {radical_atoms}")

    n_h = sum(1 for atom in repaired.GetAtoms() if atom.GetAtomicNum() == 1)

    if n_h == 0:
        fail("No explicit hydrogens found after repair")

    out.parent.mkdir(parents=True, exist_ok=True)

    writer = Chem.SDWriter(str(out))
    writer.write(repaired)
    writer.close()

    print(f"Wrote repaired OpenFF-ready SDF: {out}")
    print(f"Atoms: {repaired.GetNumAtoms()}")
    print(f"Explicit hydrogens: {n_h}")
    print("Repair complete.")


if __name__ == "__main__":
    main()
