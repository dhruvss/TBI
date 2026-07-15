#!/usr/bin/env python3
"""
run_openmm_unrestrained_md.py

Run unrestrained OpenMM MD from an equilibrated membrane-protein-ligand system.

This is intended for short pilot production/stability testing after successful
minimization and restrained equilibration.

For AC-5216:
    Input: equilibrated stage 2 or stage 3 PDB
    System: OpenMM System XML from membrane setup
    Output: PDB, DCD, CSV log, checkpoint, summary

This script does not add positional restraints.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from openmm import XmlSerializer, LangevinIntegrator, Platform
from openmm import unit
from openmm.app import PDBFile, Simulation, DCDReporter, StateDataReporter, CheckpointReporter


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def get_energy_kj_per_mol(simulation: Simulation) -> float:
    state = simulation.context.getState(getEnergy=True)
    return state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run unrestrained OpenMM MD.")
    parser.add_argument("--pdb", required=True, help="Input equilibrated PDB")
    parser.add_argument("--system-xml", required=True, help="Input OpenMM System XML")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--prefix", default="AC-5216_unrestrained_1ns")

    parser.add_argument("--steps", type=int, default=1000000, help="Number of MD steps")
    parser.add_argument("--timestep-fs", type=float, default=1.0, help="Timestep in femtoseconds")
    parser.add_argument("--temperature-k", type=float, default=300.0)
    parser.add_argument("--friction", type=float, default=1.0)
    parser.add_argument("--report-interval", type=int, default=5000)
    parser.add_argument("--checkpoint-interval", type=int, default=5000)
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
    out_csv = outdir / f"{args.prefix}.csv"
    out_chk = outdir / f"{args.prefix}.chk"
    out_summary = outdir / f"{args.prefix}_summary.txt"

    print("=== Unrestrained OpenMM MD ===")
    print(f"Input PDB: {pdb_path}")
    print(f"System XML: {xml_path}")
    print(f"Output directory: {outdir}")
    print(f"Steps: {args.steps}")
    print(f"Timestep: {args.timestep_fs} fs")
    print(f"Total simulated time: {args.steps * args.timestep_fs / 1_000_000.0:.3f} ns")
    print(f"Temperature: {args.temperature_k} K")
    print(f"Platform requested: {args.platform}")
    print("")

    pdb = PDBFile(str(pdb_path))

    with xml_path.open() as f:
        system = XmlSerializer.deserialize(f.read())

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
        fail("Initial energy is extremely high. Refusing to run dynamics.")

    simulation.reporters.append(DCDReporter(str(out_dcd), args.report_interval))

    simulation.reporters.append(
        StateDataReporter(
            str(out_csv),
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

    simulation.reporters.append(
        CheckpointReporter(str(out_chk), args.checkpoint_interval)
    )

    print("Running unrestrained MD...")
    simulation.step(args.steps)

    final_energy = get_energy_kj_per_mol(simulation)
    print(f"Final potential energy: {final_energy:.3f} kJ/mol")
    print(f"Energy change: {final_energy - initial_energy:.3f} kJ/mol")

    state = simulation.context.getState(getPositions=True, getEnergy=True)
    positions = state.getPositions()

    with out_pdb.open("w") as f:
        PDBFile.writeFile(simulation.topology, positions, f)

    summary = f"""Unrestrained OpenMM MD summary
==============================

Input PDB: {pdb_path}
System XML: {xml_path}

Output PDB: {out_pdb}
Output DCD: {out_dcd}
Output CSV log: {out_csv}
Output checkpoint: {out_chk}

Platform requested: {args.platform}
Platform used: {actual_platform}

Steps: {args.steps}
Timestep: {args.timestep_fs} fs
Total simulated time: {args.steps * args.timestep_fs / 1_000_000.0:.6f} ns
Temperature: {args.temperature_k} K
Friction: {args.friction} 1/ps

Initial potential energy: {initial_energy:.6f} kJ/mol
Final potential energy: {final_energy:.6f} kJ/mol
Energy change: {final_energy - initial_energy:.6f} kJ/mol

Interpretation:
This is an unrestrained pilot MD run intended to test short-timescale
stability of the membrane-embedded TSPO-ligand system. It is not yet a
long-timescale production replicate.
"""

    out_summary.write_text(summary)

    print(f"Wrote final PDB: {out_pdb}")
    print(f"Wrote DCD: {out_dcd}")
    print(f"Wrote CSV log: {out_csv}")
    print(f"Wrote checkpoint: {out_chk}")
    print(f"Wrote summary: {out_summary}")
    print("DONE.")


if __name__ == "__main__":
    main()
