#!/bin/bash
# ============================================================
# Build environment for NekRS on University of Manchester CSF3
# ============================================================
# Source this file from a fresh shell on CSF3 before building
# NekRS from a fresh clone. The module stack matches the
# software version manifest in Appendix C.5 of the dissertation.
# ============================================================

module purge
module load gcc/14.2.0
module load openmpi/5.0.6
module load cuda/12.6.2
module load nvhpc/25.3

export CC=mpicc
export CXX=mpicxx
export FC=mpif90

# OCCA looks for CUDA at this location
export OCCA_CUDA_ENABLED=1
export OCCA_DIR=$HOME/nekRS/3rd_party/occa

# Path to the NekRS install tree (adjust if cloned elsewhere)
export NEKRS_HOME=$HOME/nekRS

# Build instructions:
#
#   cd $NEKRS_HOME
#   ./build.sh
#
# Notes:
#   - The OCCA build inside nekRS requires explicit
#     --allow-unsupported-compiler if you hit a compiler-version
#     check during the CUDA portion of the build (this was the
#     case for GCC 14 + CUDA 12.6 on CSF3 in early 2026).
#   - The final binary lands in $NEKRS_HOME/bin/nekrs.
#   - The case directories under cases/ invoke this binary by
#     absolute path; no copy into the case directory is needed.

echo "NekRS build environment loaded."
echo "  GCC:         $(gcc --version | head -1)"
echo "  MPI:         $(which mpicc)"
echo "  CUDA:        $(nvcc --version | tail -1)"
echo "  NEKRS_HOME:  $NEKRS_HOME"
echo ""
echo "Next steps:"
echo "  cd \$NEKRS_HOME && ./build.sh"
