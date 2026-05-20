# naca0012-nekrs-scaling

Reproducibility repository for the BEng dissertation
**"High-Fidelity Simulations of Wall-Bounded Flows Over a 3D Aerofoil Using GPU and CPU Architectures"**
(University of Manchester, BEng Aerospace Engineering, 2026).

This repository contains every input deck, mesh-generation reference, solver configuration, SLURM submission script, and post-processing reference needed to reproduce the strong-scaling, weak-scaling, throughput, validation, and production-LES results reported in the dissertation, on hardware comparable to the University of Manchester Computational Shared Facility (CSF3).

The dissertation itself is not redistributed here; consult the submitted PDF for the full description of methodology, results, and discussion.

## Repository structure

```
naca0012-nekrs-scaling/
├── README.md                     # This file
├── LICENSE                       # MIT
├── CITATION.cff                  # GitHub citation metadata
├── .gitignore                    # Standard CFD/LaTeX/Python ignores
│
├── cases/                        # Solver case directories
│   ├── README.md
│   ├── nek5000_validation/       # 25,000-step CPU validation run with force logging
│   ├── nek5000_scaling/          # CPU strong- and weak-scaling case (500-step)
│   ├── nekrs_scaling/            # GPU strong- and weak-scaling case (500-step)
│   └── nekrs_production/         # GPU production LES (100,000 steps on 4 A100s)
│
├── meshes/                       # Gmsh source files and conversion driver
│   └── README.md                 # Documents the M2-M5 mesh family
│
├── validation/                   # Post-hoc validation tooling
│   ├── README.md
│   └── naca0012_corrected.usr    # Corrected userchk using boundaryID array
│
└── env/                          # Build environment for CSF3 module stack
    ├── build_nek5000.sh
    └── build_nekrs.sh
```

## Quick start (on CSF3 or equivalent A100 / Xeon Platinum 8358 cluster)

### Build Nek5000

```bash
git clone https://github.com/Nek5000/Nek5000.git $HOME/Nek5000
cd $HOME/Nek5000
source path/to/this/repo/env/build_nek5000.sh
```

### Build NekRS

```bash
git clone https://github.com/Nek5000/nekRS.git $HOME/nekRS
cd $HOME/nekRS
source path/to/this/repo/env/build_nekrs.sh
```

### Run a Nek5000 validation case

```bash
cp cases/nek5000_validation/* /path/to/run/dir/
cp meshes/naca0012_m4.re2  /path/to/run/dir/
cp meshes/naca0012_m4.ma2  /path/to/run/dir/
cd /path/to/run/dir
sbatch submit.slurm
```

### Run a NekRS production case

```bash
cp cases/nekrs_production/* /path/to/run/dir/
cp meshes/naca0012_m4.re2  /path/to/run/dir/
cp meshes/naca0012_m4.ma2  /path/to/run/dir/
cd /path/to/run/dir
sbatch submit.slurm
```

## Reproducing the dissertation results

| Dissertation reference | How to reproduce |
|---|---|
| Table 4.3, Figure 4.2 (CPU strong scaling, 8-128 cores) | Run `cases/nek5000_scaling/` with `submit.slurm` SBATCH `--ntasks` set to 8, 16, 32, 64, 128 in turn |
| Table 4.3, Figure 4.2 (GPU strong scaling, 1-4 A100s) | Run `cases/nekrs_scaling/` with SBATCH `--gres=gpu:1`, `:2`, `:4` in turn |
| Table 4.5 (CPU weak scaling) | Run `cases/nek5000_scaling/` paired with meshes M2-M5 at 16, 32, 64, 128 cores |
| Table 4.6 (throughput) | Reduction notebook in `postproc/`, runs against the timing outputs from the above |
| Table 4.7 (production statistics) | Run `cases/nekrs_production/` on 4 A100s |
| Table 4.8 (energy and carbon) | Run `cases/nekrs_production/` with `nvidia-smi` 1Hz logging enabled, reduce with `postproc/` notebook |

## Software versions

All results in the dissertation were obtained with the following pinned versions. Re-runs against newer toolchain versions risk differing in build behaviour and would need to be re-validated.

| Component | Version | Source |
|---|---|---|
| Nek5000 | v19.0 | https://github.com/Nek5000/Nek5000 |
| NekRS | v26.0 | https://github.com/Nek5000/nekRS |
| Gmsh | 4.11.1 | https://gmsh.info |
| OpenMPI | 5.0.6 | CSF3 module |
| CUDA Toolkit | 12.6.2 | CSF3 module |
| NVIDIA HPC SDK | 25.3 | CSF3 module |
| GCC | 14.2.0 | CSF3 module |
| Python | 3.11.5 | local install |
| NumPy | 1.26 | pip |
| pandas | 2.1 | pip |
| matplotlib | 3.8 | pip |
| SciPy | 1.11 | pip |
| Green Algorithms | v2.2 | https://green-algorithms.org |

## Known limitations

The submitted dissertation reports the quantitative validation against the Kurtulus (2015), Di Ilio et al. (2018), Rossi et al. (2018), and Durante et al. (2020) reference range as **partial**. The corrected force-logging routine in `validation/naca0012_corrected.usr` resolves the `cbc`-vs-`usrdat2` ordering issue that produced zero output in the original validation run, and a re-run with this file would close the validation gap. See Section 5.2 and Appendix C of the dissertation for full discussion.

The four-GPU per-user cap on the CSF3 `gpuA` partition limited the GPU strong-scaling sweep to three data points (1, 2, 4 A100s) and the GPU weak-scaling sweep to two (M2/2 A100s and M3/4 A100s). On a system without this constraint the strong-scaling sweep can naturally be extended.

## How to cite

If you use this repository or build on the methodology, please cite the dissertation. A `CITATION.cff` file is included for automatic citation tooling via GitHub.

## License

Released under the MIT License. See `LICENSE` for the full text.

## Contact

For questions about the case setup, build environment, or post-processing, please open a GitHub issue on this repository.
