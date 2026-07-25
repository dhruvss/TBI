#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/dhruv/Documents/Research/TBI"
LOCAL="/Users/dhruv/Documents/Research/TBI-tracer"
SETUP="$LOCAL/MD_runs/A15/openmm_setup_001"

PDB="$SETUP/equilibration_stage3/A15_equil_stage3.pdb"
SYSTEM_XML="$SETUP/A15_system.xml"

# The setup directory retains the legacy A15 name, but the frozen identity map
# establishes that this is canonical A8 / TSPO-C08.
OUTDIR="$SETUP/opencl_2fs_10ns_canonical_A8"
PREFIX="A8_opencl_2fs_10ns"

RUNNER="$REPO/md/scripts/run_openmm_unrestrained_md.py"
ANALYZER="$REPO/md/scripts/analyze_openmm_trajectory_v2.py"

for f in "$PDB" "$SYSTEM_XML" "$RUNNER" "$ANALYZER"; do
  [[ -f "$f" ]] || { echo "ERROR: Missing required file: $f" >&2; exit 1; }
done

if [[ -e "$OUTDIR/$PREFIX.dcd" || -e "$OUTDIR/$PREFIX.csv" ]]; then
  echo "ERROR: Existing A8 10 ns output detected in:"
  echo "  $OUTDIR"
  echo "Refusing to overwrite. Rename/archive the existing folder first."
  exit 1
fi

mkdir -p "$OUTDIR"

echo "Canonical identity: TSPO-C08"
echo "Primary legacy ID: A8"
echo "Legacy setup alias: A15"
echo "Input PDB: $PDB"
echo "System XML: $SYSTEM_XML"
echo "Output: $OUTDIR"
echo

python "$RUNNER" \
  --pdb "$PDB" \
  --system-xml "$SYSTEM_XML" \
  --outdir "$OUTDIR" \
  --prefix "$PREFIX" \
  --platform OpenCL \
  --steps 5000000 \
  --timestep-fs 2.0 \
  --temperature-k 300 \
  --report-interval 5000 \
  --checkpoint-interval 50000

python "$ANALYZER" \
  --topology-pdb "$PDB" \
  --trajectory-dcd "$OUTDIR/$PREFIX.dcd" \
  --log-csv "$OUTDIR/$PREFIX.csv" \
  --outdir "$OUTDIR/analysis_pbc_corrected" \
  --ligand-resname UNK \
  --contact-cutoff-a 4.0 \
  --pocket-definition-cutoff-a 6.0 \
  --frame-stride 1 \
  --write-aligned-dcd

echo
echo "============================================================"
echo "Canonical A8 / TSPO-C08 10 ns summary"
echo "============================================================"
cat "$OUTDIR/analysis_pbc_corrected/trajectory_summary_pbc_corrected.txt"

echo
echo "Monitor during the run with:"
echo "tail -f \"$OUTDIR/$PREFIX.csv\""
