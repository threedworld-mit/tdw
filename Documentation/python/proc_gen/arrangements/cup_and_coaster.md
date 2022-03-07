# CupAndCoaster

`from proc_gen.arrangements.cup_and_coaster import CupAndCoaster`

A cup, which sometimes has a coaster underneath it.

- 50% of the time, there is a coaster underneath the cup.
  - The coaster model is chosen randomly; see `CupAndCoaster.MODEL_CATEGORIES["coaster"]`.
  - The coaster is rotated randomly; see `CupAndCoaster.ROTATION`.
- The cup model is chosen randomly and can be either a `"cup"` or a `"wineglass"`; see `CupAndCoaster.MODEL_CATEGORIES["cup"]` and `CupAndCoaster.MODEL_CATEGORIES["wineglass"]`.
  - If there is a coaster, the cup is on top of the coaster.
  - The rotation of the cup is random (0 to 360 degrees).

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. |
| `ROTATION` | float | Coasters are randomly rotated up to +/- this many degrees. |

***

## Fields

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Functions

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

### \_\_init\_\_

**`Arrangement(position)`**

**`Arrangement(position, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| rng |  np.random.RandomState  | None | The random number generator. If None, a new random number generator is created. |



#### get_categories_and_wcategories

**`Arrangement(ABC).get_categories_and_wcategories()`**

_This is a static function._

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

