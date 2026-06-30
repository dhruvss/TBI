#!/usr/bin/env zsh

set -uo pipefail

# Resolve repository paths from this script's location
SCRIPT_DIR="${0:A:h}"
PROJECT_ROOT="${SCRIPT_DIR:h}"

DOCKING_DIR="$PROJECT_ROOT/docking"
RECDIR="$DOCKING_DIR/TSPO"
PASSCSV="$DOCKING_DIR/passed_log.csv"

R1ROOT="$DOCKING_DIR/emap_enum_round1"
R2ROOT="$DOCKING_DIR/emap_enum_round2"
R3ROOT="$DOCKING_DIR/emap_enum_round3"

OUTROOT="$DOCKING_DIR/fine_all_rounds"
OUTDIR="$OUTROOT/out_pdbqt"
LOGDIR="$OUTROOT/logs"
OUTCSV="$OUTROOT/results_fine_all_rounds.csv"
FAILCSV="$OUTROOT/results_fine_all_rounds_failures.csv"
IDLIST="$OUTROOT/fine_ids.tmp"

VINA_BIN="$(command -v vina || true)"

[[ -n "$VINA_BIN" && -x "$VINA_BIN" ]] || {
  echo "AutoDock Vina was not found in PATH."
  echo "Activate the tspo-tracer environment before running this script."
  exit 1
}

[[ -f "$PASSCSV" ]] || {
  echo "Missing pass CSV: $PASSCSV"
  exit 1
}

[[ -f "$RECDIR/TSPO_prepped.pdbqt" ]] || {
  echo "Missing receptor input: $RECDIR/TSPO_prepped.pdbqt"
  exit 1
}

mkdir -p "$OUTDIR" "$LOGDIR"

grep -vE '^(ROOT|BRANCH|ENDBRANCH|ENDROOT|TORSDOF)' \
  "$RECDIR/TSPO_prepped.pdbqt" \
  > "$RECDIR/TSPO_receptor.pdbqt"

# Detect available CPU cores on macOS or Linux
if command -v sysctl >/dev/null 2>&1; then
  CORES="$(sysctl -n hw.ncpu 2>/dev/null || echo 1)"
elif command -v nproc >/dev/null 2>&1; then
  CORES="$(nproc)"
else
  CORES=1
fi

EXH=32
NMODES=3

echo "ligand_id,round,affinity_kcal_per_mol,ligand_pdbqt,out_pdbqt,log" \
  > "$OUTCSV"

echo "ligand_id,round,status,reason,detail" \
  > "$FAILCSV"

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

python3 - "$PASSCSV" "$col" "$IDLIST" << 'PY'
import csv
import sys

fp = sys.argv[1]
col = sys.argv[2]
outp = sys.argv[3]

seen = set()

with open(fp, newline="") as source, open(outp, "w") as output:
    reader = csv.DictReader(source)

    for row in reader:
        value = (row.get(col) or "").strip()

        if not value:
            continue

        if value in seen:
            continue

        seen.add(value)
        output.write(value + "\n")
PY

[[ -s "$IDLIST" ]] || {
  echo "No ligand IDs extracted from passed_log.csv"
  exit 1
}

resolve_lig() {
  local lid="$1"
  local lid2="${lid//,/_}"
  local p

  p="$R1ROOT/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }

  p="$R1ROOT/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }

  p="$R1ROOT/pdbqt_clean/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }

  p="$R1ROOT/pdbqt_clean/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }

  p="$R1ROOT/pdbqt_meeko/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }

  p="$R1ROOT/pdbqt_meeko/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R1|$p"; return 0; }

  p="$R2ROOT/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }

  p="$R2ROOT/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }

  p="$R2ROOT/pdbqt_clean/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }

  p="$R2ROOT/pdbqt_clean/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }

  p="$R2ROOT/pdbqt_meeko/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }

  p="$R2ROOT/pdbqt_meeko/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R2|$p"; return 0; }

  p="$R3ROOT/pdbqt_clean/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }

  p="$R3ROOT/pdbqt_clean/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }

  p="$R3ROOT/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }

  p="$R3ROOT/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }

  p="$R3ROOT/pdbqt_meeko/${lid}.pdbqt"
  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }

  p="$R3ROOT/pdbqt_meeko/${lid2}.pdbqt"
  [[ -s "$p" ]] && { echo "R3|$p"; return 0; }

  return 1
}

while IFS= read -r lid; do
  [[ -z "$lid" ]] && continue

  res=$(resolve_lig "$lid")

  if [[ $? -ne 0 || -z "$res" ]]; then
    echo "$lid,NA,missing_ligand,not_found,checked:R1ROOT/R2ROOT/R3ROOT(+pdbqt_clean/+pdbqt_meeko,+comma_to_underscore)" \
      >> "$FAILCSV"
    continue
  fi

  rnd="${res%%|*}"
  lig="${res#*|}"

  outp="$OUTDIR/${lid}_out.pdbqt"
  logp="$LOGDIR/${lid}.log"

  "$VINA_BIN" \
    --receptor "$RECDIR/TSPO_receptor.pdbqt" \
    --ligand "$lig" \
    --center_x 5.2 \
    --center_y 12.8 \
    --center_z 8.3 \
    --size_x 14 \
    --size_y 14 \
    --size_z 14 \
    --exhaustiveness "$EXH" \
    --num_modes "$NMODES" \
    --cpu "$CORES" \
    --out "$outp" > "$logp" 2>&1

  rc=$?

  if [[ $rc -eq 0 && -s "$outp" ]]; then
    energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$outp")
    [[ -z "$energy" ]] && \
      energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$logp")
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
