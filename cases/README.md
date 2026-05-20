# cases/

This directory contains the four solver case directories that produce every numerical result in the dissertation.

| Directory | Solver | Purpose | Compute target |
|---|---|---|---|
| `nek5000_validation/` | Nek5000 | 25,000-step validation run with force logging | 128 cores |
| `nek5000_scaling/` | Nek5000 | 500-step CPU strong/weak scaling timing runs | 8 to 128 cores |
| `nekrs_scaling/` | NekRS | 500-step GPU strong/weak scaling timing runs | 1 to 4 A100s |
| `nekrs_production/` | NekRS | 100,000-step production LES with power logging | 4 A100s |

Each directory has its own README documenting the files, the SLURM submit script, and the expected wall-clock. All four cases depend on the M4 mesh produced by the pipeline in `meshes/`, with the weak-scaling sweeps additionally requiring M2, M3, and M5.

## Identical numerics across the four cases

Each case uses identical numerical parameters (`Re = 1000`, `N = 7`, OIFS-BDF2 with sub-cycling = 2, residual tolerances of `1e-6` for pressure and `1e-8` for velocity, BoomerAMG preconditioner for the pressure solve in NekRS). The only differences between case directories are the number of steps and the boundary-condition / force-logging routines. This is what makes the cross-architecture performance comparison a like-for-like measurement.

## Build dependency

The solver binaries are built once (per architecture) and then the binary symlink or compiled object goes into each case directory:

```bash
# Build Nek5000 once
cd path/to/this/repo
source env/build_nek5000.sh
cp $HOME/Nek5000/bin/nek5000  cases/nek5000_validation/
cp $HOME/Nek5000/bin/nek5000  cases/nek5000_scaling/

# Build NekRS once
source env/build_nekrs.sh
# (NekRS uses a configured executable in $HOME/nekRS/bin/nekrs;
#  the submit scripts call it by absolute path so no copy needed)
```
