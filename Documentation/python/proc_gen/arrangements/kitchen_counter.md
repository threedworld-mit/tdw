# KitchenCounter

`from tdw.proc_gen.arrangements.kitchen_counter import KitchenCounter`

A kitchen counter can have objects on it and inside it.

- The kitchen counter model is chosen randomly; see `KitchenCounter.MODEL_CATEGORIES["kitchen_counter"]`.
- The kitchen counter is placed next to a wall.
  - The kitchen counter's position is automatically adjusted to set it flush to the wall.
  - The kitchen counter is automatically rotated so that it faces away from the wall.
- A kitchen counter longer than 0.7 meters may have a [`Microwave`](microwave.md); see `allow_microwave` in the constructor.
  - If the kitchen counter does _not_ have a microwave:
    - If the kitchen counter is alongside a wall without windows and has a corresponding wall cabinet model, a [`WallCabinet`](wall_cabinet.md) will be added above it; see `KitchenCounter.COUNTERS_AND_CABINETS`.
    - The kitchen counter will have a rectangular arrangement of objects on top of it. The objects are chosen randomly; see `KitchenCounter.ON_TOP_OF["kitchen_counter"]`.
- The interior of the kitchen counter may be empty; see `empty` in the constructor.
  - If the interior is _not_ empty, the kitchen counter will have a rectangular arrangement of objects inside of it. The objects are chosen randomly; see `KitchenCounter.ENCLOSED_BY["kitchen_counter"]`.
- All kitchen counters have doors that can open.
- The root object of the kitchen counter is kinematic and the door sub-objects are non-kinematic.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `COUNTERS_AND_CABINETS` | Dict[str, str] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/counters_and_cabinets.json")).read_text())` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |

***

## Fields

- `has_microwave` If True, this kitchen counter has a microwave.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Functions

#### \_\_init\_\_

**`KitchenCounter(cabinetry, wall, corner, distance, region)`**

**`KitchenCounter(cabinetry, wall, corner, distance, region, allow_microwave=True, microwave_plate=0.7, empty=0.1, model=None, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| cabinetry |  KitchenCabinetSet |  | The [`KitchenCabinetSet`](kitchen_cabinets/kitchen_cabinet_set.md). |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
| allow_microwave |  bool  | True | If True, and if this kitchen counter is longer than 0.7 meters, there will be a [`Microwave`](microwave.md) instead of an arrangement of objects on the counter top. |
| microwave_plate |  float  | 0.7 | The probability (between 0 and 1) of adding a [`Plate`](plate.md) to the inside of the microwave. |
| empty |  float  | 0.1 | The probability (between 0 and 1) of the of the kitchen counter being empty. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`, or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected. |
| wall_length |  float  | None | The total length of the lateral arrangement. If None, defaults to the length of the wall. |
| rng |  np.random.RandomState  | None | The random number generator. If None, a new random number generator is created. |

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