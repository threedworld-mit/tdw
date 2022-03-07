# Void

`from proc_gen.arrangements.void import Void`

An empty space along a wall.

***

## Functions

#### \_\_init\_\_

**`Void(corner, wall, distance, region)`**

**`Void(corner, wall, distance, region, length=ArrangementAlongWall.DEFAULT_CELL_SIZE)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| corner |  OrdinalDirection |  | The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction. |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
| length |  float  | ArrangementAlongWall.DEFAULT_CELL_SIZE | The length of the void. |

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

#### get_commands

**`self.get_commands()`**

#### get_length

**`self.get_length()`**

_Returns:_  The lateral extent of the object.

