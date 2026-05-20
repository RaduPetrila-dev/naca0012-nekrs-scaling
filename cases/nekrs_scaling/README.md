# NekRS scaling case

500-step GPU timing runs for strong-scaling and weak-scaling measurements on NVIDIA A100 80GB accelerators via NekRS v26. Numerics match the Nek5000 case at $N=7$ with second-order OIFS-BDF (NekRS `tombo2`).

## Files

- `naca0012.par` - NekRS solver configuration
- `naca0012.udf` - host-side user functions (initial condition)
- `naca0012.oudf` - device-side boundary functions
- `submit.slurm` - SLURM submission template; edit `--gres=gpu:N` per scaling point

## Strong-scaling sweep (all on mesh M4)

| A100s | `--gres` | `--ntasks-per-node` |
|---|---|---|
| 1 | `gpu:1` | 1 |
| 2 | `gpu:2` | 2 |
| 4 | `gpu:4` | 4 |

The four-GPU per-user limit on the CSF3 `gpuA` partition is what capped the sweep at three points; the dissertation discusses this constraint and its bearing on the GPU strong-scaling plateau in Section 5.3.2.

## Weak-scaling sweep (mesh per GPU count)

| Mesh | A100s |
|---|---|
| M2 (5,076 el.) | 2 |
| M3 (10,504 el.) | 4 |

Only two points were possible because mesh M1 was excluded as globally invalid and the M4/8-GPU pairing was blocked by the per-user limit. The dissertation reports this as a bounded verification rather than a fitted curve (Section 5.4.2).

## How to run a single scaling point

```bash
mkdir -p $SCRATCH/nekrs_scaling_4gpu
cp naca0012.par naca0012.udf naca0012.oudf submit.slurm \
   $SCRATCH/nekrs_scaling_4gpu/
cp /path/to/meshes/naca0012_m4.re2  $SCRATCH/nekrs_scaling_4gpu/naca0012.re2
cp /path/to/meshes/naca0012_m4.ma2  $SCRATCH/nekrs_scaling_4gpu/naca0012.ma2
cd $SCRATCH/nekrs_scaling_4gpu
sbatch submit.slurm
```

## Where the timing data lives

NekRS prints per-step solver timing to stdout. After the run completes the timing column can be extracted from `run.log` and reduced with the strong-scaling notebook in `postproc/`.

## Expected wall-clock times

Approximate values on CSF3 A100 80GB SXM accelerators, from Section 4.2 of the dissertation:

| A100s | Step time (s) | Per-GPU elements (M4) |
|---|---|---|
| 1 | 0.200 | 20,060 |
| 2 | 0.186 | 10,030 |
| 4 | 0.200 | 5,015 |

The flat profile across 1, 2, and 4 GPUs is the plateau characterised in Section 5.3.2 of the dissertation. It is the expected behaviour at this problem size on this hardware, not a software defect.
