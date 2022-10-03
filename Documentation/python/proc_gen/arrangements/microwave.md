# Microwave

`from tdw.proc_gen.arrangements.microwave import Microwave`

A microwave can have objects on top of it and inside of it.

- The microwave model is chosen randomly; see `Microwave.MODEL_CATEGORIES["microwave"]`
- A microwave always has a rectangular arrangement of objects on top of it.
  - The objects are chosen randomly; see `Microwave.ON_TOP_OF["microwave"]`.
  - The objects are positioned in a rectangular grid on the microwave with random rotations and positional perturbations; see `Microwave.CELL_SIZE`, `Microwave.CELL_DENSITY`, `Microwave.WIDTH_SCALE`, and `Microwave.DEPTH_SCALE`.
- A microwave may have a [`Plate`](plate.md) inside it; see `Microwave.PLATE_PROBABILITY`.
- All microwaves have a door that can be opened.
- The root object of the microwave is kinematic and the door sub-object is non-kinematic.

***

## Fields

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the rectangular arrangement  on top of the microwave being empty. Lower value = a higher density of small objects. | `0.4` |
| `CELL_SIZE` | float | The size of each cell in the rectangular arrangement on top of the microwave. This controls the minimum size of objects and the density of the arrangement. | `0.05` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |
| `PLATE_MODEL` | str | The model name of the plate that will be placed in the microwave (if any). | `"plate06"` |
| `PLATE_PROBABILITY` | float | The probability from 0 to 1 of placing a [`Plate`](plate.md) arrangement inside the microwave. | `0.7` |

***

## Functions

#### \_\_init\_\_

**`Microwave(wall, position)`**

**`Microwave(wall, position, model=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a random model in the category is selected. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created. |

#### get_categories_and_wcategories

**`Arrangement.get_categories_and_wcategories()`**

_(Static)_

_Returns:_  A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.