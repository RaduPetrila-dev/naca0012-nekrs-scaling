#!/bin/bash --login
#SBATCH --partition=gpuA
#SBATCH --nodes=1
#SBATCH --gres=gpu:4
#SBATCH --ntasks-per-node=4
#SBATCH --time=06:00:00
#SBATCH --job-name=nekrs_production
#SBATCH --output=%x_%j.out

# University of Manchester CSF3 - NekRS production LES.
# 100,000 steps on mesh M4 across four A100 80GB SXM accelerators.
# Concurrent nvidia-smi power sampling at 1 Hz feeds the
# energy/carbon analysis (Section 4.6 of the dissertation).

module load gcc/14.2.0 openmpi/5.0.6 cuda/12.6.2 nvhpc/25.3

cd $SLURM_SUBMIT_DIR

# Start nvidia-smi power logging in the background
nvidia-smi \
  --query-gpu=timestamp,index,power.draw,utilization.gpu,memory.used \
  --format=csv \
  --loop=1 \
  > nvsmi_power.log 2>&1 &
NVSMI_PID=$!

# Run NekRS production simulation
mpirun -n $SLURM_NTASKS \
  $HOME/nekRS/bin/nekrs --setup naca0012 \
  > run.log 2>&1

# Stop nvidia-smi logging
kill -INT $NVSMI_PID 2>/dev/null
wait $NVSMI_PID 2>/dev/null

echo "Production run complete. Power log in nvsmi_power.log."
