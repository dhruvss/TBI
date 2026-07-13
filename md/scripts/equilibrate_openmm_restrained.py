#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from collections import Counter

from openmm import XmlSerializer, LangevinIntegrator, Platform, CustomExternalForce
from openmm import unit
from openmm.app import PDBFile, Simulation, DCDReporter, StateDataReporter


STANDARD_PROTEIN_RESIDUES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "CYX", "GLN", "GLU", "GLY",
    "HIS", "HID", "HIE", "HIP", "ILE", "LEU", "LYS", "MET", "PHE",
    "PRO", "SER", "THR", "TRP", "TYR", "VAL",
}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def is_hydrogen(atom) -> bool:
    if atom.element is None:
        return atom.name.upper().startswith("H")
    return atom.element.symbol.upper() == "H"


def residue_summary(topology) -> str:
    res_counts = Counter()
    atom_counts = Counter()

    for res in topology.residues():
        atoms = list(res.atoms())
        res_counts[res.name] += 1
        atom_counts[res.name] += len(atoms)

    lines = []
    for name in sorted(res_counts):
        lines.append(f"{name:8s} residues={res_counts[name]:6d} atoms={atom_counts[name]:8d}")
    return "\n".join(lines)


def add_position_restraints(system, topology, positions, ligand_resname, protein_k, ligand_k):
    restraint = CustomExternalForce("0.5*k*((x-x0)^2+(y-y0)^2+(z-z0)^2)")
    restraint.addPerParticleParameter("x0")
    restraint.addPerParticleParameter("y0")
    restraint.addPerParticleParameter("z0")
    restraint.addPerParticleParameter("k")

    n_protein = 0
    n_ligand = 0

    ligand_resname = ligand_resname.strip()

    for atom in topology.atoms():
        if is_hydrogen(atom):
            continue

        resname = atom.residue.name.strip()

        if resname in STANDARD_PROTEIN_RESIDUES:
            k = protein_k
            n_protein += 1
        elif resname == ligand_resname:
            k = ligand_k
            n_ligand += 1
        else:
            continue

        pos = positions[atom.index].value_in_unit(unit.nanometer)
        restraint.addParticle(atom.index, [pos.x, pos.y, pos.z, k])

    if n_protein == 0:
        fail("No protein heavy atoms selected for restraints.")

    if n_ligand == 0:
        fail(f"No ligand heavy atoms selected for ligand residue name '{ligand_resname}'.")

    if n_ligand > 200:
        fail(
            f"Selected {n_ligand} ligand heavy atoms, which is too many. "
            "This probably means the ligand residue name is wrong."
        )

    system.addForce(restraint)
    return n_protein, n_ligand


def get_energy_kj_per_mol(simulation: Simulation) -> float:
    state = simulation.context.getState(getEnergy=True)
    return state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run short restrained NVT equilibration.")
    parser.add_argument("--pdb", required=True)
    parser.add_argument("--system-xml", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--prefix", default="AC-5216_equil_stage1")
    parser.add_argument("--ligand-resname", required=True)

    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument("--timestep-fs", type=float, default=1.0)
    parser.add_argument("--temperature-k", type=float, default=300.0)
    parser.add_argument("--friction", type=float, default=1.0)
    parser.add_argument("--protein-restraint-k", type=float, default=1000.0)
    parser.add_argument("--ligand-restraint-k", type=float, default=500.0)
    parser.add_argument("--report-interval", type=int, default=250)
    parser.add_argument("--platform", default="CPU")

    args = parser.parse_args()

    pdb_path = Path(args.pdb).expanduser().resolve()
    xml_path = Path(args.system_xml).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()

    if not pdb_path.is_file():
        fail(f"Missing PDB: {pdb_path}")
    if not xml_path.is_file():
        fail(f"Missing System XML: {xml_path}")

    outdir.mkdir(parents=True, exist_ok=True)

    out_pdb = outdir / f"{args.prefix}.pdb"
    out_dcd = outdir / f"{args.prefix}.dcd"
    out_log = outdir / f"{args.prefix}.csv"
    out_chk = outdir / f"{args.prefix}.chk"
    out_summary = outdir / f"{args.prefix}_summary.txt"

    print("=== Restrained OpenMM equilibration ===")
    print(f"Input PDB: {pdb_path}")
    print(f"System XML: {xml_path}")
    print(f"Output directory: {outdir}")
    print(f"Ligand residue name: {args.ligand_resname}")
    print(f"Steps: {args.steps}")
    print(f"Timestep: {args.timestep_fs} fs")
    print(f"Temperature: {args.temperature_k} K")
    print(f"Platform requested: {args.platform}")
    print("")
    print("Residue summary:")

    pdb = PDBFile(str(pdb_path))
    print(residue_summary(pdb.topology))
    print("")

    with xml_path.open() as f:
        system = XmlSerializer.deserialize(f.read())

    n_protein, n_ligand = add_position_restraints(
        system=system,
        topology=pdb.topology,
        positions=pdb.positions,
        ligand_resname=args.ligand_resname,
        protein_k=args.protein_restraint_k,
        ligand_k=args.ligand_restraint_k,
    )

    print(f"Restrained protein heavy atoms: {n_protein}")
    print(f"Restrained ligand heavy atoms: {n_ligand}")

    integrator = LangevinIntegrator(
        args.temperature_k * unit.kelvin,
        args.friction / unit.picosecond,
        args.timestep_fs * unit.femtoseconds,
    )

    try:
        platform = Platform.getPlatformByName(args.platform)
        simulation = Simulation(pdb.topology, system, integrator, platform)
        actual_platform = args.platform
    except Exception as exc:
        print(f"WARNING: Could not use platform {args.platform}: {exc}")
        simulation = Simulation(pdb.topology, system, integrator)
        actual_platform = simulation.context.getPlatform().getName()
        print(f"Using default platform: {actual_platform}")

    simulation.context.setPositions(pdb.positions)
    simulation.context.setVelocitiesToTemperature(args.temperature_k * unit.kelvin)

    initial_energy = get_energy_kj_per_mol(simulation)
    print(f"Initial potential energy: {initial_energy:.3f} kJ/mol")

    if initial_energy > 1.0e7:
        fail(
            "Initial potential energy is extremely high. Refusing to run dynamics. "
            "Check restraints, topology, coordinates, and ligand residue selection."
        )

    simulation.reporters.append(DCDReporter(str(out_dcd), args.report_interval))
    simulation.reporters.append(
        StateDataReporter(
            str(out_log),
            args.report_interval,
            step=True,
            time=True,
            potentialEnergy=True,
            kineticEnergy=True,
            totalEnergy=True,
            temperature=True,
            speed=True,
            separator=",",
        )
    )

    print("Running restrained equilibration...")
    simulation.step(args.steps)

    final_energy = get_energy_kj_per_mol(simulation)
    print(f"Final potential energy: {final_energy:.3f} kJ/mol")
    print(f"Energy change: {final_energy - initial_energy:.3f} kJ/mol")

    state = simulation.context.getState(getPositions=True, getEnergy=True)
    positions = state.getPositions()

    with out_pdb.open("w") as f:
        PDBFile.writeFile(simulation.topology, positions, f)

    simulation.saveCheckpoint(str(out_chk))

    summary = f"""Restrained OpenMM equilibration summary
======================================

Input PDB: {pdb_path}
System XML: {xml_path}

Output PDB: {out_pdb}
Output DCD: {out_dcd}
Output CSV log: {out_log}
Output checkpoint: {out_chk}

Platform requested: {args.platform}
Platform used: {actual_platform}

Ligand residue name: {args.ligand_resname}

Steps: {args.steps}
Timestep: {args.timestep_fs} fs
Total simulated time: {args.steps * args.timestep_fs / 1000.0:.3f} ps
Temperature: {args.temperature_k} K
Friction: {args.friction} 1/ps

Protein heavy-atom restraint k: {args.protein_restraint_k} kJ/mol/nm^2
Ligand heavy-atom restraint k: {args.ligand_restraint_k} kJ/mol/nm^2
Restrained protein heavy atoms: {n_protein}
Restrained ligand heavy atoms: {n_ligand}

Initial potential energy: {initial_energy:.6f} kJ/mol
Final potential energy: {final_energy:.6f} kJ/mol
Energy change: {final_energy - initial_energy:.6f} kJ/mol

Interpretation:
This is a short restrained NVT equilibration/stability check, not production MD.
"""

    out_summary.write_text(summary)

    print(f"Wrote PDB: {out_pdb}")
    print(f"Wrote DCD: {out_dcd}")
    print(f"Wrote CSV log: {out_log}")
    print(f"Wrote checkpoint: {out_chk}")
    print(f"Wrote summary: {out_summary}")
    print("DONE.")


if __name__ == "__main__":
    main()
