# AddOn

`from tdw.add_ons.add_on import AddOn`

Controller add-ons can be "attached" to any controller to add functionality into the `communicate()` function.

See the README for a complete list of add-ons.

To attach an add-on, append it to the `add_ons` list.
Every time `communicate()` is called, the add-on will evaluate the response from the build. The add-on can send additional commands to the build on the next frame or do something within its own state (such as update an ongoing log):

```python
from tdw.controller import Controller
from tdw.add_ons.debug import Debug

c = Controller(launch_build=False)
d = Debug(record=True, path="log.json")
c.add_ons.append(d)
# The debug add-on will log this command.
c.communicate({"$type": "do_nothing"})
# The debug add-on will log this command and generate a log.json file.
c.communicate({"$type": "terminate"})
```

## Add-ons

- [Benchmark](benchmark.md)
- [CinematicCamera](cinematic_camera.md)
- [Debug](debug.md)
- [ImageCapture](image_capture.md)
- [Keyboard](keyboard.md)
- [ThirdPersonCamera](third_person_camera.md)

## Example controllers

- `tdw/Python/example_controllers/add_ons.py` How to add multiple add-ons to the controller.
- `tdw/Python/example_controller/debug.py` Example implementation of a `Debug` add-on.
- `tdw/Python/example_controllers/keyboard_controls.py` Example implementation of a `Keyboard` add-on.
- `tdw/Python/example_controllers/cinematic_camera_controls.py` Example implementation of a `CinematicCamera` add-on.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`AddOn()`**

(no parameters)

#### get_initialization_commands

_(Abstract)_

**`self.get_initialization_commands()`**

_Returns:_  A list of commands that will initialize this module.

#### on_communicate

_(Abstract)_

**`self.on_communicate(resp)`**

This is called after commands are sent to the build and a response is received.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### previous_commands

**`self.previous_commands(commands)`**

Do something with the commands that were just sent to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that were just sent to the build. |

