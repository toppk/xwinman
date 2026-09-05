#!/bin/sh
# Screenshot every page of the mirror and of public/ with headless Chrome and report pages that differ.
# Needs google-chrome and ImageMagick; side-by-side images for differing pages land in $OUT.
set -e
cd "$(dirname "$0")/.."
OUT=${OUT:-/tmp/xwinman-pixelcheck}; mkdir -p "$OUT"
for f in mirror/xteddy.org/xwinman/*.html; do
  p=$(basename "$f" .html)
  for side in m p; do
    [ $side = m ] && src="$PWD/$f" || src="$PWD/public/$p.html"
    google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars --window-size=1100,1400 \
      --screenshot="$OUT/$side-$p.png" "file://$src" >/dev/null 2>&1
  done
  if [ "$(magick compare -metric AE "$OUT/m-$p.png" "$OUT/p-$p.png" null: 2>&1)" != "0 (0)" ]; then
    magick "$OUT/m-$p.png" "$OUT/p-$p.png" +append "$OUT/sbs-$p.png"
    echo "DIFFERS $p  ($OUT/sbs-$p.png)"
  fi
done
echo "done; screenshots in $OUT"
