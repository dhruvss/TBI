#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created: 2025-11-23
Protons in at 7.4pH when converted to PDBQT file for Autodock Vina docking
"""
import os, re, argparse, subprocess, tempfile
from pathlib import Path
from rdkit import Chem

def safe(name: str) -> str:
    # keep alnum,_,- ; map others to _
    base = re.sub(r'[^A-Za-z0-9_.-]+', '_', name.strip())
    # collapse repeats
    base = re.sub(r'_+', '_', base).strip('_')
    return base or "ligand"

def run_obabel(in_sdf, out_pdbqt):
    cmd = ["obabel", in_sdf, "-O", out_pdbqt, "-p", "7.4"]
    # obabel auto-adds H & gasteiger in pdbqt writer
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Written by AI - ChatGPT 5.2, OpenAI, 2025, manual adjustments for research log
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_sdf", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    suppl = Chem.SDMolSupplier(args.in_sdf, removeHs=False)
    n_ok = 0
    for i, mol in enumerate(suppl):
        if mol is None: continue
        title = mol.GetProp("_Name") if mol.HasProp("_Name") else f"lig_{i+1}"
        fname = safe(title) + ".pdbqt"
        out_path = os.path.join(args.out_dir, fname)
        # write a temp single-mol SDF for obabel
        with tempfile.TemporaryDirectory() as td:
            tmp_sdf = os.path.join(td, "lig.sdf")
            w = Chem.SDWriter(tmp_sdf); w.write(mol); w.close()
            try:
                run_obabel(tmp_sdf, out_path)
                n_ok += 1
            except subprocess.CalledProcessError as e:
                print(f"[WARN] obabel failed for {title}: {e}", flush=True)
                continue
    print(f"[sdf_to_pdbqt_batch] wrote {n_ok} PDBQTs → {args.out_dir}")

if __name__ == "__main__":
    main()
