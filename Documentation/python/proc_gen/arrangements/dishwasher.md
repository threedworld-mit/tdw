# Dishwasher

`from tdw.proc_gen.arrangements.dishwasher import Dishwasher`

A dishwasher with a kitchen counter top with objects on it.

- The dishwasher model is chosen randomly; see `Dishwasher.MODEL_CATEGORIES["dishwasher"]`.
- The dishwasher is placed next to a wall.
  - The dishwasher's position is automatically adjusted to set it flush to the wall.
  - The dishwasher is automatically rotated so that it faces away from the wall.
  - The dishwasher's position along the wall is slightly offset; see `Dishwasher.LENGTH_OFFSET`.
- The dishwasher has a floating kitchen counter top above it.
- The floating kitchen counter top always has a rectangular arrangement of objects on top of it.
  - The objects are chosen randomly; see `Dishwasher.ON_TOP_OF["kitchen_counter"]`.
  - The objects are positioned in a rectangular grid on the dishwasher with random rotations and positional perturbations; see `Dishwasher.CELL_SIZE`, Dishwasher.CELL_DENSITY`, `Dishwasher.WIDTH_SCALE`, and `Dishwasher.DEPTH_SCALE`.
- All dishwashers have a door that can be opened.
- The root object of the dishwasher is kinematic and the door sub-object is non-kinematic.

***

## Fields

- `send_commands` If True, send commands when `self.get_commands()` is called. If False, `self.get_commands()` will return an empty list.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the counter top rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.4` |
| `CELL_SIZE` | float | The size of each cell in the counter top rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.05` |
| `COUNTER_TOPS` | Dict[str, str] | A dictionary of counter top models per dishwasher model. | `loads(Path(resource_filename(__name__, "data/dishwasher_counter_tops.json")).read_text())` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `LENGTH_OFFSET` | float | Offset the position and length of the dishwasher by this distance. | `0.025` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`Dishwasher(wall, corner, distance, region)`**

**`Dishwasher(wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`OrdinalDirection`](../../ordinal_direction.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected. If no model fits, the arrangement will not be added to the scene. |
| wall_length |  float  | None | The total length of the lateral arrangement. If None, defaults to the length of the wall. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created. |

#### get_categories_and_wcategories

**`Arrangement.get_categories_and_wcategories()`**

_(Static)_

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

#### get_length

**`self.get_length()`**

_Returns:_  The lateral extent of the object.