# KitchenTable

`from tdw.proc_gen.arrangements.kitchen_table import KitchenTable`

A kitchen table has chairs and table settings.

- The kitchen table model is chosen randomly; see `KitchenTable.MODEL_CATEGORIES["kitchen_table"]`.
  - The kitchen table's position is defined by center of the main region of a room; see `room` in the constructor.
  - If there are alcoves, the kitchen table will be positioned part way between the main room and the largest connecting alcove. The offset is random; see `KitchenTable.MIN_TABLE_ALCOVE_OFFSET_FACTOR` and `KitchenTable.MAX_TABLE_ALCOVE_OFFSET_FACTOR`.
  - The position of the kitchen table is perturbed randomly; see `KitchenTable.TABLE_POSITION_PERTURBATION`.
  - The rotation of the kitchen table is perturbed randomly; see `KITCHEN_TABLE_ROTATION`.
- There are *n* chairs around the table.
  - All chairs are the same model. The chair model is chosen randomly; see `KitchenTable.MODEL_CATEGORIES["kitchen_chair"]`.
  - If the surface area of the table is greater than 0.9 square meters, there are 4 chairs. Otherwise, there are two chairs and they are placed on the shorter sides of the table.
  - The `used_walls` parameter defines which walls are "used". It is assumed that there are objects along these walls. If the wall is less than 2 meters away from the table, a chair _won't_ be added on that side of the table.
  - The position of the chair is offset randomly: `half_extent + random.uniform(-0.1, -0.05)`
  - The chairs face the center of the table and then their rotations are perturbed randomly; see `KitchenTable.CHAIR_ROTATION`.
- For each chair, there is a [`TableSetting`](table_setting.md).
  - The table setting's position is set at the edge of the table and then moved inward by a random factor; see `KitchenTable.MIN_PLATE_OFFSET_FACTOR` and `KitchenTable.MAX_PLATE_OFFSET_FACTOR`.
  - The table setting's position is randomly perturbed; see `KitchenTable.PLATE_POSITION_PERTURBATION`.
- Sometimes, if the table is big enough, there is a centerpiece; see `KitchenTable.CENTERPIECE_PROBABILITY` and `KitchenTable.MIN_AREA_FOR_CENTERPIECE`.
  - The centerpiece is a random model from a random category; see `KitchenTable.CENTERPIECE_CATEGORIES`.
  - The centerpiece is in the center of the table and then its position is perturbed randomly; see `KitchenTable.CENTERPIECE_POSITION_PERTURBATION`
  - The rotation of the centerpiece is random (0 to 360 degrees).

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
| `CENTERPIECE_CATEGORIES` | List[str] | The possible centerpiece categories. | `["jug", "vase", "bowl"]` |
| `CENTERPIECE_POSITION_PERTURBATION` | float | Randomly perturb the (x, z) coordinates of the centerpiece by up to +/- this distance. | `0.1` |
| `CENTERPIECE_PROBABILITY` | float | The probability (0 to 1) of adding a adding a centerpiece to a table. | `0.75` |
| `CHAIR_ROTATION` | float | The chairs will be rotated randomly up to +/- this many degrees with respect to their initial rotation (facing the table). | `10` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `MAX_CHAIR_OFFSET` | float | The minimum random offset of a chair from the edge of the table. | `-0.01` |
| `MAX_PLATE_OFFSET_FACTOR` | float | The maximum offset of the plate from the edge of the table as a fraction of the table surface's extent. | `0.7` |
| `MAX_TABLE_ALCOVE_OFFSET_FACTOR` | float | If there is an alcove in the room, the table will be between the center of the main region and the center of the alcove at a random distance factor (0 to 1, with 0 being the center of the main region). | `0.65` |
| `MIN_AREA_FOR_CENTERPIECE` | float | The table surface area must be greater than this for there to potentially be a centerpiece. | `1.1` |
| `MIN_CHAIR_DISTANCE_FROM_USED_WALL` | float | The minimum distace from a "used wall" at which a chair can be placed. | `2` |
| `MIN_CHAIR_OFFSET` | float | The minimum random offset of a chair from the edge of the table. | `-0.02` |
| `MIN_PLATE_OFFSET_FACTOR` | float | The minimum offset of the plate from the edge of the table as a fraction of the table surface's extent. | `0.65` |
| `MIN_TABLE_ALCOVE_OFFSET_FACTOR` | float | If there is an alcove in the room, the table will be between the center of the main region and the center of the alcove at a random distance factor (0 to 1, with 0 being the center of the main region). | `0.35` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |
| `PLATE_POSITION_PERTURBATION` | float | Randomly perturb the (x, z) coordinates of each plate by up to +/- this distance. | `0.03` |
| `TABLE_POSITION_PERTURBATION` | float | Randomly perturb the (x, z) coordinates of the table by up to +/- this distance. | `0.1` |
| `TABLE_ROTATION` | float | The table will be rotated randomly up to +/- this many degrees. | `2` |

***

## Functions

#### \_\_init\_\_

**`KitchenTable(room, used_walls)`**

**`KitchenTable(room, used_walls, model=None, rng=None, offset_distance=0.1)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| room |  Room |  | The [`Room`] that the table is in. |
| used_walls |  int |  | Bitwise sum of walls with objects. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a random model in the category is selected. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created. |
| offset_distance |  float  | 0.1 | Offset the position from the used walls by this distance. |

#### get_categories_and_wcategories

**`Arrangement.get_categories_and_wcategories()`**

_(Static)_

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.