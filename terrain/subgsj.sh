#!/bin/bash
#SBATCH -p amd_256
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -c 1
#SBATCH -J terrain
srun python terrain.py

