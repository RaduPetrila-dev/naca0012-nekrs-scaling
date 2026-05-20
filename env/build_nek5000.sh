#!/bin/bash
# ============================================================
# Build environment for Nek5000 on University of Manchester CSF3
# ============================================================
# Source this file from a fresh shell on CSF3 before building
# Nek5000 from a fresh clone. Reproduced from Appendix C.4 of
# the dissertation. Pinned versions match the build environment
# under which every result in the dissertation was obtained.
# ============================================================

module purge
module load gcc/14.2.0
module load openmpi/5.0.6

export CC=mpicc
export FC=mpif90
export F77=mpif90

# The -mcmodel=large flag is required because mesh M4 and larger
# trigger a relocation overflow in Nek5000's static-allocation
# Fortran arrays without it. The -std=legacy flag is required
# because GCC 14 rejects several Fortran 77 constructs in the
# Nek5000 source tree by default.
export FFLAGS="-std=legacy -mcmodel=large"
export CFLAGS="-mcmodel=large"
export USR_LFLAGS="-std=legacy -mcmodel=large"

# CPATH addition is needed so the bare gcc/gfortran (used in
# parts of the Nek5000 build) can find the OpenMPI headers.
export CPATH=$CPATH:$MPI_HOME/include

# Path to the Nek5000 source tree (adjust if cloned elsewhere)
export NEK_SOURCE_ROOT=$HOME/Nek5000

# Build the naca0012 binary
# Run this from the case directory containing naca0012.usr:
#
#   $NEK_SOURCE_ROOT/bin/makenek naca0012
#
# which produces the nek5000 executable in the same directory.

echo "Nek5000 build environment loaded."
echo "  GCC version: $(gcc --version | head -1)"
echo "  MPI:         $(which mpicc)"
echo "  NEK_SOURCE_ROOT=$NEK_SOURCE_ROOT"
echo ""
echo "Next steps: cd to a case directory and run:"
echo "  \$NEK_SOURCE_ROOT/bin/makenek naca0012"
