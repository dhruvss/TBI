#!/usr/bin/env zsh

# === Round 3 docking (Vina 1.2.5) ===
set -uo pipefail

# Resolve repository paths from this script's location
SCRIPT_DIR="${0:A:h}"
PROJECT_ROOT="${SCRIPT_DIR:h}"

DOCKING_DIR="$PROJECT_ROOT/docking"
RECDIR="$DOCKING_DIR/TSPO"
ROUND3_DIR="$DOCKING_DIR/emap_enum_round3"

LIGDIR="$ROUND3_DIR/pdbqt_meeko"   # or pdbqt_clean if that is what was generated
OUTDIR="$ROUND3_DIR/out_coarse"
LOGDIR="$ROUND3_DIR/logs_coarse"

OUTCSV="$DOCKING_DIR/results_round3_coarse.csv"
FAILCSV="$DOCKING_DIR/results_round3_failures.csv"

VINA_BIN="$(command -v vina || true)"
[[ -n "$VINA_BIN" && -x "$VINA_BIN" ]] || {
  echo "AutoDock Vina was not found in PATH."
  echo "Activate the tspo-tracer environment before running this script."
  exit 1
}

[[ -f "$RECDIR/TSPO_prepped.pdbqt" ]] || {
  echo "Missing receptor input: $RECDIR/TSPO_prepped.pdbqt"
  exit 1
}

[[ -d "$LIGDIR" ]] || {
  echo "Missing ligand directory: $LIGDIR"
  exit 1
}

# Receptor cleanup, same as R1/R2
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

EXH=10

setopt null_glob
mkdir -p "$LIGDIR" "$OUTDIR" "$LOGDIR"

echo "ligand_id,affinity_kcal_per_mol" > "$OUTCSV"
echo "ligand_id,status,reason,log" > "$FAILCSV"

for lig in "$LIGDIR"/*.pdbqt(N); do
  [[ "$lig" == *"_out.pdbqt" ]] && continue

  name=$(basename "$lig" .pdbqt)
  clean_name="${name//,/__}"

  outp="$OUTDIR/${name}_out.pdbqt"
  logp="$LOGDIR/${name}.log"

  "$VINA_BIN" \
    --receptor "$RECDIR/TSPO_receptor.pdbqt" \
    --ligand "$lig" \
    --center_x 5.2 \
    --center_y 12.8 \
    --center_z 8.3 \
    --size_x 20 \
    --size_y 20 \
    --size_z 20 \
    --exhaustiveness "$EXH" \
    --num_modes 1 \
    --cpu "$CORES" \
    --out "$outp" > "$logp" 2>&1

  rc=$?

  if [[ $rc -eq 0 && -s "$outp" ]]; then
    energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$outp")
    [[ -z "$energy" ]] && \
      energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$logp")
    [[ -z "$energy" ]] && energy="NA"

    echo "$clean_name,$energy" >> "$OUTCSV"
  else
    msg=$(tail -n 1 "$logp" | tr ',' ';')
    [[ -z "$msg" ]] && msg="no_output_or_error"

    echo "$clean_name,NA" >> "$OUTCSV"
    echo "$clean_name,$rc,$msg,$logp" >> "$FAILCSV"
  fi
done

echo "wrote $OUTCSV"
echo "wrote $FAILCSV"
