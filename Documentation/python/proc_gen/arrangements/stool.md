# Stool

`from proc_gen.arrangements.stool import Stool`

A stool.

- The stool model is chosen randomly; see `Stool.MODEL_CATEGORIES["stool"]`.
- The stool is placed next to a wall.
  - The stool's position is automatically adjusted to set it flush to the way.
  - The stool is automatically rotated so that it faces away from the wall.
- The stool's rotation is random.
- The stool is non-kinematic.

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



