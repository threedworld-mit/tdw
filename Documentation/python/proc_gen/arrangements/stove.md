# Stove

`from proc_gen.arrangements.stove import Stove`

A stove with oven doors.

- For now, the stove model is always the same (`gas_stove_composite`).
- The stove is placed next to a wall.
  - The stove's position is automatically adjusted to set it flush to the way.
  - The stove is automatically rotated so that it faces away from the wall.
- The stove always has a rectangular arrangement of objects on top of it; see `Stove.ON_TOP_OF["stove"]`.
- The stove has two doors that can open and two interior spaces.
- 70% of the time, each of the interior spaces may have an object; see `Stove.ENCLOSED_BY["stove"]`.
- The root object of the stove is non-kinematic and its door sub-objects are kinematic.

***

## Functions

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

#### get_length

**`self.get_length()`**

#### \_\_init\_\_

**`ArrangementAlongWall(wall, corner, distance, region)`**

**`ArrangementAlongWall(wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected. If no model fits, the arrangement will not be added to the scene. |
| wall_length |  float  | None | The total length of the lateral arrangement. If None, defaults to the length of the wall. |
| rng |  np.random.RandomState  | None | The random number generator. If None, a new random number generator is created. |



#### get_length

**`self.get_length()`**

_Returns:_  The lateral extent of the object.



