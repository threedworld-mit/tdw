# KitchenCounter

`from tdw.proc_gen.arrangements.kitchen_counter import KitchenCounter`

A kitchen counter can have objects on it and inside it.

- The kitchen counter model is chosen randomly; see `KitchenCounter.MODEL_CATEGORIES["kitchen_counter"]`.
- The kitchen counter is placed next to a wall.
  - The kitchen counter's position is automatically adjusted to set it flush to the wall.
  - The kitchen counter is automatically rotated so that it faces away from the wall.
- A kitchen counter longer than 0.7 meters may have a [`Microwave`](microwave.md); see `allow_microwave` in the constructor.
    - If the kitchen counter is alongside a wall without windows and has a corresponding wall cabinet model, a [`WallCabinet`](wall_cabinet.md) will be added above it; see `KitchenCounter.COUNTERS_AND_CABINETS`.
    - The kitchen counter will have a rectangular arrangement of objects on top of it.
      - The objects are chosen randomly; see `KitchenCounter.ON_TOP_OF["kitchen_counter"]`.
      - The objects are positioned in a rectangular grid on the counter top with random rotations and positional perturbations; see `KitchenCounter.COUNTER_TOP_CELL_SIZE`, `KitchenCounter.COUNTER_TOP_CELL_DENSITY`, `KitchenCounter.COUNTER_TOP_WIDTH_SCALE`, and `KitchenCounter.COUNTER_TOP_DEPTH_SCALE`.
- The interior of the kitchen counter may be empty; see `cabinet_is_empty_probability` in the constructor.
  - If the interior is _not_ empty, the kitchen counter will have a rectangular arrangement of objects inside its cabinet.
    - The objects are chosen randomly; see `KitchenCounter.ENCLOSED_BY["kitchen_counter"]`.
    - The objects are positioned in a rectangular grid inside the cabinet with random rotations and positional perturbations; see `KitchenCounter.CABINET_CELL_SIZE`, `KitchenCounter.CABINET_CELL_DENSITY`, `KitchenCounter.CABINET_WIDTH_SCALE`, and `KitchenCounter.CABINET_DEPTH_SCALE`.
- All kitchen counters have doors that can open.
- The root object of the kitchen counter is kinematic and the door sub-objects are non-kinematic.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `CABINET_CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the cabinet rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.1` |
| `CABINET_CELL_SIZE` | float | The size of each cell in the cabinet rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.04` |
| `CABINET_DEPTH_SCALE` | float | When adding objects, the depth of the cabinet is assumed to be `actual_width * CABINET_DEPTH_SCALE`. This prevents objects from being too close to the edges of the cabinet. | `0.7` |
| `CABINET_WIDTH_SCALE` | float | When adding objects, the width of the cabinet is assumed to be `actual_width * CABINET_WIDTH_SCALE`. This prevents objects from being too close to the edges of the cabinet. | `0.7` |
| `COUNTERS_AND_CABINETS` | Dict[str, str] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/counters_and_cabinets.json")).read_text())` |
| `COUNTER_TOP_CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the counter top rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.4` |
| `COUNTER_TOP_CELL_SIZE` | float | The size of each cell in the counter top rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.05` |
| `COUNTER_TOP_DEPTH_SCALE` | float | When adding objects, the depth of the counter top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the counter top. | `0.8` |
| `COUNTER_TOP_WIDTH_SCALE` | float | When adding objects, the width of the counter top is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the counter top. | `0.8` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |

***

## Fields

- `has_microwave` If True, this kitchen counter has a microwave.

- `send_commands` If True, send commands when `self.get_commands()` is called. If False, `self.get_commands()` will return an empty list.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

- `send_commands` If True, send commands when `self.get_commands()` is called. If False, `self.get_commands()` will return an empty list.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Functions

#### \_\_init\_\_

**`KitchenCounter(cabinetry, wall, corner, distance, region)`**

**`KitchenCounter(cabinetry, wall, corner, distance, region, allow_microwave=True, cabinet_is_empty_probability=0.1, model=None, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| cabinetry |  Cabinetry |  | The [`Cabinetry`](cabinetry/cabinetry.md) set. |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`OrdinalDirection`](../../ordinal_direction.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
| allow_microwave |  bool  | True | If True, and if this kitchen counter is longer than 0.7 meters, there will be a [`Microwave`](microwave.md) instead of an arrangement of objects on the counter top. |
| cabinet_is_empty_probability |  float  | 0.1 | The probability (between 0 and 1) of the of the kitchen counter cabinet and wall cabinet being empty. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected. |
| wall_length |  float  | None | The total length of the lateral arrangement. If None, defaults to the length of the wall. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created. |

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