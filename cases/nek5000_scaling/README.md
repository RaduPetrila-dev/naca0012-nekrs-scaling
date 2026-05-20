# Nek5000 scaling case

500-step CPU timing runs for strong-scaling and weak-scaling measurements. The first 50 steps are discarded as warm-up; the mean step time is reported over the remaining 450 steps.

## Files

- `naca0012.par` - solver configuration (numSteps = 500, identical numerics to validation case)
- `naca0012.usr` - minimal user routines: curve stripping, boundary mapping, no force logging
- `submit.slurm` - SLURM submission template; edit `--ntasks` per scaling point

## Strong-scaling sweep (all on mesh M4)

| Cores | `--ntasks` |
|---|---|
| 8 | 8 |
| 16 | 16 |
| 32 | 32 |
| 64 | 64 |
| 128 | 128 |

## Weak-scaling sweep (each point on a different mesh)

| Mesh | Cores | Per-rank elements (target ≈ 317) |
|---|---|---|
| M2 (5,076 el.) | 16 | 317 |
| M3 (10,504 el.) | 32 | 328 |
| M4 (20,060 el.) | 64 | 313 |
| M5 (40,396 el.) | 128 | 316 |

## How to run a single scaling point

```bash
mkdir -p $SCRATCH/nek_scaling_64core
cp naca0012.par naca0012.usr submit.slurm $SCRATCH/nek_scaling_64core/
cp /path/to/meshes/naca0012_m4.re2  $SCRATCH/nek_scaling_64core/naca0012.re2
cp /path/to/meshes/naca0012_m4.ma2  $SCRATCH/nek_scaling_64core/naca0012.ma2
cd $SCRATCH/nek_scaling_64core
sbatch submit.slurm
```

## Where the timing data lives

Nek5000 prints per-step wall-clock time to stdout. After the job finishes, the timing column can be extracted from `run.log` and reduced with the strong-scaling and weak-scaling notebooks in `postproc/`.

## Expected wall-clock times

Approximate values on CSF3 Xeon Platinum 8358 nodes, from Section 4.2 of the dissertation:

| Cores | Step time (s) | Total run time |
|---|---|---|
| 8 | 5.373 | ~45 min |
| 16 | 2.821 | ~24 min |
| 32 | 1.872 | ~16 min |
| 64 | 0.922 | ~8 min |
| 128 | 0.481 | ~4 min |
