# Floorplan

`from tdw.add_ons.floorplan import Floorplan`

Initialize a scene populated by objects in pre-scripted layouts.

There are four scenes (1, 2, 4, 5), each with three visual variants (a, b, c). Each scene has three different object layouts (0, 1, 2).

```python
from tdw.controller import Controller
from tdw.add_ons.floorplan import Floorplan

c = Controller()
f = Floorplan()
f.init_scene(scene="1a", layout=0)
c.add_ons.append(f)
c.communicate([])
```

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Floorplan()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### init_scene

**`self.init_scene(scene, layout)`**

Set commands to initialize the scene. On the next frame, the scene will be initialized.

Valid scenes and layouts:

| `scene` | `layout` |
| --- | --- |
| 1a, 1b, or 1c | 0, 1, or 2 |
| 2a, 2b, or 2c | 0, 1, or 2 |
| 4a, 4b, or 4c | 0, 1, or 2 |
| 5a, 5b, or 5c | 0, 1, or 2 |

Where `1a` is the scene number (1) and visual variant (a).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| scene |  str |  | The name of the floorplan scene to load. Can be just the suffix of the scene to load (such as `"1a"`) or the full name of the scene (such as `"floorplan_1a"`). |
| layout |  int |  | The layout index. |