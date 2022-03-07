# ArrangementAlongWall

`from proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall`

Abstract class procedurally-generated spatial arrangements of objects that are positioned alongside a wall as part of a lateral arrangement.

Rather than supplying a position and rotation for the object, the arrangement is placed at a `distance` from a `corner` along a `wall` in a `region` and then rotated so that it faces away from the wall.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. |

***

## Functions

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

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

#### get_length

**`self.get_length()`**

_Returns:_  The lateral extent of the object.

