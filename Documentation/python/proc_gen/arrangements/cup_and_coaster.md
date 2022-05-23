# CupAndCoaster

`from tdw.proc_gen.arrangements.cup_and_coaster import CupAndCoaster`

A cup, which sometimes has a coaster underneath it.

- 50% of the time, there is a coaster underneath the cup.
  - The coaster model is chosen randomly; see `CupAndCoaster.MODEL_CATEGORIES["coaster"]`.
  - The coaster is rotated randomly; see `CupAndCoaster.ROTATION`.
- The cup model is chosen randomly and can be either a `"cup"` or a `"wineglass"`; see `CupAndCoaster.MODEL_CATEGORIES["cup"]` and `CupAndCoaster.MODEL_CATEGORIES["wineglass"]`.
  - If there is a coaster, the cup is on top of the coaster.
  - The rotation of the cup is random (0 to 360 degrees).

***

## Fields

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `CUP_CATEGORIES` | List[str] | A list of cup model categories. | `["cup", "wineglass"]` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ROTATION` | float | Coasters are randomly rotated up to +/- this many degrees. | `25` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`CupAndCoaster(position)`**

**`CupAndCoaster(position, rng=None)`**

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