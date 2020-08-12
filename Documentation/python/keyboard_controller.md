# `keyboard_controller.py`

## `KeyboardController(Controller)`

`from tdw.keyboard_controller import KeyboardController`

Listen for keyboard input to send commands.

Usage:

```python
from tdw.keyboard_controller import KeyboardController
from tdw.tdw_utils import TDWUtils

def stop():
done = True

done = False
c = KeyboardController()
c.start()

# Quit.
c.listen(key="esc", commands=None, function=stop)

# Equivalent to c.start()
c.listen(key="r", commands={"$type": "load_scene", "scene_name": "ProcGenScene"}, function=None)

while not done:
# Receive data. Load the scene when r is pressed. Quit when Esc is pressed.
c.communicate([])
# Stop the build.
c.communicate({"$type": "terminate"})
```

***

#### `stop()`

def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True,
framerate: int = 30):

***

#### `__init__(self, port: int = 1071, check_version: bool = True, launch_build`

Create the network socket and bind the socket to the port.

| Parameter | Description |
| --- | --- |
| port | The port number. |
| check_version | If true, the controller will check the version of the build and print the result. |
| launch_build | If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor. |
| framerate | The build's target frames per second. |

***

#### `communicate(self, commands: Union[dict, List[dict]]) -> list`

Listen for when a key is pressed and send commands.

| Parameter | Description |
| --- | --- |
| key | The keyboard key. |
| commands | Commands to be sent when the key is pressed. |
| function | A function to be invoked when the key is pressed. |

***

#### `listen(self, key: str, commands: Union[dict, List[dict]] = None, function=None) -> None`

Listen for when a key is pressed and send commands.

| Parameter | Description |
| --- | --- |
| key | The keyboard key. |
| commands | Commands to be sent when the key is pressed. |
| function | A function to be invoked when the key is pressed. |

***

