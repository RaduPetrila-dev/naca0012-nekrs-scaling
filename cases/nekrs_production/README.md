# NekRS production LES

100,000-step production run on mesh M4 across four NVIDIA A100 80GB SXM accelerators. The first 20,000 steps are discarded as transient; statistics are accumulated over the remaining 80,000 steps, equivalent to 40 flow-through times at the free-stream velocity.

## Files

- `naca0012.par` - NekRS solver configuration (`numSteps = 100000`, `checkpointInterval = 4000`)
- `naca0012.udf` - host-side user functions
- `naca0012.oudf` - device-side boundary functions
- `submit.slurm` - SLURM submission script with concurrent `nvidia-smi` 1 Hz power sampling

## Why four GPUs

The strong-scaling tests were completed at 1, 2, and 4 A100s. The production allocation matched the largest tested configuration so the reported production wall-clock figure (3.20 hours) is directly comparable to the 4-A100 strong-scaling test. The dissertation discusses the energy-efficiency consequences of this choice in Section 5.5.

## How to run

```bash
mkdir -p $SCRATCH/nekrs_production
cp naca0012.par naca0012.udf naca0012.oudf submit.slurm $SCRATCH/nekrs_production/
cp /path/to/meshes/naca0012_m4.re2  $SCRATCH/nekrs_production/naca0012.re2
cp /path/to/meshes/naca0012_m4.ma2  $SCRATCH/nekrs_production/naca0012.ma2
cd $SCRATCH/nekrs_production
sbatch submit.slurm
```

## Expected output

- `naca0012.f00001` through `naca0012.f00025` - flow-field snapshots every 4,000 steps (25 snapshots total, the first 5 in the transient window)
- `run.log` - NekRS stdout including per-step timing
- `nvsmi_power.log` - 1 Hz `nvidia-smi` power, utilisation, and memory samples for the four accelerators

## Expected wall-clock

Approximately 3.20 hours of wall-clock time on the CSF3 four-A100 GPU node. Average steady-state step time is 0.104 s after the JIT-compilation transient.

## Energy and carbon

The `nvsmi_power.log` time series is reduced to total accelerator energy by the energy notebook in `postproc/`. The Green Algorithms framework (Lannelongue et al. 2021) is applied with:

- PUE = 1.5 (conventional figure for university-tier UK data centres)
- Grid carbon intensity = 128 gCO2e/kWh (rolling 12-month UK average, early 2026)

The dissertation reports the resulting carbon footprint at approximately 0.74 kg CO2e (300 W per accelerator estimate) or 0.98 kg (400 W TDP upper bound).

## Validation status

The production run does not include force logging because of the `userchk` configuration issue documented in Appendix B of the dissertation. The corrected user routine in `validation/naca0012_corrected.usr` would resolve this in a follow-up Nek5000 validation run; the production NekRS run itself uses NekRS's separate force-logging mechanism (not used in this submission). See Section 5.2 of the dissertation for the full validation discussion.
