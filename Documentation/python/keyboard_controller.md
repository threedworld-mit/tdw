# `keyboard_controller.py`

## `KeyboardController(Controller)`

`from tdw.keyboard_controller import KeyboardController`

Listen for keyboard input to send commands.

Usage:

```python
from tdw.keyboard_controller import KeyboardController

def stop():
done = True

done = False
c = KeyboardController()
c.listen(key="esc", commands={"$type": "terminate"}, function=stop)
while not done:
c.step() # Receive data until the Esc key is pressed.
```

***

#### `stop()`

def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True, display: int = None,
framerate: int = 30):

***

#### `__init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True, display`

Create the network socket and bind the socket to the port.

| Parameter | Description |
| --- | --- |
| port | The port number. |
| check_version | If true, the controller will check the version of the build and print the result. |
| launch_build | If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor. |
| display | If launch_build == True, launch the build using this display number (Linux-only). |
| framerate | The build's target frames per second. |

***

#### `step(self, commands: Union[dict, List[dict]] = None) -> List[bytes]`

Step the simulation and listen for keyboard input.
Call this function after registering your listeners with `listen()`.

| Parameter | Description |
| --- | --- |
| commands | Any additional commands to send to the build on this frame. |

_Returns:_ The response from the build.

***

#### `listen(self, key: str, commands: Union[dict, List[dict]] = None, function=None) -> None`

Listen for when a key is pressed and send commands.

| Parameter | Description |
| --- | --- |
| key | The keyboard key. |
| commands | Commands to be sent when the key is pressed. |
| function | A function to be invoked when the key is pressed. |

***

