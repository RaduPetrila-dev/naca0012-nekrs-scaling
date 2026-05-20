#!/bin/bash --login
#SBATCH --partition=multicore
#SBATCH --ntasks=128
#SBATCH --time=04:00:00
#SBATCH --job-name=nek5k_validation
#SBATCH --output=%x_%j.out

# University of Manchester CSF3 - Nek5000 validation run
# 25,000 steps on mesh M4 at 128 cores, force logging enabled

module load gcc/14.2.0 openmpi/5.0.6

cd $SLURM_SUBMIT_DIR

# Nek5000 expects the case name (no extension) and the working
# directory listed in the SESSION.NAME file
echo "naca0012"      >  SESSION.NAME
echo "$(pwd)/"       >> SESSION.NAME

mpirun -n $SLURM_NTASKS ./nek5000 > run.log 2>&1
