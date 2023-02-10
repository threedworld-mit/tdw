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

To generate an occupancy map, you can use the [`OccupancyMap`](../../python/add_ons/occupancy_map.md) add-on, call `generate()`, and then call `controller.communicate(commands)`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

c = Controller()
occupancy_map = OccupancyMap()
c.add_ons.append(occupancy_map)
occupancy_map.generate(cell_size=0.5)
c.communicate([TDWUtils.create_empty_room(6, 6),
               c.get_add_object(model_name="trunck",
                                object_id=c.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 1.5})])
print(occupancy_map.occupancy_map)
c.communicate({"$type": "terminate"})
```

Output:

```
[[1 1 1 1 1 1 1 1 1 1 1]
 [1 0 0 0 0 0 0 0 0 0 1]
 [1 0 0 0 0 0 0 0 0 0 1]
 [1 0 0 0 0 0 0 0 0 0 1]
 [1 0 0 0 0 0 0 0 0 0 1]
 [1 0 0 0 0 0 0 0 0 0 1]
 [1 0 0 0 0 0 0 0 0 0 1]
 [1 0 0 0 1 1 1 0 0 0 1]
 [1 0 0 0 1 1 1 0 0 0 1]
 [1 0 0 0 1 1 1 0 0 0 1]
 [1 1 1 1 1 1 1 1 1 1 1]]
```

## Occupancy map statuses

| Value | Meaning                                                      |
| ----- | ------------------------------------------------------------ |
| 0     | The cell is unoccupied.                                      |
| 1     | The cell is occupied by at least one object or occupied by an environment object (such as a wall). |
| 2    | The cell is out of bounds (there is no floor).               |
| 3    | The cell is free, but it's in an isolated island. |

## Occupancy map positions

`occupancy_map.positions` is a 3D array where the first two axes correspond to `occupancy_map.occupancy_map`.

For example, `occupancy_map.positions[0][1]` might return `[-2.  -2.5]` and its occupancy status is `occupancy_map.occupancy_map[0][1]`, which in the above example returns `1` (occupied).

## Cell Size

Set the `cell_size` parameter in `generate()` to adjust the size of each cell:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

c = Controller()
occupancy_map = OccupancyMap()
c.add_ons.append(occupancy_map)
occupancy_map.generate(cell_size=1)
c.communicate([TDWUtils.create_empty_room(6, 6),
               c.get_add_object(model_name="trunck",
                                object_id=c.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 1.5})])
print(occupancy_map.occupancy_map)
c.communicate({"$type": "terminate"})
```

Output (note that this map is smaller than the previous example, despite having the scene being exactly the same):

```
[[1 1 1 1 1 1]
 [1 0 0 0 0 1]
 [1 0 0 0 0 1]
 [1 0 0 0 0 1]
 [1 0 1 1 0 1]
 [1 1 1 1 1 1]]
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
occupancy_map = OccupancyMap()
c.add_ons.append(occupancy_map)
object_id = Controller.get_unique_id()
occupancy_map.generate(cell_size=1, ignore_objects=[object_id])
c.communicate([TDWUtils.create_empty_room(6, 6),
               c.get_add_object(model_name="trunck",
                                object_id=object_id,
                                position={"x": 0, "y": 0, "z": 1.5})])
print(occupancy_map.occupancy_map)
c.communicate({"$type": "terminate"})
```

Output:

```
[[1 1 1 1 1 1]
 [1 0 0 0 0 1]
 [1 0 0 0 0 1]
 [1 0 0 0 0 1]
 [1 0 0 0 0 1]
 [1 1 1 1 1 1]]
```

## Regenerate every communicate() call

**Occupancy maps are static.** If an object in the scene moves, `occupancy_map.occupancy_map` won't update.

You can optionally regenerate the occupancy map on every communicate() call by setting `generate(once=False)`. In general, it is relatively expensive to generate occupancy maps. If you need to continuously update your occupancy map, setting `once=False` is faster than calling `generate()` every communicate() call because the build will be able to use cached data.

## Reset

You don't need to reset an `OccupancyMap` add-on. Simply call `generate()` followed by `controller.communicate(commands)` to create a new occupancy map.

***

**This is the last document in the "Navigation" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [occupancy_map.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/navigation/occupancy_map.py) Minimal example of occupancy map generation.

Python API:

- [`OccupancyMap`](../../python/add_ons/occupancy_map.md)