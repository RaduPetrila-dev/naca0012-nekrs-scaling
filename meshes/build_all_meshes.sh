#!/bin/bash
# ============================================================
# Generate the M2-M5 mesh family and convert to Nek .re2
# ============================================================
# Run on a machine with GMSH and Nek5000's gmsh2nek tool both
# available. On CSF3 with the build environment from env/build_nek5000.sh,
# gmsh2nek lives in $NEK_SOURCE_ROOT/bin/gmsh2nek.
#
# This script reproduces the four mesh files used in the
# dissertation, with the calibrated lc-* parameters that produce
# the element counts reported in Table 3.1 (Methods).
# ============================================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# -- 1. Generate the four .msh files via Gmsh Python API ----------------

echo "=== Generating M2 (~5,076 hex) ==="
python3 generate_naca0012_mesh.py \
    --lc-wall 0.04  --lc-far 2.0  --lc-wake 0.2  \
    --nz 4 -o naca0012_M2.msh

echo "=== Generating M3 (~10,504 hex) ==="
python3 generate_naca0012_mesh.py \
    --lc-wall 0.028 --lc-far 1.4  --lc-wake 0.14 \
    --nz 4 -o naca0012_M3.msh

echo "=== Generating M4 (~20,060 hex) ==="
python3 generate_naca0012_mesh.py \
    --lc-wall 0.02  --lc-far 1.1  --lc-wake 0.1  \
    --nz 4 -o naca0012_M4.msh

echo "=== Generating M5 (~40,396 hex) ==="
python3 generate_naca0012_mesh.py \
    --lc-wall 0.013 --lc-far 0.8  --lc-wake 0.07 \
    --nz 4 -o naca0012_M5.msh

# -- 2. Convert each .msh to Nek .re2 via gmsh2nek ----------------------
#
# gmsh2nek is interactive. It prompts:
#   - mesh dimension: enter 3
#   - fluid .msh file name: enter the basename (no .msh suffix)
#   - solid mesh present: enter 0 (no)
#   - number of periodic surface pairs: enter 1
#   - periodic surface IDs: enter 5 6  (the two z-faces)
#   - re2 output file name: enter the desired output basename
#
# We script this with `here documents` for unattended conversion.

GMSH2NEK="${GMSH2NEK:-$HOME/Nek5000/bin/gmsh2nek}"
if [ ! -x "$GMSH2NEK" ]; then
    echo "ERROR: gmsh2nek not found at $GMSH2NEK"
    echo "Set GMSH2NEK environment variable to the correct path,"
    echo "or skip conversion and run gmsh2nek interactively on each .msh."
    exit 1
fi

for M in M2 M3 M4 M5; do
    echo "=== Converting naca0012_${M}.msh to naca0012_${M}.re2 ==="
    "$GMSH2NEK" <<EOF
3
naca0012_${M}
0
1
5 6
naca0012_${M}
EOF
done

echo
echo "=== Mesh family generation complete ==="
ls -1 naca0012_M*.msh naca0012_M*.re2
