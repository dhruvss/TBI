#!/usr/bin/env bash
set -euo pipefail

# Edit only these two paths if your local layout differs.
BASE="/Users/dhruv/Documents/Research/TBI-tracer/MD_runs"
ANALYZER="/Users/dhruv/Documents/Research/TBI/md/scripts/analyze_openmm_trajectory_v2.py"

find_one() {
  local root="$1"
  local pattern="$2"
  local result
  result="$(find "$root" -type f -name "$pattern" 2>/dev/null | sort | head -n 1 || true)"
  [[ -n "$result" ]] || {
    echo "ERROR: Could not find '$pattern' under: $root" >&2
    return 1
  }
  printf '%s\n' "$result"
}

find_setup() {
  local ligand="$1"
  local setup_name="$2"
  local result
  result="$(find "$BASE" -type d -name "$setup_name" 2>/dev/null \
    | grep -E "/${ligand}(/|_|-)" \
    | sort | head -n 1 || true)"

  if [[ -z "$result" ]]; then
    result="$(find "$BASE" -type d -name "$setup_name" 2>/dev/null \
      | grep -i "$ligand" \
      | sort | head -n 1 || true)"
  fi

  [[ -n "$result" ]] || {
    echo "ERROR: Could not locate $setup_name for $ligand under $BASE" >&2
    return 1
  }
  printf '%s\n' "$result"
}

run_case() {
  local label="$1"
  local setup_dir="$2"
  local duration_pattern="$3"

  echo
  echo "============================================================"
  echo "Analyzing $label"
  echo "Setup: $setup_dir"
  echo "============================================================"

  local topology dcd log_csv outdir dcd_dir

  topology="$(find_one "$setup_dir" "*equil_stage3.pdb")"
  dcd="$(find_one "$setup_dir" "$duration_pattern")"
  dcd_dir="$(dirname "$dcd")"
  log_csv="${dcd%.dcd}.csv"

  if [[ ! -f "$log_csv" ]]; then
    log_csv="$(find "$dcd_dir" -maxdepth 1 -type f -name "*.csv" | sort | head -n 1 || true)"
  fi

  [[ -f "$log_csv" ]] || {
    echo "ERROR: Could not locate OpenMM CSV log beside: $dcd" >&2
    return 1
  }

  outdir="$dcd_dir/analysis_pbc_corrected"

  echo "Topology: $topology"
  echo "DCD:      $dcd"
  echo "CSV:      $log_csv"
  echo "Output:   $outdir"

  python "$ANALYZER" \
    --topology-pdb "$topology" \
    --trajectory-dcd "$dcd" \
    --log-csv "$log_csv" \
    --outdir "$outdir" \
    --ligand-resname UNK \
    --contact-cutoff-a 4.0 \
    --pocket-definition-cutoff-a 6.0 \
    --frame-stride 1 \
    --write-aligned-dcd

  echo
  echo "Summary for $label:"
  cat "$outdir/trajectory_summary_pbc_corrected.txt"
}

# Known 10 ns systems
A3_SETUP="$(find_setup "A3" "openmm_setup_001")"
A7_SETUP="$(find_setup "A7" "openmm_setup_001")"
AC_SETUP="$(find_setup "AC-5216|AC5216" "openmm_setup_003")"

run_case "A3 10 ns"      "$A3_SETUP" "*10ns*.dcd"
run_case "A7 10 ns"      "$A7_SETUP" "*10ns*.dcd"
run_case "AC-5216 10 ns" "$AC_SETUP" "*10ns*.dcd"

# Legacy 1 ns systems
A15_SETUP="$(find_setup "A15" "openmm_setup_001")"
A17_SETUP="$(find_setup "A17" "openmm_setup_001")"

run_case "Legacy A15 / canonical A8 1 ns" "$A15_SETUP" "*1ns*.dcd"
run_case "A17 1 ns"                       "$A17_SETUP" "*1ns*.dcd"

echo
echo "All requested analyses completed."
