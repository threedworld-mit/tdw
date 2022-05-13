# StackOfPlates

`from tdw.proc_gen.arrangements.stack_of_plates import StackOfPlates`

A stack of plates.

- The plate model is chosen randomly and is the same for each plate; see `StackOfPlates.MODEL_CATEGORIES["plate"]`.
- The number of plates in the stack is random; see `min_num` and `max_num` in the constructor.

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |

***

## Fields

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Functions

#### \_\_init\_\_

**`StackOfPlates(min_num, max_num, position, rng)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| min_num |  int |  | The minimum number of plates. |
| max_num |  int |  | The maximum number of plates. |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| rng |  np.random.RandomState |  | The random number generator. |

#### get_categories_and_wcategories

**`Arrangement.get_categories_and_wcategories()`**

_(Static)_

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.