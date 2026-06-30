# === Round 3 docking (Vina 1.2.5) ===
cd ~/Documents/Research/TBI-tracer
eval "$(/Users/dhruv/miniconda3/bin/conda shell.zsh hook)"
conda activate tspo-tracer

BASE=~/Documents/Research/TBI-tracer
RECDIR="$BASE/docking/TSPO"
LIGDIR="$BASE/docking/emap_enum_round3/pdbqt_meeko"   # or .../pdbqt_clean if that's what you generated
OUTCSV="$BASE/docking/results_round3_coarse.csv"
FAILCSV="$BASE/docking/results_round3_failures.csv"

VINA_BIN=$(command -v vina)
[[ -x "$VINA_BIN" ]] || { echo "vina not found in env tspo-tracer"; exit 1; }

# receptor cleanup (same as R1/R2)
grep -vE '^(ROOT|BRANCH|ENDBRANCH|ENDROOT|TORSDOF)' "$RECDIR/TSPO_prepped.pdbqt" > "$RECDIR/TSPO_receptor.pdbqt"

CORES=$(sysctl -n hw.ncpu)
EXH=10
setopt null_glob
mkdir -p "$LIGDIR" "$BASE/docking/emap_enum_round3/out_coarse" "$BASE/docking/emap_enum_round3/logs_coarse"

echo "ligand_id,affinity_kcal_per_mol" > "$OUTCSV"
echo "ligand_id,status,reason,log" > "$FAILCSV"

for lig in "$LIGDIR"/*.pdbqt(N); do
  [[ "$lig" == *"_out.pdbqt" ]] && continue
  name=$(basename "$lig" .pdbqt)
  clean_name="${name//,/__}"

  outp="$BASE/docking/emap_enum_round3/out_coarse/${name}_out.pdbqt"
  logp="$BASE/docking/emap_enum_round3/logs_coarse/${name}.log"

  "$VINA_BIN" --receptor "$RECDIR/TSPO_receptor.pdbqt" --ligand "$lig" \
    --center_x 5.2  --center_y 12.8 --center_z 8.3 \
    --size_x   20   --size_y   20   --size_z   20 \
    --exhaustiveness "$EXH" --num_modes 1 --cpu "$CORES" \
    --out "$outp" > "$logp" 2>&1
  rc=$?

  if [[ $rc -eq 0 && -s "$outp" ]]; then
    energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$outp")
    [[ -z "$energy" ]] && energy=$(awk '/REMARK VINA RESULT/{print $4; exit}' "$logp")
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