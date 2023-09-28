# Openmind

To run TDW on [MIT Openmind](https://openmind.mit.edu/) you must have valid Kerebos credentials.

[Read this to learn how to set up an Openmind account.](https://github.mit.edu/MGHPCC/openmind/wiki/Getting-started)

To login: `ssh <kerebos_name>@openmind.mit.edu` The password is your Kerebos password.

## First time setup

```bash
#!/bin/bash

# Add conda and a new environment.
module load openmind8/anaconda/3-2022.10
conda create -n tdw

# Initialize conda and "restart" bash.
conda init bash
exec bash

# Install tdw.
conda activate tdw
python3 -m pip install tdw

# Add apptainer (this will be used for Docker and Singularity).
module load openmind8/apptainer/1.1.7
export APPTAINER_CACHEDIR="/om2/user/$USER/.apptainer"

# Get the current version of TDW.
TDW_VERSION=$(python3 -c "import tdw.version; print(tdw.version.__version__)")

# Build TDW's Docker container.
singularity build --sandbox tdw docker://alters/tdw:$TDW_VERSION
```

## Every time you login

```bash
#!/bin/bash

# Initialize conda.
module load openmind8/anaconda/3-2022.10
conda init bash
exec bash
conda activate tdw

# Initialize apptainer (for the TDW container).
module load openmind8/apptainer/1.1.7
export APPTAINER_CACHEDIR="/om2/user/$USER/.apptainer"

# Allocate a GPU:
#
# -n The number of CPUs
# -t The time alloted. Example value for $1: 02:00:00
# gpu:1 The number of GPUs
srun -n 1 -t $1 --gres=gpu:1 --pty bash
```

Then wait for the GPU to be allocated. It can take several minutes.