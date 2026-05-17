#!/usr/bin/env bash
set -euo pipefail
ROOT="$HOME/22i-2327_F_FinalProject"
BIN="$ROOT/experiments/bin"
DATA="$ROOT/experiments/data_gap3"
OUT="$ROOT/experiments/gap3_runs.txt"
STATIC="$BIN/kmeans_static_gap1"
GUIDED="$BIN/kmeans_guided_gap1"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
K=256
ARGS="-c $K -v 1 -r 42 -R 1e-4"

: > "$OUT"
shopt -s nullglob
for f in $(ls -1 "$DATA"/gap3_N*_M*.bin 2>/dev/null | sort -t_M -k2 -n); do
  base=$(basename "$f" .bin)
  echo "======== $base naive static ========" | tee -a "$OUT"
  "$STATIC"  "$f" -a naive  $ARGS 2>&1 | tee -a "$OUT"
  echo "======== $base elkan static ========" | tee -a "$OUT"
  "$STATIC"  "$f" -a elkan  $ARGS 2>&1 | tee -a "$OUT"
  echo "======== $base elkan guided ========" | tee -a "$OUT"
  "$GUIDED" "$f" -a elkan  $ARGS 2>&1 | tee -a "$OUT"
done
