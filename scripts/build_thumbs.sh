#!/usr/bin/env bash
# Build compressed webp thumbnails for the archive grid.
# Requires: caesiumclt (https://github.com/Lymphatus/caesium-clt) — cargo install caesium-clt
# Usage: ./scripts/build_thumbs.sh [SRC_DIR]   (default SRC_DIR=Screenshots)
# Output: archive/thumbs/<same-basename>.webp  (640px wide, q70, ~25KB each, ~130MB for 5340)
set -euo pipefail
SRC="${1:-Screenshots}"
OUT="archive/thumbs"
mkdir -p "$OUT"
caesiumclt -q 70 --width 640 --no-upscale --format webp \
  -o "$OUT" -R "$SRC" --overwrite never
echo "done — $(ls "$OUT" | wc -l) thumbs in $OUT"
