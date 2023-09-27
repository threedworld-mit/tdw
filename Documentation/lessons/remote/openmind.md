# Openmind

To run TDW on [MIT Openmind](https://openmind.mit.edu/) you must have valid Kerebos credentials.

[Read this to learn how to set up an Openmind account.](https://github.mit.edu/MGHPCC/openmind/wiki/Getting-started)

To login: `ssh <kerebos_name>@openmind.mit.edu` The password is your Kerebos password.

## First time setup

```
module load openmind8/apptainer/1.1.7
```

```
export APPTAINER_CACHEDIR="/om2/user/$USER/.apptainer"
```

```
singularity build --sandbox tdw docker://alters/tdw:<version>
```

Replace `<version>` with the latest version of TDW, e.g. `1.12.10`

## Every time you login

```
module load openmind8/apptainer/1.1.7
```

```
export APPTAINER_CACHEDIR="/om2/user/$USER/.apptainer"
```

To start using a GPU:

```
srun -n 1 -t 02:00:00 --gres=gpu:1 --pty bash
```

- `-n`  The number of CPUs
- `-t` The time allotted
- `gpu:1` The number of GPUs

Then wait for the resources to be allocated.