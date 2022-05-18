# Microwave

`from tdw.proc_gen.arrangements.microwave import Microwave`

A microwave can have objects on top of it and inside of it.

- The microwave model is chosen randomly; see `Microwave.MODEL_CATEGORIES["microwave"]`
- A microwave always has a rectangular arrangement of objects on top of it.
  - The objects are chosen randomly; see `Microwave.ON_TOP_OF["microwave"]`.
  - The objects are positioned in a rectangular grid on the microwave with random positional perturbations.
  - The objects have random rotations (0 to 360 degrees).
- A microwave may have a [`Plate`](plate.md) inside it; see `plate_probability` and `food_probability` in the constructor.
- All microwaves have a door that can be opened.
- The root object of the microwave is kinematic and the door sub-object is non-kinematic.

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |

***

## Fields

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Functions

#### \_\_init\_\_

**`Microwave(plate_probability, food_probability, wall, position)`**

**`Microwave(plate_probability, food_probability, wall, position, plate_model="plate06", model="plate06", rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| plate_probability |  float |  | The probability of placing a `Plate` arrangement inside the microwave. |
| food_probability |  float |  | The probability of placing food on the plate. |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| plate_model |  Union[str, ModelRecord] | "plate06" | The name of the plate model. |
| model |  Union[str, ModelRecord] | "plate06" | Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a random model in the category is selected. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created. |

#### get_categories_and_wcategories

**`Arrangement.get_categories_and_wcategories()`**

_(Static)_

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.