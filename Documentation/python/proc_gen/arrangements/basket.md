# Basket

`from proc_gen.arrangements.basket import Basket`

A basket with random objects.

- The basket model is chosen random; see `Basket.MODEL_CATEGORIES["basket"]`.
- There are a random number of objects in the basket; see `BASKET.MIN_NUM_OBJECTS` and `BASKET.MAX_NUM_OBJECTS`.
  - The objects are chosen randomly; see `Basket.INSIDE_OF["basket"]`.
  - The rotations of the objects are random.
  - The starting positions of the objects are random, but they are placed at (x, z) coordinates within the basket and at a y coordinate _above_ the basket. Each y coordinate is higher than the other to prevent interpenetration; see `Basket.DELTA_Y`.
- The basket is placed next to a wall at a random distance offset: `extent * random.uniform(Basket.MIN_OFFSET, Basket.MAX_OFFSET)`.
- The basket is rotated randomly; see `Basket.ROTATION`.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `MIN_NUM_OBJECTS` | int | The minimum number of objects in a basket. |
| `MAX_NUM_OBJECTS` | int | The maximum number of objects in a basket. |
| `MIN_OFFSET` | float | The minimum offset from the wall. |
| `MAX_OFFSET` | float | The maximum offset from the wall. |
| `ROTATION` | float | Baskets are randomly rotated up to +/- this many degrees. |
| `DELTA_Y` | float | Each subsequent object in the basket is placed this many meters above the previous. |

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



