##### Navigation

# Occupancy maps

An **occupancy map** is a two-dimensional numpy array representation of a scene in TDW. Each element in the array is an area of a given size and can have one of three values:

| Value | Meaning                                                      |
| ----- | ------------------------------------------------------------ |
| -1    | The cell is out of bounds (there is no floor).               |
| 1     | The cell is occupied by at least one object, occupied by an environment object (such as a wall), or otherwise not navigable (blocked by other objects). |
| 0     | The cell is unoccupied.                                      |

You can use an occupancy map for several purposes:

-  In [scene generation](../scene_setup/overview.md), occupancy maps can be used to find free areas to place objects.
- Occupancy maps can be used for pathfinding navigation.

## The `OccupancyMap` add-on

To generate an occupancy map, you can use the [`OccupancyMap`](../../python/add_ons/occupancy_map.md) add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

c = Controller()
occupancy_map = OccupancyMap(cell_size=0.5)
c.add_ons.append(occupancy_map)
c.communicate([TDWUtils.create_empty_room(6, 6),
               c.get_add_object(model_name="trunck",
                                object_id=c.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 1.5})])
occupancy_map.generate()
c.communicate([])
print(occupancy_map.occupancy_map)
c.communicate({"$type": "terminate"})
```

Output:

```
[[-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  1  1  1 -1]
 [-1  0  0  0  0  0  0  1  1  1 -1]
 [-1  0  0  0  0  0  0  1  1  1 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]]
```

Note that it takes two `communicate()` calls to create the occupancy map; the first gets the bounds of the scene and the second divides the bounds into cells and requests [`Raycast`](../semantic_states/raycast.md) and [`Overlap`](../semantic_states/overlap.md) data per cell.

`occupancy_map.generate()` prepares to send commands to the build but doesn't actually send commands to the build (only a controller can do that). You always need to send `occupancy_map.generate()` *then* `c.communicate(commands)`.

## Convert occupancy map coordinates to world space coordinates

To convert occupancy map coordinates to world space coordinates, call `occupancy_map.get_occupancy_position(i, j)`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

"""
Minimal example of generating an occupancy map.
"""

c = Controller()
occupancy_map = OccupancyMap(cell_size=0.5)
c.add_ons.append(occupancy_map)
c.communicate([TDWUtils.create_empty_room(6, 6)])
occupancy_map.generate()
c.communicate([])
print(occupancy_map.get_occupancy_position(0, 0))
c.communicate({"$type": "terminate"})
```

Output:

```
(-2.5, -2.5)
```

## Ignore objects

You might want the `OccupancyMap` to ignore certain objects. Examples:

- You don't want the cell agent is in to be marked as "occupied"
- You want to ignore small objects

Set the `ignore_objects` parameter of `occupancy_map.generate()` to ignore objects:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

c = Controller()
occupancy_map = OccupancyMap(cell_size=0.5)
c.add_ons.append(occupancy_map)
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(6, 6),
               c.get_add_object(model_name="trunck",
                                object_id=object_id,
                                position={"x": 0, "y": 0, "z": 1.5})])
occupancy_map.generate(ignore_objects=[object_id])
c.communicate([])
print(occupancy_map.occupancy_map)
c.communicate({"$type": "terminate"})
```

Output:

```
[[-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]]
```

## Scene reset

When [resetting a scene](../scene_setup_high_level/reset_scene.md), call `occupancy_map.reset()`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

c = Controller()
occupancy_map = OccupancyMap(cell_size=0.5)
c.add_ons.append(occupancy_map)
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(6, 6)])
occupancy_map.generate()
c.communicate([])
print(occupancy_map.occupancy_map)
occupancy_map.reset()
c.communicate([{"$type": "load_scene",
                "scene_name": "ProcGenScene"},
               TDWUtils.create_empty_room(8, 4)])
occupancy_map.generate()
c.communicate([])
print(occupancy_map.occupancy_map)
c.communicate({"$type": "terminate"})
```

Output:

```
[[-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1  0  0  0  0  0  0  0  0  0 -1]
 [-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]]
 
[[-1 -1 -1 -1 -1 -1 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1  0  0  0  0  0 -1]
 [-1 -1 -1 -1 -1 -1 -1]]
```

## Limitations

- Occupancy maps are static. If an object in the scene moves, `occupancy_map.occupancy_map` won't update until you call `occupancy_map.generate()` again.
- Generating an occupancy map can slow down the build. We recommend generating occupancy maps only as needed (not per-frame).

***

**This is the last document in the "Navigation" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [occupancy_map.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/navigation/occupancy_map.py) Minimal example of occupancy map generation.

Python API:

- [`OccupancyMap`](../../python/add_ons/occupancy_map.md)