###### Setup

# Setup TDW on MIT Openmind

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

Activate conda:

```bash
#!/bin/bash

module load openmind8/anaconda/3-2022.10
conda init bash
```

Then:

```bash
conda activate tdw
```

Allocate a GPU:

```bash
srun -p dicarlo -n 1 -t 02:00:00 --gres=gpu:1 --pty bash
```

Change `dicarlo` to your lab and the `-t` value to the desired time.

Allocate an X session:

```bash
srun -p dicarlo --x11 -t 02:00:00 --pty bash
```

Change `dicarlo` to your lab and the `-t` value to the desired time.
