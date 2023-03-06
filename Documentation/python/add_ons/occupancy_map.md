# OccupancyMap

`from tdw.add_ons.occupancy_map import OccupancyMap`

An occupancy map is a numpy array that divides a TDW into a grid. Each cell is free (no objects), non-free (has objects), or is outside of the environment.

Each element in the occupancy map can be one of three values:

| Value | Meaning                                                      |
| ----- | ------------------------------------------------------------ |
| 0     | The cell is unoccupied.                                      |
| 1     | The cell is occupied by at least one object or occupied by an environment object (such as a wall). |
| 2    | The cell is out of bounds (there is no floor).               |
| 3    | The cell is free, but it's in an isolated island. |

***

## Fields

- `occupancy_map` A 2D numpy array of the occupancy map. Each value is an occupancy value. For example, if `self.occupancy_map[0][1] == 0`, then that position is free. This array is `None` until you call `generate()` followed by `controller.communicate(commands)`.

- `positions` A 3D numpy array of the occupancy map worldspace positions where the shape is `(width, length, 2)` where the last axis is (x, z) worldspace coordinates. The lengths of the first two axes of this array are the same as in `self.occupancy_map`, meaning that `self.occupancy_map[0][1]` is the occupancy status of `self.positions[0][1]`. This array is `None` until you call `generate()` followed by `controller.communicate(commands)`.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`OccupancyMap()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### generate

**`self.generate()`**

**`self.generate(ignore_objects=None, cell_size=0.5, raycast_y=2.7, once=True)`**

Generate an occupancy map. Call this, followed by `controller.communicate(commands)` to generate the map.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| ignore_objects |  List[int] | None | If not None, ignore these objects when determining if a cell is free or non-free. |
| cell_size |  float  | 0.5 | The cell size in meters. |
| raycast_y |  float  | 2.7 | Raycast for objects from this height in meters. |
| once |  bool  | True | If True, generate an occupancy map only on this `communicate(commands)` call. If False, regenerate the occupancy map on every `communicate(commands)` call using the parameters provided here until the scene is unloaded or this function is called again. |

#### show

**`self.show()`**

Visualize the occupancy map by adding blue squares into the scene to mark free spaces.

These blue squares don't interact with the physics engine.

#### hide

**`self.hide()`**

Remove all positions markers (the blue squares created by `self.show()`).