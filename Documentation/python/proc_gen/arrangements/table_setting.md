# TableSetting

`from tdw.proc_gen.arrangements.table_setting import TableSetting`

A table setting includes a plate, fork, knife, spoon, and sometimes a cup.

- This is a subclass of [`Plate`](plate.md). The plate model is always the same; see `TableSetting.PLATE_MODEL_NAME`.
- The fork, knife, and spoon models are random; see `TableSetting.MODEL_CATEGORIES["fork"]`, `TableSetting.MODEL_CATEGORIES["knife"]`, and `TableSetting.MODEL_CATEGORIES["spoon"]`.
  - The rotations of the fork, knife, and spoon are perturbed randomly; see `TableSetting.CUTLERY_ROTATION_PERTURBATION`.
  - The positions of the fork, knife, and spoon are perturbed randomly; see `TableSetting.CUTLERY_POSITION_PERTURBATION`.
- Sometimes, there is a [`CupAndCoaster`](cup_and_coaster.md); see `TableSetting.PROBABILITY_CUP_AND_COASTER`.
  - The position of the `CupAndCoaster` is perturbed randomly; see `TableSetting.CUP_AND_COASTER_POSITION_PERTURBATION`.

***

## Fields

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `CUP_AND_COASTER_POSITION_PERTURBATION` | float | Randomly perturb the (x, z) positional coordinates of `CupAndCoaster` by up to +/- this distance. | `0.02` |
| `CUTLERY_POSITION_PERTURBATION` | float | Randomly perturb the (x, z) positional coordinates of the fork, knife and spoon by up to +/- this distance. | `0.03` |
| `CUTLERY_ROTATION_PERTURBATION` | float | Randomly perturb the rotation of the fork, knife, and spoon by +/- this many degrees. | `3` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `FOOD_CATEGORIES` | List[str] | The categories of possible food models. | `["apple", "banana", "chocolate", "orange", "sandwich"]` |
| `FOOD_PROBABILITY` | float | The probability from 0 to 1 of adding a food model on top of the plate. | `0.8` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |
| `PLATE_MODEL_NAME` | str | The model name of the plate. | `"plate06"` |
| `PROBABILITY_CUP_AND_COASTER` | float | The probability from 0 to 1 of adding a [`CupAndCoaster`](cup_and_coaster.md). | `0.66` |

***

## Functions

#### \_\_init\_\_

**`TableSetting(position)`**

**`TableSetting(position, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created. |

#### get_categories_and_wcategories

**`Arrangement.get_categories_and_wcategories()`**

_(Static)_

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.