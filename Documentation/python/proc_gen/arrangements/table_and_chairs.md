# TableAndChairs

`from tdw.proc_gen.arrangements.table_and_chairs import TableAndChairs`

Abstract base class for a table with chairs around it.

***

## Fields

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `AREA_FOUR_CHAIRS` | float | The minimum surface area required for four chairs; below this, there are only two chairs. | `0.9` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `MAX_CHAIR_OFFSET` | float | The minimum random offset of a chair from the edge of the table. | `-0.01` |
| `MIN_CHAIR_DISTANCE_FROM_USED_WALL` | float | The minimum distace from a "used wall" at which a chair can be placed. | `2` |
| `MIN_CHAIR_OFFSET` | float | The minimum random offset of a chair from the edge of the table. | `-0.02` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |

***

## Functions

#### \_\_init\_\_

**`TableAndChairs(used_walls, region, model, position)`**

**`TableAndChairs(used_walls, region, model, position, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| used_walls |  int |  | Bitwise sum of walls with objects. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the table is in. |
| model |  Union[str, ModelRecord] |  | Either the name of the model (in which case the model must be in `models_core.json` or a `ModelRecord`. |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created. |

#### get_categories_and_wcategories

**`Arrangement.get_categories_and_wcategories()`**

_(Static)_

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.