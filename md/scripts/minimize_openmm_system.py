#!/usr/bin/env python3
"""
minimize_openmm_system.py

Energy-minimize a prepared OpenMM membrane-protein-ligand system.

Inputs:
    - OpenMM System XML
    - Solvated/membrane PDB with coordinates/topology

Outputs:
    - minimized PDB
    - minimization energy log

This is the first validation step after local OpenMM system construction.
It does not run equilibration or production MD.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from openmm import XmlSerializer, LangevinIntegrator, Platform
from openmm import unit
from openmm.app import PDBFile, Simulation


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def get_energy_kj_per_mol(simulation: Simulation) -> float:
    state = simulation.context.getState(getEnergy=True)
    energy = state.getPotentialEnergy()
    return energy.value_in_unit(unit.kilojoule_per_mole)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimize an OpenMM membrane-protein-ligand system."
    )

    parser.add_argument(
        "--pdb",
        required=True,
        help="Input membrane/solvated PDB.",
    )

    parser.add_argument(
        "--system-xml",
        required=True,
        help="Serialized OpenMM System XML.",
    )

    parser.add_argument(
        "--out-pdb",
        required=True,
        help="Output minimized PDB.",
    )

    parser.add_argument(
        "--log",
        required=True,
        help="Output minimization log.",
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=10.0,
        help="Minimization tolerance in kJ/mol/nm. Default: 10.0",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=2000,
        help="Maximum minimization iterations. Default: 2000",
    )

    parser.add_argument(
        "--platform",
        default="CPU",
        help="OpenMM platform to use. Default: CPU. Options may include CPU, OpenCL, CUDA, Metal.",
    )

    args = parser.parse_args()

    pdb_path = Path(args.pdb).expanduser().resolve()
    xml_path = Path(args.system_xml).expanduser().resolve()
    out_pdb = Path(args.out_pdb).expanduser().resolve()
    log_path = Path(args.log).expanduser().resolve()

    if not pdb_path.is_file():
        fail(f"Missing input PDB: {pdb_path}")

    if not xml_path.is_file():
        fail(f"Missing System XML: {xml_path}")

    out_pdb.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    print("=== OpenMM minimization ===")
    print(f"Input PDB: {pdb_path}")
    print(f"System XML: {xml_path}")
    print(f"Output PDB: {out_pdb}")
    print(f"Log: {log_path}")
    print(f"Platform requested: {args.platform}")

    pdb = PDBFile(str(pdb_path))

    with xml_path.open() as f:
        system = XmlSerializer.deserialize(f.read())

    integrator = LangevinIntegrator(
        300.0 * unit.kelvin,
        1.0 / unit.picosecond,
        0.002 * unit.picoseconds,
    )

    try:
        platform = Platform.getPlatformByName(args.platform)
        simulation = Simulation(pdb.topology, system, integrator, platform)
    except Exception as exc:
        print(f"WARNING: Could not use requested platform {args.platform}: {exc}")
        print("Falling back to default OpenMM platform.")
        simulation = Simulation(pdb.topology, system, integrator)

    simulation.context.setPositions(pdb.positions)

    initial_energy = get_energy_kj_per_mol(simulation)
    print(f"Initial potential energy: {initial_energy:.3f} kJ/mol")

    print("Running energy minimization...")
    simulation.minimizeEnergy(
        tolerance=args.tolerance * unit.kilojoule_per_mole / unit.nanometer,
        maxIterations=args.max_iterations,
    )

    final_energy = get_energy_kj_per_mol(simulation)
    print(f"Final potential energy: {final_energy:.3f} kJ/mol")
    print(f"Energy change: {final_energy - initial_energy:.3f} kJ/mol")

    state = simulation.context.getState(getPositions=True, getEnergy=True)
    positions = state.getPositions()

    with out_pdb.open("w") as f:
        PDBFile.writeFile(simulation.topology, positions, f)

    with log_path.open("w") as f:
        f.write("OpenMM minimization log\n")
        f.write("=======================\n\n")
        f.write(f"Input PDB: {pdb_path}\n")
        f.write(f"System XML: {xml_path}\n")
        f.write(f"Output PDB: {out_pdb}\n")
        f.write(f"Platform requested: {args.platform}\n")
        f.write(f"Tolerance: {args.tolerance} kJ/mol/nm\n")
        f.write(f"Max iterations: {args.max_iterations}\n\n")
        f.write(f"Initial potential energy: {initial_energy:.6f} kJ/mol\n")
        f.write(f"Final potential energy: {final_energy:.6f} kJ/mol\n")
        f.write(f"Energy change: {final_energy - initial_energy:.6f} kJ/mol\n")

    print(f"Wrote minimized PDB: {out_pdb}")
    print(f"Wrote log: {log_path}")
    print("DONE.")


if __name__ == "__main__":
    main()
