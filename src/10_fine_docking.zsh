cd ~/Documents/Research/TBI-tracer
eval "$(/Users/dhruv/miniconda3/bin/conda shell.zsh hook)"
conda activate tspo-tracer

BASE=~/Documents/Research/TBI-tracer
RECDIR="$BASE/docking/TSPO"
PASSCSV="$BASE/docking/passed_log.csv"

R1ROOT="$BASE/docking/emap_enum_round1"
R2ROOT="$BASE/docking/emap_enum_round2"
R3ROOT="$BASE/docking/emap_enum_round3"

OUTROOT="$BASE/docking/fine_all_rounds"
OUTDIR="$OUTROOT/out_pdbqt"
LOGDIR="$OUTROOT/logs"
OUTCSV="$OUTROOT/results_fine_all_rounds.csv"
FAILCSV="$OUTROOT/results_fine_all_rounds_failures.csv"
IDLIST="$OUTROOT/fine_ids.tmp"

VINA_BIN=$(command -v vina)
[[ -x "$VINA_BIN" ]] || { echo "vina not found in env tspo-tracer"; exit 1; }
[[ -f "$PASSCSV" ]] || { echo "missing pass csv: $PASSCSV"; exit 1; }

mkdir -p "$OUTDIR" "$LOGDIR"

grep -vE '^(ROOT|BRANCH|ENDBRANCH|ENDROOT|TORSDOF)' "$RECDIR/TSPO_prepped.pdbqt" > "$RECDIR/TSPO_receptor.pdbqt"

CORES=$(sysctl -n hw.ncpu)
EXH=32
NMODES=3

echo "ligand_id,round,affinity_kcal_per_mol,ligand_pdbqt,out_pdbqt,log" > "$OUTCSV"
echo "ligand_id,round,status,reason,detail" > "$FAILCSV"

hdr=$(head -n 1 "$PASSCSV")
if echo "$hdr" | grep -q "ligand_id"; then
  col="ligand_id"
elif echo "$hdr" | grep -q "name"; then
  col="name"
else
  echo "passed_log.csv must contain column ligand_id or name"
  echo "header: $hdr"
  exit 1
fi

python3 - << 'PY' "$PASSCSV" "$col" "$IDLIST"
import csv, sys
fp = sys.argv[1]
col = sys.argv[2]
outp = sys.argv[3]
seen = set()
with open(fp, newline='') as f, open(outp, "w") as out:
    r = csv.DictReader(f)
    for row in r:
        v = (row.get(col) or "").strip()
        if not v:
            continue
        if v in seen:
            continue
        seen.add(v)
        out.write(v + "\n")
PY

[[ -s "$IDLIST" ]] || { echo "no ligand ids extracted from passed_log.csv"; exit 1; }

resolve_lig() {
  local lid="$1"
  local lid2="${lid//,/_}"
  local p

  p="$R1ROOT/${lid}.pdbqt";        [[ -s "$p" ]] && { echo "R1|$p"; return 0; }
  p="$R1ROOT/${lid2}.pdbqt";       [[ -s "$p" ]] && { echo "R1|$p"; return 0; }
  p="$R1ROOT/pdbqt_clean/${lid}.pdbqt";  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }
  p="$R1ROOT/pdbqt_clean/${lid2}.pdbqt"; [[ -s "$p" ]] && { echo "R1|$p"; return 0; }
  p="$R1ROOT/pdbqt_meeko/${lid}.pdbqt";  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }
  p="$R1ROOT/pdbqt_meeko/${lid2}.pdbqt"; [[ -s "$p" ]] && { echo "R1|$p"; return 0; }

  p="$R2ROOT/${lid}.pdbqt";        [[ -s "$p" ]] && { echo "R2|$p"; return 0; }
  p="$R2ROOT/${lid2}.pdbqt";       [[ -s "$p" ]] && { echo "R2|$p"; return 0; }
  p="$R2ROOT/pdbqt_clean/${lid}.pdbqt";  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }
  p="$R2ROOT/pdbqt_clean/${lid2}.pdbqt"; [[ -s "$p" ]] && { echo "R2|$p"; return 0; }
  p="$R2ROOT/pdbqt_meeko/${lid}.pdbqt";  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }
  p="$R2ROOT/pdbqt_meeko/${lid2}.pdbqt"; [[ -s "$p" ]] && { echo "R2|$p"; return 0; }

  p="$R3ROOT/pdbqt_clean/${lid}.pdbqt";  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }
  p="$R3ROOT/pdbqt_clean/${lid2}.pdbqt"; [[ -s "$p" ]] && { echo "R3|$p"; return 0; }
  p="$R3ROOT/${lid}.pdbqt";        [[ -s "$p" ]] && { echo "R3|$p"; return 0; }
  p="$R3ROOT/${lid2}.pdbqt";       [[ -s "$p" ]] && { echo "R3|$p"; return 0; }
  p="$R3ROOT/pdbqt_meeko/${lid}.pdbqt";  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }
  p="$R3ROOT/pdbqt_meeko/${lid2}.pdbqt"; [[ -s "$p" ]] && { echo "R3|$p"; return 0; }

  return 1
}

while IFS= read -r lid; do
  [[ -z "$lid" ]] && continue

  res=$(resolve_lig "$lid")
  if [[ $? -ne 0 || -z "$res" ]]; then
    echo "$lid,NA,missing_ligand,not_found,checked:R1ROOT/R2ROOT/R3ROOT(+pdbqt_clean/+pdbqt_meeko,+comma_to_underscore)" >> "$FAILCSV"
    continue
  fi

  rnd="${res%%|*}"
  lig="${res#*|}"

  outp="$OUTDIR/${lid}_out.pdbqt"
  logp="$LOGDIR/${lid}.log"

  "$VINA_BIN" --receptor "$RECDIR/TSPO_receptor.pdbqt" --ligand "$lig" \
    --center_x 5.2 --center_y 12.8 --center_z 8.3 \
    --size_x 14 --size_y 14 --size_z 14 \
    --exhaustiveness "$EXH" --num_modes "$NMODES" --cpu "$CORES" \
    --out "$outp" > "$logp" 2>&1
  rc=$?

  if [[ $rc -eq 0 && -s "$outp" ]]; then
    energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$outp")
    [[ -z "$energy" ]] && energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$logp")
    [[ -z "$energy" ]] && energy="NA"
    echo "$lid,$rnd,$energy,$lig,$outp,$logp" >> "$OUTCSV"
  else
    msg=$(tail -n 1 "$logp" | tr ',' ';')
    [[ -z "$msg" ]] && msg="no_output_or_error"
    echo "$lid,$rnd,$rc,$msg,$logp" >> "$FAILCSV"
  fi
done < "$IDLIST"

echo "wrote $OUTCSV"
echo "wrote $FAILCSV"