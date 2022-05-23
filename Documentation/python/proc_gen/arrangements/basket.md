# Basket

`from tdw.proc_gen.arrangements.basket import Basket`

A basket with random objects.

- The basket model is chosen random; see `Basket.MODEL_CATEGORIES["basket"]`.
- There are a random number of objects in the basket; see `BASKET.MIN_NUM_OBJECTS` and `BASKET.MAX_NUM_OBJECTS`.
  - The objects are chosen randomly; see `Basket.INSIDE_OF["basket"]`.
  - The rotations of the objects are random.
  - The starting positions of the objects are random, but they are placed at (x, z) coordinates within the basket and at a y coordinate _above_ the basket. Each y coordinate is higher than the other to prevent interpenetration; see `Basket.DELTA_Y`.
- The basket is placed next to a wall at a random distance offset: `extent * random.uniform(Basket.MIN_DEPTH_OFFSET, Basket.MAX_DEPTH_OFFSET)`.
- The basket is rotated randomly; see `Basket.ROTATION`.

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
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `DELTA_Y` | float | Each subsequent object in the basket is placed this many meters above the previous. | `0.25` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `LENGTH_OFFSET` | float | Add this length to the basket's length when creating lateral arrangements. | `0.1` |
| `MAX_DEPTH_OFFSET` | float | The maximum offset from the wall. | `1.25` |
| `MAX_NUM_OBJECTS` | int | The maximum number of objects in a basket. | `2` |
| `MIN_DEPTH_OFFSET` | float | The minimum offset from the wall. | `1.15` |
| `MIN_NUM_OBJECTS` | int | The minimum number of objects in a basket. | `2` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |
| `ROTATION` | float | Baskets are randomly rotated up to +/- this many degrees. | `10` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`Basket(wall, corner, distance, region)`**

**`Basket(wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

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