# OccupancyMap

`from tdw.add_ons.occupancy_map import OccupancyMap`

An occupancy map is a numpy array that divides a TDW into a grid. Each cell is free (no objects), non-free (has objects), or is outside of the environment.

Each element in the occupancy map can be one of three values:

| Value | Meaning                                                      |
| ----- | ------------------------------------------------------------ |
| -1    | The cell is out of bounds (there is no floor).               |
| 1     | The cell is occupied by at least one object, occupied by an environment object (such as a wall), or otherwise not navigable (blocked by other objects). |
| 0     | The cell is unoccupied.                                      |

***

## Fields

- `occupancy_map` A 2-dimensional numpy array of the occupancy map. Each row corresponds to a worldspace x value and each column corresponds to a worldspace z value (see `get_occupancy_position(idx, idy)` below).

- `scene_bounds` The [bounds of the scene](../scene_data/scene_bounds.md).

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`OccupancyMap()`**

**`OccupancyMap(cell_size=0.5)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| cell_size |  float  | 0.5 | The diameter of each cell in meters. |

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

#### generate

**`self.generate()`**

**`self.generate(ignore_objects=None)`**

Generate an occupancy map.
This function should only be called at least one controller.communicate() call after adding this add-on.
The OccupancyMap then requires one more controller.communicate() call to create the occupancy map.
(See the example at the top of this document.)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| ignore_objects |  List[int] | None | If not None, ignore these objects when determining if a cell is free or non-free. |

#### get_occupancy_position

**`self.get_occupancy_position(i, j)`**

Convert occupancy map indices to worldspace coordinates.
This function can only be sent after first calling `self.generate()` and waiting at least one `controller.communicate()` call.:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

c = Controller(launch_build=False)
o = OccupancyMap(cell_size=0.5)
c.add_ons.append(o)
c.communicate(TDWUtils.create_empty_room(12, 12))
o.generate()
c.communicate([])
print(o.get_occupancy_position(4, 5))  # (-3.5, -3.0)
c.communicate({"$type": "terminate"})
```


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| i |  int |  | The column index of self.occupancy_map |
| j |  int |  | The row index of self.occupancy_map. |

_Returns:_  A tuple: `self.occupancy_map[i][j]` converted into `(x, z)` worldspace coordinates.

#### show

**`self.show()`**

Visualize the occupancy map by adding blue squares into the scene to mark free spaces.
These blue squares don't interact with the physics engine.

#### hide

**`self.hide()`**

Remove all positions markers (the blue squares created by `self.show()`).

#### reset

**`self.reset()`**

Reset the occupancy map. Call this when resetting a scene.