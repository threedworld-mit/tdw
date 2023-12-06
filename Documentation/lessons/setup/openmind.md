###### Setup

# Run TDW on MIT Openmind

To run TDW on [MIT Openmind](https://openmind.mit.edu/) you must have valid Kerebos credentials.

[Read this to learn how to set up an Openmind account.](https://github.mit.edu/MGHPCC/openmind/wiki/Getting-started)

To login: `ssh <kerebos_name>@openmind.mit.edu` The password is your Kerebos password.

1. Load conda and install `tdw`

```bash
module load openmind8/anaconda/3-2022.10
pip install --user tdw
```

2. Allocate a GPU:

```bash
srun -p normal -n 1 -t 02:00:00 --gres=gpu:1 --pty bash
```

3. Start Xfast remote desktop:
   - [Login into FastX 3](https://openmind7.mit.edu:3300/) with your Kerebos credentials.
   - Click the small "+" icon on the left-top corner.
   - Click XFCE
   - Click Launch

4. Start X11:

```bash
srun -p normal --x11 -t 02:00:00 --pty bash
```
