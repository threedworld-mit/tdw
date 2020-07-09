# `binary_manager.py`

Launch `binary_manager.py` on a node to automatically:

* Start and configure builds (binaries).
* Connect each build to a local or remote controller.
* Garbage collect old running builds.
* Distribute builds across available GPUs sequentially.

### Usage

`binary_manager.py` and the build must be on the same machine. The controller can be on the same machine, or on a remote machine.

This script can be safely re-used to launch addition builds.

Each build will be allocated a separate GPU, unless there is already a build on each GPU of the machine.

1. Launch `binary_manager.py`

```bash
cd tdw/Python
```

```bash
python3 binary_manager.py
```

2. Launch the controller. For example implementation, see `minimal_remote.py`.

### Requirements

* Linux or macOS.
* Python 3
  * ZMQ

To set a default build, add TDW_BUILD_PATH to your shell's environmental variables:

```
echo 'export TDW_BUILD_PATH="/path/to/tdw.x86_64"' >> $HOME/.bashrc
source $HOME/.bashrc
```

### Arguments

| Argument           | Type   | Description                                                  | Default                               |
| ------------------ | ------ | ------------------------------------------------------------ | ------------------------------------- |
| `--listening_port` | string | Port binary manager will use to listen for requests.         | 5556                                  |
| `--build_path`     | string | Path to build.                                               | Environmental variable TDW_BUILD_PATH |
| `--force_glcore42` | bool   | Force each build to render with OpenGL 4.2 (see [Getting Started](../getting_started.md) for why you might want to do this). | True                                  |
| `--screen_width`   | int    | Screen width of each build, in pixels.                       | 256                                   |
| `--screen_height`  | int    | Screen height of each build, in pixels.                      | 256                                   |
| `--gpus`           | string | Specify which GPUs are allowed for a build, separated by commas (e.g. `0,1,2`). This won't set which specific GPU will be used by the build (which is handled automatically). | 0                                     |

