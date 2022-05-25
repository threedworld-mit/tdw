# Sink

`from tdw.proc_gen.arrangements.sink import Sink`

A sink can have objects on it and inside it.

- The sink model is chosen randomly; see `Sink.MODEL_CATEGORIES["sink"]`.
- The sink is placed next to a wall.
  - The sink's position is automatically adjusted to set it flush to the wall.
  - The sink is automatically rotated so that it faces away from the wall.
- The sink will have a rectangular arrangement of objects on the counter top.
  - The objects are chosen randomly; see `Sink.ON_TOP_OF["sink"]`.
  - The objects are positioned in a rectangular grid on the sink counter top with random rotations and positional perturbations; see `Sink.COUNTER_TOP_CELL_SIZE`, `Sink.COUNTER_TOP_CELL_DENSITY`, `Sink.COUNTER_TOP_WIDTH_SCALE`, and `Sink.COUNTER_TOP_DEPTH_SCALE`.
- The interior of the sink may be empty; see `empty` in the constructor.
  - If the interior is _not_ empty, the sink will have a rectangular arrangement of objects inside its cabinet.
    - The objects are chosen randomly; see `Sink.ENCLOSED_BY["sink"]`.
    - The objects are positioned in a rectangular grid in the sink cabinet with random rotations and positional perturbations; see `Sink.CABINET_CELL_SIZE`, `Sink.CABINET_CELL_DENSITY`, `Sink.CABINET_WIDTH_SCALE`, and `Sink.CABINET_DEPTH_SCALE`.
- There may be objects in the sink basin; see `Sink.IN_BASIN_PROBABILITY`.
  - The objects are chosen randomly; see `Sink.INSIDE_OF["sink"]`.
  - The objects are positioned in a rectangular arrangement in the sink basin; see: `Sink.BASIN_CELL_SIZE`, `Sink.BASIN_CELL_DENSITY`, `Sink.BASIN_WIDTH_SCALE`, and `Sink.BASIN_DEPTH_SCALE`.
- All sinks have doors that can open.
- The root object of the sink is kinematic and the door sub-objects are non-kinematic.

***

## Fields

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

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `BASIN_CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the sink basin rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.4` |
| `BASIN_CELL_SIZE` | float | The size of each cell in the sink basin rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.05` |
| `BASIN_DEPTH_SCALE` | float | When adding objects, the depth of the counter top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the sink basin. | `0.8` |
| `BASIN_WIDTH_SCALE` | float | When adding objects, the width of the sink basin is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the sink basin. | `0.8` |
| `CABINET_CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the cabinet rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.1` |
| `CABINET_CELL_SIZE` | float | The size of each cell in the cabinet rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.04` |
| `CABINET_DEPTH_SCALE` | float | When adding objects, the depth of the cabinet is assumed to be `actual_width * CABINET_DEPTH_SCALE`. This prevents objects from being too close to the edges of the cabinet. | `0.7` |
| `CABINET_WIDTH_SCALE` | float | When adding objects, the width of the cabinet is assumed to be `actual_width * CABINET_WIDTH_SCALE`. This prevents objects from being too close to the edges of the cabinet. | `0.7` |
| `COUNTER_TOP_CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the counter top rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.4` |
| `COUNTER_TOP_CELL_SIZE` | float | The size of each cell in the counter top rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.05` |
| `COUNTER_TOP_DEPTH_SCALE` | float | When adding objects, the depth of the counter top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the counter top. | `0.8` |
| `COUNTER_TOP_WIDTH_SCALE` | float | When adding objects, the width of the counter top is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the counter top. | `0.8` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `IN_BASIN_PROBABILITY` | float | The probability (0 to 1) of there being objects in the sink. | `0.7` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`Sink(cabinetry, wall, corner, distance, region)`**

**`Sink(cabinetry, wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| cabinetry |  Cabinetry |  | The [`Cabinetry`](cabinetry/cabinetry.md) set. |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`OrdinalDirection`](../../ordinal_direction.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
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