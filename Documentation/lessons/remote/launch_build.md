##### Misc. remote server topics

# Launch a TDW build on a remote server from a personal computer

## Step 1: Launch binary_manager.py on the remote server

[binary_manager.py](https://github.com/threedworld-mit/tdw/blob/master/Python/binary_manager.py) can be used to launch and manage TDW builds on a remote server.

### Setup

1. Copy [this file](https://github.com/threedworld-mit/tdw/blob/master/Python/binary_manager.py) to the remote server.
2. Make sure that the server has Python 3.6 or newer

### Usage

```bash
python3 binary_manager.py [ARGUMENTS]
```

| Argument           | Type | Default                          | Description                                                  |
| ------------------ | ---- | -------------------------------- | ------------------------------------------------------------ |
| `--listening_port` | str  | 5556                             | The socket port.                                             |
| `--build_path`     | str  | os.environ.get("TDW_BUILD_PATH") | The path to the build.                                       |
| `--force_glcore42` | bool | False                            | Use OpenGL 4.2 instead of latest system version. [Read this for more information.](../troubleshooting/common_errors.md) |
| `--screen_width`   | int  | 256                              | Screen width in pixels.                                      |
| `--screen_height`  | int  | 256                              | Screen height in pixels.                                     |
| `--gpus`           | str  | 0                                | GPUs to be used for rendering.                               |

## Step 2: Launch a controller with `RemoteBuildLauncher`

Use [`RemoteBuildLauncher`](../../python/remote_build_launcher.md) to launch a build on a remote server from a person computer. To use this, you need to have already launched `binary_manager.py` on the remote server.

This is a minimal example of a controller that uses `RemoteBuildLauncher` to connect to a remote build:

```python
import argparse
from tdw.controller import Controller
from tdw.remote_build_launcher import RemoteBuildLauncher


class MinimalRemote(Controller):
    """
    A minimal example of how to use the launch binaries daemon to
    start and connect to a build on a remote node. Note: the remote
    must be running binary_manager.py.
    """

    def __init__(self):
        args = self.parse_args()
        build_info = RemoteBuildLauncher.launch_build(args.listening_port,
                                                      args.build_address,
                                                      args.controller_address)

        super().__init__(port=build_info["build_port"])

    def parse_args(self):
        """
        Helper function that parses command line arguments .
        Returns parsed args.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--listening_port",
            default="5556",
            type=str,
            help="Port on which binary_manager is listening",
        )
        parser.add_argument(
            "--build_address",
            default="node14-ccncluster.stanford.edu",
            type=str,
            help="IP/hostname on which to launch build",
        )
        parser.add_argument(
            "--controller_address",
            default="node05-ccncluster.stanford.edu",
            type=str,
            help="Address of controller",
        )
        args = parser.parse_args()
        return args

    def run(self):
        # Create an empty environment.
        self.communicate({"$type": "create_empty_environment"})
        for i in range(100):
            # Do nothing. Receive a response from the build.
            resp = self.communicate([])
            print(resp)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    MinimalRemote().run()
```

***

**Next: [Remote rendering with xpra](xpra.md).**

[Return to the README](../../../README.md)

***

Example controllers:

- [minimal_remote.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/remote/minimal_remote.py) A minimal example of how to use the launch binaries daemon to start and connect to a build on a remote node. Note: the remote must be running binary_manager.py.

Python API:

- [`RemoteBuildLauncher`](../../python/remote_build_launcher.md)
