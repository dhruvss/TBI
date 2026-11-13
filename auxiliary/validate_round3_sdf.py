#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created: 2025-11-28
File: src/enumerate_emapunil_round3_from_files.py

Purpose: Enumerate EXACT AC-5216 template analogs using file-driven R1/R2 lists.
Inputs:
  - templates/R1_round3.tsv  (tab-separated: tag<tab>smiles)
  - templates/R2_round3.tsv  (tab-separated: tag<tab>smiles)
Outputs:
  - docking/emap_enum_round3/round3_max.sdf
  - docking/emap_enum_round3/round3_max.csv
  - docking/emap_enum_round3/round3_manifest.txt

Validation:
  - Ensures all SMILES parse.
  - Ensures total = (#R1 * #R2), default target = 2040 (34 × 60). Use --expect if different.
  - Writes a manifest with SHA256 and unique R1/R2 tags.
Run:
  conda activate tspo-tracer2
  python src/enumerate_emapunil_round3_from_files.py \
    --r1_tsv templates/R1_round3.tsv \
    --r2_tsv templates/R2_round3.tsv \
    --out_sdf docking/emap_enum_round3/round3_max.sdf \
    --out_smiles docking/emap_enum_round3/round3_max.csv \
    --manifest docking/emap_enum_round3/round3_manifest.txt \
    --expect 2040
"""
import os, csv, argparse, hashlib, sys
from rdkit import Chem
from rdkit.Chem import AllChem

TEMPLATE = "CCN({R1})C(=O)Cn2c3c(cnc(n3)c4ccccc4)n(c2=O){R2}"

def load_tsv(path):
    items=[]
    with open(path) as f:
        for ln in f:
            ln=ln.strip()
            if not ln or ln.startswith("#"): continue
            parts=ln.split("\t")
            if len(parts)<2:
                raise ValueError(f"Bad line in {path}: {ln}")
            tag, smi = parts[0].strip(), parts[1].strip()
            items.append((tag,smi))
    if not items:
        raise ValueError(f"No entries in {path}")
    # ensure unique tags
    tags=[t for t,_ in items]
    if len(tags)!=len(set(tags)):
        dup=[t for t in set(tags) if tags.count(t)>1]
        raise ValueError(f"Duplicate tags in {path}: {dup}")
    return items

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--r1_tsv", required=True)
    ap.add_argument("--r2_tsv", required=True)
    ap.add_argument("--out_sdf", required=True)
    ap.add_argument("--out_smiles", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--name_prefix", default="emap3_")
    ap.add_argument("--expect", type=int, default=2040)
    args=ap.parse_args()

    r1_list=load_tsv(args.r1_tsv)     # e.g., 34
    r2_list=load_tsv(args.r2_tsv)     # e.g., 60
    target=len(r1_list)*len(r2_list)

    os.makedirs(os.path.dirname(args.out_sdf), exist_ok=True)

    writer=Chem.SDWriter(args.out_sdf)
    rows=[]; ok=fail=0; bad=[]
    for r1n,r1 in r1_list:
        for r2n,r2 in r2_list:
            name=f"{args.name_prefix}{r1n}_{r2n}"
            smi=TEMPLATE.replace("{R1}",r1).replace("{R2}",r2)
            mol=Chem.MolFromSmiles(smi)
            if mol is None:
                fail+=1; bad.append((name,smi,"MolFromSmiles failed")); continue
            try:
                Chem.SanitizeMol(mol)
            except Exception as e:
                fail+=1; bad.append((name,smi,f"SanitizeMol: {e}")); continue
            try:
                AllChem.EmbedMolecule(mol, randomSeed=17)
                AllChem.UFFOptimizeMolecule(mol, maxIters=200)
            except Exception:
                pass
            mol.SetProp("_Name", name)
            writer.write(mol)
            rows.append((name,smi))
            ok+=1
    writer.close()

    with open(args.out_smiles,"w",newline="") as f:
        cw=csv.writer(f); cw.writerow(["ligand_id","smiles"]); cw.writerows(rows)

    with open(args.manifest,"w") as f:
        f.write("Round-3 enumeration manifest\n")
        f.write("Created: 2025-10-28\n")
        f.write(f"R1_tsv: {args.r1_tsv}\nR2_tsv: {args.r2_tsv}\n")
        f.write(f"SDF: {args.out_sdf}\nCSV: {args.out_smiles}\n")
        f.write(f"Total intended (|R1|*|R2|): {target}\n")
        f.write(f"Wrote: {ok}\nFailed: {fail}\n")
        try: f.write(f"SDF sha256: {sha256(args.out_sdf)}\n")
        except: pass
        try: f.write(f"CSV sha256: {sha256(args.out_smiles)}\n")
        except: pass
        f.write("\nUnique R1 tags:\n")
        f.write(", ".join([t for t,_ in r1_list])+"\n")
        f.write("\nUnique R2 tags:\n")
        f.write(", ".join([t for t,_ in r2_list])+"\n")
        if bad:
            f.write("\nFailures (first 50):\n")
            for b in bad[:50]:
                f.write(f"{b[0]}\t{b[1]}\t{b[2]}\n")

    # hard validation
    if ok != target:
        print(f"[ERROR] Wrote {ok}, expected {target}. See manifest {args.manifest}.", file=sys.stderr)
        sys.exit(1)
    if args.expect and ok != args.expect:
        print(f"[ERROR] Wrote {ok}, expected --expect {args.expect}.", file=sys.stderr)
        sys.exit(1)

    print(f"[enumeration] wrote {ok} / expected {target} → {args.out_sdf}")
    print(f"[enumeration] SMILES → {args.out_smiles}")
    print(f"[enumeration] manifest → {args.manifest}")

if __name__=="__main__":
    main()
