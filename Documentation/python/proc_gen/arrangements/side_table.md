# SideTable

`from tdw.proc_gen.arrangements.side_table import SideTable`

A small side table with objects on it.

- The side table model is chosen randomly; see `SideTable.MODEL_CATEGORIES["side_table"]`.
- The side table is placed next to a wall.
  - The side table's position is automatically adjusted to set it flush to the wall.
  - The side table is automatically rotated so that it faces away from the wall.
  - The side table's (x, z) positional coordinates are offset by a factor; see `SideTable.DEPTH_FACTOR` and `SIDE_TABLE.LENGTH_FACTOR`.
- The side table will have a rectangular arrangement of objects on top of it.
  - The objects are chosen randomly; see `SideTable.ON_TOP_OF["side_table"]`.
  - The objects are positioned in a rectangular grid on the table with random rotations and positional perturbations; see: `SideTable.CELL_SIZE`, `SideTable.CELL_DENSITY`, `SideTable.WIDTH_SCALE`, and `SideTable.DEPTH_SCALE`.
- The side table is non-kinematic.

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
| `CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the side table rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.4` |
| `CELL_SIZE` | float | The size of each cell in the side table rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.05` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `DEPTH_FACTOR` | float | Offset the distance from the wall by this factor. | `1.05` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `LENGTH_FACTOR` | float | Offset the distance along the wall by this factor. | `1.25` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`SideTable(wall, corner, distance, region)`**

**`SideTable(wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

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