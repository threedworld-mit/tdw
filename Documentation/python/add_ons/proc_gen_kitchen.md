# ProcGenKitchen

`from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen`

Procedurally generate in a kitchen in a group of regions.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `KINEMATIC_CATEGORIES` | List[str] | Objects in these categories will be kinematic. |
| `RECTANGULAR_ARRANGEMENTS` | Dict[str, dict] | Parameters for rectangular arrangements. Key = Category. Value = Dictionary (`"cell_size"`, `"density"`). |
| `MODEL_NAMES_NINETY_DEGREES` | List[str] | The names of the models that are rotated 90 degrees. |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. |
| `BOUNDS_OFFSETS` | dict | Offset values for the bounds extents of specific models. |
| `ON_SHELF` | List[str] | Categories of models that can be placed on a shelf. |
| `IN_BASKET` | List[str] | Categories of models that can be placed in a basket. |
| `SHELF_DIMENSIONS` | Dict[str, dict] | Data for shelves. Key = model name. Value = Dictionary: "size" (a 2-element list), "ys" (list of shelf y's). |
| `NUMBER_OF_CHAIRS_AROUND_TABLE` | Dict[str, List[str]] | The number of chairs around kitchen tables. Key = The number as a string. Value = A list of model names. |
| `SECONDARY_CATEGORIES` | Dict[str, Dict[str, int]] | Categories of "secondary objects". |
| `WALL_CABINET_Y` | float | The y value (height) of the wall cabinets. |
| `COUNTERS_AND_CABINETS` | Dict[str, str] | A dictionary of the name of a kitchen counter model, and its corresponding wall cabinet. |
| `RADIATOR_ROTATIONS` | dict | The rotations of the radiator models. |
| `OBJECT_ROTATIONS` | Dict[str, Dict[str, int]] | A dictionary of canonical rotations for kitchen objects. Key = The model name. Value = A dictionary: Key = The wall as a string. Value = The rotation in degrees. |
| `TALL_CATEGORIES` | List[str] | Categories of models that are tall and might obscure windows. |
| `KITCHEN_TABLES_WITH_CENTERPIECES` | List[str] | Kitchen table models that can have centerpieces. |

***

## Fields

- `random_seed` The random seed.

- `rng` The random number generator.

- `scene_record` The record of the scene. This is set by `self.add_random_single_room_scene()`.

***

## Functions

#### \_\_init\_\_

**`ProcGenKitchen()`**

**`ProcGenKitchen(random_seed=None, print_random_seed=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| random_seed |  int  | None | The random seed. If None, a random seed is randomly selected. |
| print_random_seed |  bool  | True | If True, print the random seed. This can be useful for debugging. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### create

**`self.create(room)`**

Create a kitchen. Populate it with a table and chairs, kitchen counters and wall cabinets, and appliances.
Objects may be on top of or inside of larger objects.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| room |  Room |  | The [`Room`](../scene_data/room.md) that the kitchen is in. |

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### reset

**`self.reset()`**

**`self.reset(set_random_seed=False, random_seed=False)`**

Reset the procedural generator. Call this when resetting the scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| set_random_seed |  bool  | False | If True, set a new random seed. |
| random_seed |  bool  | False | The random seed. If None, a random seed is randomly selected. Ignored if `set_random_seed == False` |

#### add_random_single_room_scene

**`self.add_random_single_room_scene()`**

Load a random single-room streamed scene. Cache the record as `self.scene_record`.

#### get_categories_and_wcategories

**`self.get_categories_and_wcategories()`**

_Returns:_  A dictionary of the categories of every model that can be used by `ProcGenObjects` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### add_lateral_arrangement

**`self.add_lateral_arrangement(position, wall, direction, sub_arrangements, length, region)`**

**`self.add_lateral_arrangement(position, wall, direction, sub_arrangements, length, region, check_object_positions=False)`**

Create a linear arrangement of objects, each one adjacent to the next.
The objects can have other objects on top of them.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Dict[str, float] |  | The start position of the lateral arrangement. |
| wall |  CardinalDirection |  | The wall that the lateral arrangement runs along. |
| direction |  CardinalDirection |  | The direction that the lateral arrangement runs towards. |
| sub_arrangements |  List[LateralSubArrangement] |  | The ordered list of sub-arrangements. |
| length |  float |  | The maximum length of the lateral arrangement. |
| region |  RegionWalls |  | [The `RegionWalls` data.](../scene_data/region_walls.md) |
| check_object_positions |  bool  | False | If True, try to avoid placing objects near existing objects. |



