#!/bin/bash --login
#SBATCH --partition=multicore
#SBATCH --ntasks=64
#SBATCH --time=02:00:00
#SBATCH --job-name=nek5k_scaling
#SBATCH --output=%x_%j.out

# University of Manchester CSF3 - Nek5000 scaling run template.
#
# Change the --ntasks line above for each strong-scaling point:
#   8, 16, 32, 64, 128 (CPU strong-scaling sweep on mesh M4)
#
# For weak-scaling pair each mesh with the matching core count:
#   M2 / 16, M3 / 32, M4 / 64, M5 / 128
# (per-rank element count held within +/- 3% of design target)

module load gcc/14.2.0 openmpi/5.0.6

cd $SLURM_SUBMIT_DIR

echo "naca0012"     >  SESSION.NAME
echo "$(pwd)/"      >> SESSION.NAME

mpirun -n $SLURM_NTASKS ./nek5000 > run.log 2>&1
