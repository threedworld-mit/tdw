# WallCabinet

`from tdw.proc_gen.arrangements.wall_cabinet import WallCabinet`

A wall cabinet hangs on the wall above a kitchen counter. It can have objects inside it.

- The wall cabinet model is chosen randomly; see `WallCabinet.MODEL_CATEGORIES["wall_cabinet"]`.
- The wall cabinet is placed next to a wall.
  - The wall cabinet's position is automatically adjusted to set it flush to the wall.
  - The wall cabinet is automatically rotated so that it faces away from the wall.
  - The wall cabinet is at a fixed height from the wall, see `WALL_CABINET.Y`.
- The wall cabinet always has objects inside it. The contents are random:
  - Sometimes, there is a [`StackOfPlates`](stack_of_plates.md); see `WallCabinet.PROBABILITY_STACK_OF_PLATES`.
  - Sometimes, there is a rectangular arrangement of random objects; see `WallCabinet.PROBABILITY_CUPS`.
    - The objects are chosen randomly; see `WallCabinet.ENCLOSED_BY["wall_cabinet"]`.
    - The objects are positioned in a rectangular grid inside the wall cabinet with random rotations and positional perturbations; see `WallCabinet.CELL_SIZE`, `WallCabinet.CELL_DENSITY`, `WallCabinet.WIDTH_SCALE`, and `WallCabinet.DEPTH_SCALE`.
- The root object of the wall cabinet is kinematic and the door sub-objects are non-kinematic.

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
| `CELL_DENSITY` | float | The probability from 0 to 1 of a "cell" in the cabinet rectangular arrangement being empty. Lower value = a higher density of small objects. | `0.1` |
| `CELL_SIZE` | float | The size of each cell in the cabinet rectangular arrangement. This controls the minimum size of objects and the density of the arrangement. | `0.04` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `DEPTH_SCALE` | float | When adding objects, the depth of the cabinet is assumed to be `actual_width * CABINET_DEPTH_SCALE`. This prevents objects from being too close to the edges of the cabinet. | `0.8` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |
| `PROBABILITY_CUPS` | float | The probability between 0 and 1 of adding a rectangular arrangment of cups and glasses. | `0.66` |
| `PROBABILITY_STACK_OF_PLATES` | float | The probability between 0 and 1 of adding a [`StackOfPlates`](stack_of_plates.md). | `0.33` |
| `WIDTH_SCALE` | float | When adding objects, the width of the cabinet is assumed to be `actual_width * CABINET_WIDTH_SCALE`. This prevents objects from being too close to the edges of the cabinet. | `0.8` |
| `Y` | float | The value of the y positional coordinate (the height) of the wall cabinet. | `1.289581` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`WallCabinet(cabinetry, wall, corner, distance, region)`**

**`WallCabinet(cabinetry, wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

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