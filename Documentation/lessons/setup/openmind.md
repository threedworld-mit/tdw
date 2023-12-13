###### Setup

# Run TDW on MIT Openmind

To run TDW on [MIT Openmind](https://openmind.mit.edu/) you must have valid Kerebos credentials.

[Read this to learn how to set up an Openmind account.](https://github.mit.edu/MGHPCC/openmind/wiki/Getting-started)

To login: `ssh <kerebos_name>@openmind.mit.edu` The password is your Kerebos password.

As a one-time setup step, install the `tdw` Python module:

```bash
pip install --user tdw
```

Every time you run TDW on Openmind:

1. Start FastX 3 remote desktop:

   - [Login into FastX 3](https://openmind7.mit.edu:3300/) with your Kerebos credentials.
   - Click the small "+" icon on the left-top corner.
   - Click xterm
   - Click Launch

2. In the xterm terminal launched by XFast, run this:

```bash
salloc --x11 -t 02:00:00 -N1 -n1 --gres=gpu:1 --constraint=vgl 
```

```bash
vglconnect nodeXXX
```

TODO: https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-GUI-with-VirtualGL-in-an-interactive-session