# `keyboard_controller.py`

## `KeyboardController(Controller)`

`from tdw.keyboard_controller import KeyboardController`

Listen for keyboard input to send commands.

Keyboard input is registered _from the build, not the controller._ For this controller to work, you must:

- Run the build on the same machine as the keyboard.
- Have the build window as the focused window (i.e. not minimized).

Usage:

```python
from tdw.keyboard_controller import KeyboardController
from tdw.tdw_utils import TDWUtils

def stop():
    done = True
    c.communicate({"$type": "terminate"})

done = False
c = KeyboardController()
c.start()

# Quit.
c.listen(key="esc", function=stop)

# Equivalent to c.start()
c.listen(key="r", commands={"$type": "load_scene", "scene_name": "ProcGenScene"})

while not done:
    # Receive data. Load the scene when r is pressed. Quit when Esc is pressed.
    c.communicate([])
```

***

#### `stop()`

def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):

***

#### `__init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True)`

Create the network socket and bind the socket to the port.

| Parameter | Description |
| --- | --- |
| port | The port number. |
| check_version | If true, the controller will check the version of the build and print the result. |
| launch_build | If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor. |

***

#### `communicate(self, commands: Union[dict, List[dict]]) -> List[bytes]`

Listen for when a key is pressed and send commands.

| Parameter | Description |
| --- | --- |
| key | The keyboard key. |
| commands | Commands to be sent when the key is pressed. |
| function | Function to invoke when the key is pressed. |
| events | Listen to these keyboard events for this `key`. Options: `"press"`, `"hold"`, `"release"`. If None, this defaults to `["press"]`. |

***

#### `listen(self, key: str, commands: Union[dict, List[dict]] = None, function=None, events: List[str] = None) -> None`

Listen for when a key is pressed and send commands.

| Parameter | Description |
| --- | --- |
| key | The keyboard key. |
| commands | Commands to be sent when the key is pressed. |
| function | Function to invoke when the key is pressed. |
| events | Listen to these keyboard events for this `key`. Options: `"press"`, `"hold"`, `"release"`. If None, this defaults to `["press"]`. |

***

