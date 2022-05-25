# InteriorRegion

`from scene_data.interior_region import InteriorRegion`

An interior region has bounds data and cached data regarding continuous walls and walls with windows.

***

## Fields

- `non_continuous_walls` The summed values of the non-continuous walls. For example, if this is `3`, then the north and east walls are non-continuous.

- `walls_with_windows` The summed values of the walls that have windows. For example, if this is `3`, then the north and east walls have windows.

***

## Functions

#### \_\_init\_\_

**`InteriorRegion(region_id, center, bounds, non_continuous_walls, walls_with_windows)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| region_id |  int |  | The ID of the region. |
| center |  Tuple[float, float, float] |  | The center of the region. |
| bounds |  Tuple[float, float, float] |  | The bounds of the region. |
| non_continuous_walls |  Union[int, List[CardinalDirection] |  | Non-continuous walls. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`. |
| walls_with_windows |  Union[int, List[CardinalDirection] |  | Walls that have windows. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`. |

