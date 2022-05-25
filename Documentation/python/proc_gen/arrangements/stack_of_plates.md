# StackOfPlates

`from tdw.proc_gen.arrangements.stack_of_plates import StackOfPlates`

A stack of plates.

- The plate model is chosen randomly and is the same for each plate; see `StackOfPlates.MODEL_CATEGORIES["plate"]`.
- The number of plates in the stack is random; see `StackOfPlates.MIN_NUM` and `StackOfPlates.MAX_NUM`.

***

## Fields

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `MAX_NUM` | int | The maximum number of plates in a stack of plates. | `8` |
| `MIN_NUM` | int | The minimum number of plates in a stack of plates. | `3` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`StackOfPlates(position)`**

**`StackOfPlates(position, rng=None)`**

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