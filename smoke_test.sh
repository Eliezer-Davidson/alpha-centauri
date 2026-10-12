#!/usr/bin/env bash
# Smoke test: build ONE part and run every gate it has.
#
# The foot is the right part for this -- it is two solids in two materials with
# a snap fit, a swept ground-clearance study across 8 azimuths, and a retention
# interference check, so if the gate machinery works at all it works here.
# ~35 s cold, ~18 s warm on a laptop. Expect the last line to read
# "ALL GATES GREEN".
#
# Two lines in a PASSING run read FAIL, and that is expected: partcheck's
# watertight probe cannot pass a sphere (the pole fan leaves zero-length edges),
# so both foot solids print "FAIL watertight". foot.py proves closure
# independently -- assert_closed(), line 537, reported at line 748 as
# "closure: ... verified independently (... the known sphere artifact)" -- and
# that is why the run still ends GREEN and exits 0.
set -euo pipefail
cd "$(dirname "$0")"

CADPY="${CADPY:-edu/.cadenv/bin/python}"
if [ ! -x "$CADPY" ]; then
  echo "No CAD interpreter at $CADPY." >&2
  echo "  python3.11 -m venv edu/.cadenv" >&2
  echo "  edu/.cadenv/bin/pip install build123d trimesh rtree numpy matplotlib pillow" >&2
  echo "Or set CADPY=/path/to/python." >&2
  exit 1
fi

echo "== cad/alpha_centauri/foot.py =="
"$CADPY" cad/alpha_centauri/foot.py
