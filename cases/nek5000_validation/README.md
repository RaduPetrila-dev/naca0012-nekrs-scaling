# Nek5000 validation case

25,000-step CPU simulation on mesh M4 (≈20,060 elements, 10.27 × 10^6 DOF at N=7) with force logging enabled. Used to extract mean drag coefficient and Strouhal number for comparison against the published reference range of Kurtulus (2015), Di Ilio et al. (2018), Rossi et al. (2018), and Durante et al. (2020).

## Files

- `naca0012.par` - solver configuration (BDF2 + OIFS, Re = 1000)
- `naca0012.usr` - user routines including the **corrected** `userchk` that uses the integer `boundaryID` array rather than the character `cbc` array. This avoids the startup-sequence ordering issue documented in Section 5.2 of the dissertation that caused the original validation re-run to produce zero force output.
- `submit.slurm` - SLURM submission script for 128 cores on the CSF3 `multicore` partition

## Mesh dependency

This case expects `naca0012.re2` and `naca0012.ma2` (mesh M4) to be present in the run directory. Copy them from `meshes/` after running the Gmsh conversion pipeline (see `meshes/README.md`).

## How to run

```bash
mkdir -p $SCRATCH/nek_validation
cp naca0012.par naca0012.usr submit.slurm $SCRATCH/nek_validation/
cp /path/to/meshes/naca0012_m4.re2  $SCRATCH/nek_validation/naca0012.re2
cp /path/to/meshes/naca0012_m4.ma2  $SCRATCH/nek_validation/naca0012.ma2
cd $SCRATCH/nek_validation
sbatch submit.slurm
```

## Expected output

- `forces.dat` - per-step `Cd`, `Cl`, and their pressure and viscous components (8 columns, header row included)
- `naca0012.f0001`, `.f0002`, ... - flow-field snapshots at the configured `writeInterval`
- `run.log` - Nek5000 stdout for the run

## Post-processing

The `forces.dat` file can be reduced to mean `Cd`, mean `Cl`, RMS fluctuations, and Strouhal number using the validation notebook in `postproc/`.

## Expected wall-clock time

Approximately 2.9 hours on 128 cores on the CSF3 Xeon Platinum 8358 nodes. Add a margin for queue placement.
