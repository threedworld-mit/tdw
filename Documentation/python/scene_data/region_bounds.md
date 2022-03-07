# RegionBounds

`from scene_data.region_bounds import RegionBounds`

Data for the bounds of a region in a scene. In an interior scene, this usually corresponds to a room.

***

## Fields

- `region_id` The ID of the region.

- `center` The center of the region.

- `bounds` The bounds of the region.

- `x_min` Minimum x positional coordinate of the room.

- `y_min` Minimum y positional coordinate of the room.

- `z_min` Minimum z positional coordinate of the room.

- `x_max` Maximum x positional coordinate of the room.

- `y_max` Maximum y positional coordinate of the room.

- `z_max` Maximum z positional coordinate of the room.

***

## Functions

#### \_\_init\_\_

**`RegionBounds(region_id, center, bounds)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| region_id |  int |  | The ID of the region. |
| center |  Tuple[float, float, float] |  | The center of the region. |
| bounds |  Tuple[float, float, float] |  | The bounds of the region. |

#### is_inside

**`self.is_inside(x, z)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| x |  float |  | The x coordinate. |
| z |  float |  | The z coordinate. |

_Returns:_  True if position (x, z) is in the scene.

#### get_length

**`self.get_length(side)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| side |  CardinalDirection |  | A side of the region as a [`CardinalDirection`](../cardinal_direction.md). |

_Returns:_  The length of the side.

#### get_longer_sides

**`self.get_longer_sides()`**

_Returns:_  Tuple: A list of the longer sides as [`CardinalDirection` values](../cardinal_direction.md), the length of the sides.

#### get_shorter_sides

**`self.get_shorter_sides()`**

_Returns:_  Tuple: A list of the shorter sides as [`CardinalDirection` values](../cardinal_direction.md), the length of the sides.

#### get_from_scene_regions

**`self.get_from_scene_regions(scene_regions, i)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| scene_regions |  SceneRegions |  | The scene regions output data. |
| i |  int |  | The index of this scene in env.get_num() |

_Returns:_  `RegionBounds`.

