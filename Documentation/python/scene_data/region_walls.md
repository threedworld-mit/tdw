# RegionWalls

`from scene_data.region_walls import RegionWalls`

The walls bounding a [`RegionBounds`](region_bounds.md).

Walls may be non-continuous (such as walls with doorways) or have windows.

***

## Fields

- `region` The index of the region in [`scene_bounds.rooms`](scene_bounds.md).

- `non_continuous_walls` The summed values of the non-continuous walls. For example, if this is `3`, then the north and east walls are non-continuous.

- `walls_with_windows` The summed values of the walls that have windows. For example, if this is `3`, then the north and east walls have windows.

***

## Functions

#### \_\_init\_\_

**`RegionWalls(region, non_continuous_walls, walls_with_windows)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| region |  int |  | The index of the region in [`scene_bounds.rooms`](scene_bounds.md). |
| non_continuous_walls |  Union[int, List[CardinalDirection] |  | Non-continuous walls. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`. |
| walls_with_windows |  Union[int, List[CardinalDirection] |  | Walls that have windows. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`. |

