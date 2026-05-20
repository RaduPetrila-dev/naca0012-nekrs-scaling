# validation/

This directory contains the post-hoc validation tooling and the corrected user routine that closes the force-logging gap discussed in Section 5.2 and Appendix B of the dissertation.

## Files

- `naca0012_corrected.usr` - identical copy of `cases/nek5000_validation/naca0012.usr`, the **corrected** Nek5000 user routine that replaces the original `cbc`-array check with a direct test of the integer `boundaryID` array. This avoids the startup-sequence ordering issue between `usrdat2` (which populates `cbc`) and `userchk` (which on this build is called before `usrdat2`).

## Why this directory exists alongside `cases/nek5000_validation/`

The dissertation references the corrected user routine in two places: Section 5.2 names it as the path to closing the validation gap, and Appendix B Section B.5 names it as the residual-risk mitigation. The two references point at this directory rather than into the case directories because Appendix C of the dissertation describes a "validation" subdirectory specifically for the corrected file. The duplication of `naca0012.usr` between `cases/nek5000_validation/` and here is intentional and ensures that either reference resolves to the same file.

## Closing the validation gap

A follow-up Nek5000 validation run with this user routine would close the validation gap with approximately two to three days of additional CSF3 wall-clock:

```bash
# Copy validation case and substitute the corrected user routine
cp -r ../cases/nek5000_validation  $SCRATCH/validation_corrected
cp naca0012_corrected.usr           $SCRATCH/validation_corrected/naca0012.usr

# Mesh and binary as before
cp /path/to/meshes/naca0012_m4.re2  $SCRATCH/validation_corrected/naca0012.re2
cp /path/to/meshes/naca0012_m4.ma2  $SCRATCH/validation_corrected/naca0012.ma2

cd $SCRATCH/validation_corrected
$NEK_SOURCE_ROOT/bin/makenek naca0012
sbatch submit.slurm
```

The `forces.dat` produced by the corrected run can be reduced to mean `Cd`, mean `Cl`, RMS fluctuations, and Strouhal number using the validation notebook in `postproc/`. The reference range from the four independent studies cited in the dissertation (Table 4.2) is:

| Quantity | Reference mean | Reference spread |
|---|---|---|
| `Cd` | 0.120 | ±1.7% |
| `St` | 0.178 | ±1.1% |

## Note on the post-hoc Python integration

The dissertation describes a second validation route in Section 5.2 (a Python script using PyMech to read the production-run snapshots and integrate surface stress directly). That script is not included here because the dissertation reports it produced values inconsistent with the reference range (a probable outward-normal-orientation convention bug), and the bug was not isolated within the project window. A future investigator wishing to revisit this route should consult Section 5.2 for the diagnosis before re-implementing.
