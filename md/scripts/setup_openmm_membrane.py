#!/usr/bin/env python3
"""
setup_openmm_membrane.py

Local OpenMM fallback for preparing a membrane-embedded TSPO-ligand system.

This script is intended as a CHARMM-GUI fallback when CHARMM-GUI access is not
available through a legitimate academic/government affiliation route.

Current intended first-pass use:
    AC-5216 reference system only.

Inputs:
    - Protein PDB: docking/TSPO/TSPO_prepped.pdb
    - Ligand SDF: md/inputs/AC-5216/ligand_pose.sdf

Outputs:
    - Built membrane/water/ion system PDB
    - Serialized OpenMM System XML
    - Setup metadata text file

Important:
    This workflow is for short-timescale pose-stability screening, not absolute
    binding free energy estimation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import textwrap

import numpy as np

from openmm import Vec3, XmlSerializer
from openmm import unit
from openmm.app import (
    PDBFile,
    Modeller,
    ForceField,
    PME,
    HBonds,
    element,
)

try:
    from openff.toolkit import Molecule
    from openff.units import unit as offunit
except Exception as exc:
    Molecule = None
    offunit = None
    OPENFF_IMPORT_ERROR = exc
else:
    OPENFF_IMPORT_ERROR = None

try:
    from openmmforcefields.generators import SMIRNOFFTemplateGenerator
except Exception as exc:
    SMIRNOFFTemplateGenerator = None
    OPENMMFF_IMPORT_ERROR = exc
else:
    OPENMMFF_IMPORT_ERROR = None


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def repo_root_from_script() -> Path:
    here = Path(__file__).resolve()

    if here.parent.name == "scripts" and here.parent.parent.name == "md":
        return here.parents[2]

    return Path.cwd().resolve()


def load_openff_molecule_from_sdf(path: Path) -> Molecule:
    if Molecule is None:
        fail(f"OpenFF Toolkit is not importable: {OPENFF_IMPORT_ERROR}")

    if not path.is_file():
        fail(f"Ligand SDF not found: {path}")

    try:
        mol = Molecule.from_file(
            str(path),
            file_format="SDF",
            allow_undefined_stereo=True,
        )
    except TypeError:
        mol = Molecule.from_file(str(path), file_format="SDF")

    if isinstance(mol, list):
        if len(mol) != 1:
            fail(f"Expected exactly one molecule in SDF, found {len(mol)}: {path}")
        mol = mol[0]

    if mol.n_conformers < 1:
        fail(f"Ligand SDF has no 3D conformer coordinates: {path}")

    n_h = sum(1 for atom in mol.atoms if atom.atomic_number == 1)
    if n_h == 0:
        fail(
            "Ligand SDF appears to contain no explicit hydrogens. "
            "Regenerate ligand_pose.sdf from the selected PDBQT pose with hydrogens."
        )

    return mol


def openff_conformer_to_openmm_positions(mol: Molecule):
    conf = mol.conformers[0]

    try:
        coords_angstrom = conf.m_as(offunit.angstrom)
    except Exception:
        try:
            coords_angstrom = conf.to(offunit.angstrom).m
        except Exception as exc:
            fail(f"Could not convert OpenFF conformer coordinates to Angstrom: {exc}")

    positions = unit.Quantity(
        [
            Vec3(float(x), float(y), float(z))
            for x, y, z in np.asarray(coords_angstrom)
        ],
        unit.angstrom,
    )

    return positions


def strip_protein_hydrogens(modeller: Modeller) -> int:
    hydrogens = [
        atom
        for atom in modeller.topology.atoms()
        if atom.element == element.hydrogen
    ]

    if hydrogens:
        modeller.delete(hydrogens)

    return len(hydrogens)


def summarize_topology(topology) -> dict[str, int]:
    atoms = list(topology.atoms())
    residues = list(topology.residues())
    chains = list(topology.chains())

    residue_names = {}

    for res in residues:
        residue_names[res.name] = residue_names.get(res.name, 0) + 1

    return {
        "chains": len(chains),
        "residues": len(residues),
        "atoms": len(atoms),
        "residue_names": residue_names,
    }


def main() -> None:
    project_root = repo_root_from_script()

    parser = argparse.ArgumentParser(
        description="Build a local OpenMM POPC membrane system for TSPO-ligand MD."
    )

    parser.add_argument(
        "--candidate",
        default="AC-5216",
        help="Candidate label used for output folder naming.",
    )

    parser.add_argument(
        "--protein-pdb",
        default=str(project_root / "docking" / "TSPO" / "TSPO_prepped.pdb"),
        help="Protein PDB input.",
    )

    parser.add_argument(
        "--ligand-sdf",
        default=str(project_root / "md" / "inputs" / "AC-5216" / "ligand_pose.sdf"),
        help="Single-pose ligand SDF input.",
    )

    parser.add_argument(
        "--outdir",
        default=str(
            Path.home()
            / "Documents"
            / "Research"
            / "TBI-tracer"
            / "MD_runs"
            / "AC-5216"
            / "openmm_setup_001"
        ),
        help="Local output directory for generated system files.",
    )

    parser.add_argument(
        "--lipid",
        default="POPC",
        help="Membrane lipid type for OpenMM Modeller.addMembrane.",
    )

    parser.add_argument(
        "--minimum-padding-nm",
        type=float,
        default=1.0,
        help="Minimum padding for membrane/water box in nm.",
    )

    parser.add_argument(
        "--ionic-strength-molar",
        type=float,
        default=0.15,
        help="Ionic strength in molar.",
    )

    parser.add_argument(
        "--ph",
        type=float,
        default=7.4,
        help="pH used by OpenMM Modeller.addHydrogens.",
    )

    parser.add_argument(
        "--openff-forcefield",
        default="openff-2.1.0",
        help="OpenFF SMIRNOFF force field for ligand parameterization.",
    )

    parser.add_argument(
        "--keep-protein-hydrogens",
        action="store_true",
        help="Do not strip protein hydrogens before addHydrogens.",
    )

    args = parser.parse_args()

    if SMIRNOFFTemplateGenerator is None:
        fail(f"openmmforcefields is not importable: {OPENMMFF_IMPORT_ERROR}")

    protein_pdb = Path(args.protein_pdb).expanduser().resolve()
    ligand_sdf = Path(args.ligand_sdf).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()

    if not protein_pdb.is_file():
        fail(f"Protein PDB not found: {protein_pdb}")

    if not ligand_sdf.is_file():
        fail(f"Ligand SDF not found: {ligand_sdf}")

    outdir.mkdir(parents=True, exist_ok=True)

    print("=== Local OpenMM membrane setup ===")
    print(f"Project root: {project_root}")
    print(f"Candidate: {args.candidate}")
    print(f"Protein PDB: {protein_pdb}")
    print(f"Ligand SDF: {ligand_sdf}")
    print(f"Output directory: {outdir}")
    print("")

    print("[1/8] Loading protein PDB")
    protein = PDBFile(str(protein_pdb))
    modeller = Modeller(protein.topology, protein.positions)

    before_summary = summarize_topology(modeller.topology)
    print(f"Protein atoms before hydrogen handling: {before_summary['atoms']}")

    if not args.keep_protein_hydrogens:
        n_deleted = strip_protein_hydrogens(modeller)
        print(f"Deleted protein hydrogens before re-protonation: {n_deleted}")
    else:
        print("Keeping protein hydrogens as provided.")

    print("[2/8] Loading ligand SDF with OpenFF")
    ligand = load_openff_molecule_from_sdf(ligand_sdf)
    ligand.name = args.candidate.replace("-", "")

    ligand_topology = ligand.to_topology().to_openmm()
    ligand_positions = openff_conformer_to_openmm_positions(ligand)

    print(f"Ligand atoms: {ligand.n_atoms}")
    print(f"Ligand conformers: {ligand.n_conformers}")
    print(f"Ligand formal charge: {ligand.total_charge}")

    print("[3/8] Creating force field and ligand template generator")
    forcefield = ForceField(
        "amber14/protein.ff14SB.xml",
        "amber14/lipid17.xml",
        "amber14/tip3p.xml",
    )

    smirnoff = SMIRNOFFTemplateGenerator(
        molecules=[ligand],
        forcefield=args.openff_forcefield,
    )

    forcefield.registerTemplateGenerator(smirnoff.generator)

    print("[4/8] Adding ligand to protein topology at docked coordinates")
    modeller.add(ligand_topology, ligand_positions)

    combined_pre_h = outdir / f"{args.candidate}_protein_ligand_pre_hydrogen.pdb"
    with combined_pre_h.open("w") as f:
        PDBFile.writeFile(modeller.topology, modeller.positions, f)

    print(f"Wrote: {combined_pre_h}")

    print("[5/8] Adding hydrogens")
    modeller.addHydrogens(forcefield, pH=args.ph)

    combined_h = outdir / f"{args.candidate}_protein_ligand_hydrogenated.pdb"
    with combined_h.open("w") as f:
        PDBFile.writeFile(modeller.topology, modeller.positions, f)

    print(f"Wrote: {combined_h}")

    print("[6/8] Adding POPC membrane, water, and ions")
    print("This may take several minutes.")

    modeller.addMembrane(
        forcefield,
        lipidType=args.lipid,
        minimumPadding=args.minimum_padding_nm * unit.nanometer,
        ionicStrength=args.ionic_strength_molar * unit.molar,
        positiveIon="Na+",
        negativeIon="Cl-",
    )

    built_pdb = outdir / f"{args.candidate}_membrane_solvated_ions.pdb"

    with built_pdb.open("w") as f:
        PDBFile.writeFile(modeller.topology, modeller.positions, f)

    print(f"Wrote: {built_pdb}")

    after_summary = summarize_topology(modeller.topology)

    print("[7/8] Creating OpenMM System")
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=PME,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=HBonds,
        rigidWater=True,
        ewaldErrorTolerance=0.0005,
    )

    system_xml = outdir / f"{args.candidate}_system.xml"

    with system_xml.open("w") as f:
        f.write(XmlSerializer.serialize(system))

    print(f"Wrote: {system_xml}")

    print("[8/8] Writing setup metadata")
    metadata_path = outdir / f"{args.candidate}_setup_metadata.txt"

    residue_counts = after_summary["residue_names"]

    metadata = f"""
Candidate: {args.candidate}
Protein PDB: {protein_pdb}
Ligand SDF: {ligand_sdf}
Output directory: {outdir}

Workflow:
    Local OpenMM fallback
    Protein/lipid/water: Amber14 protein + Lipid17 + TIP3P OpenMM force-field files
    Ligand: OpenFF via openmmforcefields SMIRNOFFTemplateGenerator
    Membrane builder: OpenMM Modeller.addMembrane

Settings:
    Lipid: {args.lipid}
    Water model XML: amber14/tip3p.xml
    Lipid XML: amber14/lipid17.xml
    Protein XML: amber14/protein.ff14SB.xml
    OpenFF ligand force field: {args.openff_forcefield}
    pH for addHydrogens: {args.ph}
    Minimum padding: {args.minimum_padding_nm} nm
    Ionic strength: {args.ionic_strength_molar} M
    Positive ion: Na+
    Negative ion: Cl-

Ligand:
    Name: {ligand.name}
    Atoms: {ligand.n_atoms}
    Formal charge: {ligand.total_charge}

Topology summary after membrane/water/ions:
    Chains: {after_summary["chains"]}
    Residues: {after_summary["residues"]}
    Atoms: {after_summary["atoms"]}

Residue counts:
{textwrap.indent(chr(10).join(f"{k}: {v}" for k, v in sorted(residue_counts.items())), "    ")}

Important limitation:
    This local setup does not automatically validate the biological membrane orientation
    of the AlphaFold-derived TSPO model. The membrane-embedded output PDB should be
    inspected visually before minimization/production MD.
"""

    metadata_path.write_text(metadata.strip() + "\n")

    print(f"Wrote: {metadata_path}")

    print("")
    print("DONE.")
    print("")
    print("Next checks:")
    print(f"    pymol {built_pdb}")
    print("")
    print("Inspect whether TSPO is reasonably embedded in the POPC membrane.")
    print("If the protein appears incorrectly oriented relative to the membrane, stop before minimization.")


if __name__ == "__main__":
    main()
