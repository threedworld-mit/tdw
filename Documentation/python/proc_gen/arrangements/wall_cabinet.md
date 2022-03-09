# WallCabinet

`from tdw.proc_gen.arrangements.wall_cabinet import WallCabinet`

A wall cabinet hangs on the wall above a kitchen counter. It can have objects inside it.

- The wall cabinet model is chosen randomly; see `WallCabinet.MODEL_CATEGORIES["wall_cabinet"]`.
- The wall cabinet is placed next to a wall.
  - The wall cabinet's position is automatically adjusted to set it flush to the wall.
  - The wall cabinet is automatically rotated so that it faces away from the wall.
  - The wall cabinet is at a fixed height from the wall, see `WALL_CABINET.Y`.
- The wall cabinet always has objects inside of it. The contents are random:
  - Sometimes, there is a [`StackOfPlates`](stack_of_plates.md); see `WallCabinet.PROBABILITY_STACK_OF_PLATES`, `WallCabinet.MIN_NUM_PLATES`, and `WallCabinet.MAX_NUM_PLATES`.
  - Sometimes, there is a rectangular arrangement of random objects; see `WallCabinet.PROBABILITY_CUPS`.
- The root object of the wall cabinet is kinematic and the door sub-objects are non-kinematic.

***

## Fields

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

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `MAX_NUM_PLATES` | int | The maximum number of plates in a stack of plates. | `8` |
| `Y` | float | The value of the y positional coordinate (the height) of the wall cabinet. | `1.289581` |
| `MIN_NUM_PLATES` | int | The minimum number of plates in a stack of plates. | `3` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |
| `PROBABILITY_STACK_OF_PLATES` | float | To decide what is within the cabinet, a random number between 0 and 1 is generated. If the number is below this value, a [`StackOfPlates`](stack_of_plates.md) is added. | `0.33` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |
| `PROBABILITY_CUPS` | float | To decide what is within the cabinet, a random number between 0 and 1 is generated. If the number is below this value, a rectangular arrangement of cups and glasses is added. If the number is above this value, random objects are added (see `WallCabinet.ENCLOSED_BY["wall_cabinet"]`). | `0.66` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`WallCabinet(cabinetry, wall, corner, distance, region)`**

**`WallCabinet(cabinetry, wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| cabinetry |  KitchenCabinetSet |  | The [`KitchenCabinetSet`](kitchen_cabinets/kitchen_cabinet_set.md). |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
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