###### Setup

# Run TDW on MIT Openmind

To run TDW on [MIT Openmind](https://openmind.mit.edu/) you must have valid Kerebos credentials.

[Read this to learn how to set up an Openmind account.](https://github.mit.edu/MGHPCC/openmind/wiki/Getting-started)

To login: `ssh <kerebos_name>@openmind.mit.edu` The password is your Kerebos password.

## Setup

1. Login
2. Use Apptainer to build a Docker image for Python:

```python
srun -t 500 --constraint=rocky8 -c 4 --mem=10G --pty bash
module av openmind8/apptainer
apptainer build --sandbox python-latest docker://python:latest
```

2. Install the `tdw` Python module:

```bash
pip install --user tdw
```

3. Generate an ssh key, add it to the authorized keys, and change its permission

```bash
ssh-keygen
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh/authorized_keys
```

  *[Source](https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-log-in-a-compute-node%3F)*

## Usage

1. Login
2. Start FastX 3 remote desktop:

   - [Login into FastX 3](https://openmind7.mit.edu:3300/) with your Kerebos credentials.
   - Click the small "+" icon on the left-top corner.
   - Click xterm
   - Click Launch

3. In the xterm terminal launched by XFast, run this:

```bash
salloc --x11 -t 02:00:00 -N1 -n1 --gres=gpu:1 --constraint=vgl 
```

  This will output a node name:

```
salloc: Nodes node041 are ready for job
```

4. In the xterm terminal launched by XFast, run this:

```bash
vglconnect nodeXXX
```

  Replace `XXX` with the node ID outputted by step 2, for example `041`.
  
  If the terminal asks you if you want to continue connecting, type `yes` press enter, enter your password, and press enter again.
  
  *[Source](https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-GUI-with-VirtualGL-in-an-interactive-session)*