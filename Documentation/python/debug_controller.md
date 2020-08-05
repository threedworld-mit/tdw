# `debug_controller.py`

## `DebugController(Controller)`

`from tdw.debug_controller import DebugController`

DebugController is a subclass of Controller that records every list of commands sent to the build.
You can "play back" these commands, i.e. re-send them to the build.
You can also save all of the recorded commands to a local file.

```python
from tdw.debug_controller import DebugController
c = DebugController()
c.start()
```

***

#### `__init__(self, port: int = 1071, launch_build: bool = True, display: int = None)`

Create the network socket and bind the socket to the port.

| Parameter | Description |
| --- | --- |
| port | The port number. |
| launch_build | If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor. |
| display | If launch_build == True, launch the build using this display number (Linux-only). |

***

#### `communicate(self, commands: Union[dict, List[dict]]) -> list`

Send commands and receive output data in response. Record the commands immediately prior to sending them.

| Parameter | Description |
| --- | --- |
| commands | A list of JSON commands. |

_Returns:_ The output data from the build.

***

#### `playback(self, print_commands: bool = False) -> None`

Send the record of commands to the build.

| Parameter | Description |
| --- | --- |
| print_commands | If true, print each list of commands before it is sent. |

***

#### `save_record(self, filepath: str) -> None`

Write the record of commands sent to the local disk.

| Parameter | Description |
| --- | --- |
| filepath | The absolute path to which the record will be written. |

***

#### `load_record(self, filepath: str) -> None`

If this controller was set to debug, load a record of commands from the local disk.

| Parameter | Description |
| --- | --- |
| filepath | The absolute path from which the record will be loaded. |

***

#### `get_benchmark(self, num_frames: int) -> float`

Calculate a frames per second (FPS) benchmark.
Send an empty list of commands for a given number of frames.

| Parameter | Description |
| --- | --- |
| num_frames | The number of frames for which the benchmark test will run. |

_Returns:_ The average FPS.

***

#### `clear_playback_record(self) -> None`

Clear all recorded data from memory.
Useful if you want the playback file to exclude previous commands (i.e. in a very long simulation).

***

