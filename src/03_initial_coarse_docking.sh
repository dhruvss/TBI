#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RECEPTOR="$PROJECT_ROOT/docking/TSPO/TSPO_receptor.pdbqt"
LIGAND="${1:-}"
OUTPUT="${2:-}"

if [[ -z "$LIGAND" || -z "$OUTPUT" ]]; then
  echo "Usage: $0 <ligand.pdbqt> <output-prefix>"
  exit 1
fi

if [[ ! -f "$RECEPTOR" ]]; then
  echo "Missing receptor: $RECEPTOR"
  exit 1
fi

if [[ ! -f "$LIGAND" ]]; then
  echo "Missing ligand: $LIGAND"
  exit 1
fi

vina --receptor "$RECEPTOR" \
     --ligand "$LIGAND" \
     --center_x 5.2 \
     --center_y 12.8 \
     --center_z 8.3 \
     --size_x 20 \
     --size_y 20 \
     --size_z 20 \
     --exhaustiveness 8 \
     --num_modes 1 \
     --out "${OUTPUT}.pdbqt" > "${OUTPUT}.log"
