#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created: 2025-11-03
File: src/vina_batch_round3.py

Batch dock all PDBQT ligands with AutoDock Vina (parallel, resumable).
Writes a CSV with best affinity per ligand.

Usage example:
  conda activate tspo-tracer
  python src/vina_batch_round3.py \
    --receptor docking/TSPO/TSPO_receptor.pdbqt \
    --ligand_dir docking/emap_enum_round3/pdbqt \
    --out_dir docking/emap_enum_round3/out_coarse \
    --log_dir docking/emap_enum_round3/logs_coarse \
    --results docking/results_round3_coarse.csv \
    --center 10,10,10 --size 22,22,22 \
    --exhaustiveness 8 --num_modes 9 --seed 17 --threads 8
"""
import os, csv, glob, argparse, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

def ensure_dir(p): os.makedirs(p, exist_ok=True)

def parse_best_from_log(log_path):
    # Vina logs contain: "-----+------------+----------+----------" table OR "Affinity: ..."
    best = None
    if not os.path.isfile(log_path): return best
    with open(log_path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith("   1 "):  # table row: rank 1
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        best = (float(parts[1]), float(parts[2]), float(parts[3]))  # affinity, rmsd_lb, rmsd_ub
                        break
                    except: pass
            if line.lower().startswith("affinity:"):
                # fallback
                try:
                    val = float(line.split()[1])
                    best = (val, None, None)
                except: pass
    return best

def run_vina(args, lig_path):
    lig_name = Path(lig_path).stem
    out_lig = os.path.join(args.out_dir, f"{lig_name}_out.pdbqt")
    log_file = os.path.join(args.log_dir, f"{lig_name}.log")

    # Resume if out + log exist and log has result
    if os.path.isfile(out_lig) and os.path.isfile(log_file):
        parsed = parse_best_from_log(log_file)
        if parsed is not None:
            return (lig_name, *parsed, "skipped")

    cmd = [
        "vina",
        "--receptor", args.receptor,
        "--ligand", lig_path,
        "--center_x", str(args.center[0]),
        "--center_y", str(args.center[1]),
        "--center_z", str(args.center[2]),
        "--size_x", str(args.size[0]),
        "--size_y", str(args.size[1]),
        "--size_z", str(args.size[2]),
        "--exhaustiveness", str(args.exhaustiveness),
        "--num_modes", str(args.num_modes),
        "--seed", str(args.seed),
        "--out", out_lig,
        "--log", log_file,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        parsed = parse_best_from_log(log_file)
        if parsed is None:
            return (lig_name, None, None, None, "no_parse")
        return (lig_name, *parsed, "ok")
    except subprocess.CalledProcessError as e:
        return (lig_name, None, None, None, f"err:{e.returncode}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receptor", required=True)
    ap.add_argument("--ligand_dir", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--log_dir", required=True)
    ap.add_argument("--ligand_glob", default="*.pdbqt")
    ap.add_argument("--center", required=True, help="cx,cy,cz")
    ap.add_argument("--size", required=True, help="sx,sy,sz")
    ap.add_argument("--exhaustiveness", type=int, default=8)
    ap.add_argument("--num_modes", type=int, default=9)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--threads", type=int, default=4)
    args = ap.parse_args()

    args.center = tuple(map(float, args.center.split(",")))
    args.size   = tuple(map(float, args.size.split(",")))

    ensure_dir(args.out_dir); ensure_dir(args.log_dir)
    ligs = sorted(glob.glob(os.path.join(args.ligand_dir, args.ligand_glob)))
    if not ligs:
        raise SystemExit(f"No ligands matched {args.ligand_dir}/{args.ligand_glob}")

    out_tmp = args.results + ".tmp"
    with open(out_tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ligand_id","affinity_kcal_per_mol","rmsd_lb","rmsd_ub","status"])
        with ThreadPoolExecutor(max_workers=args.threads) as ex:
            futs = [ex.submit(run_vina, args, lp) for lp in ligs]
            for i, fut in enumerate(as_completed(futs), 1):
                lig_name, aff, lb, ub, status = fut.result()
                w.writerow([lig_name, aff, lb, ub, status])
                if i % 50 == 0:
                    f.flush()
                    os.fsync(f.fileno())

    Path(out_tmp).replace(args.results)
    print(f"Wrote results → {args.results}  (ligands: {len(ligs)})")

if __name__ == "__main__":
    main()
