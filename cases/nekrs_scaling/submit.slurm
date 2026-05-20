#!/bin/bash --login
#SBATCH --partition=gpuA
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00
#SBATCH --job-name=nekrs_scaling
#SBATCH --output=%x_%j.out

# University of Manchester CSF3 - NekRS strong-scaling run template.
#
# For each strong-scaling point change the SBATCH directives above:
#   1 A100:  --gres=gpu:1   --ntasks-per-node=1
#   2 A100:  --gres=gpu:2   --ntasks-per-node=2
#   4 A100:  --gres=gpu:4   --ntasks-per-node=4
#
# Note: the four-GPU per-user limit on CSF3 gpuA capped the
# strong-scaling sweep at three points. On a system without
# this constraint the sweep can be extended to 8 and 16 GPUs.

module load gcc/14.2.0 openmpi/5.0.6 cuda/12.6.2 nvhpc/25.3

cd $SLURM_SUBMIT_DIR

# NekRS takes the case name as the only positional argument
mpirun -n $SLURM_NTASKS \
  $HOME/nekRS/bin/nekrs --setup naca0012 \
  > run.log 2>&1
