# ProcGenKitchen

`from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen`

Procedurally generate in a kitchen in a group of regions.

***

## Fields

- `random_seed` The random seed.

- `rng` The random number generator.

- `scene_bounds` The [`SceneBounds`](../scene_data/scene_bounds.md). This is set after initializing or resetting `ProcGenObjects` and then calling `c.communicate()`.

- `cell_size` The cell size in meters. This is also used to position certain objects in subclasses of `ProcGenObjects`.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `BOUNDS_OFFSETS` | dict | Offset values for the bounds extents of specific models. | `loads(Path(resource_filename(__name__, "proc_gen_objects_data/bounds_offsets.json")).read_text())` |
| `COUNTERS_AND_CABINETS` | Dict[str, str] | A dictionary of the name of a kitchen counter model, and its corresponding wall cabinet. | `loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/counters_and_cabinets.json")).read_text())` |
| `IN_BASKET` | List[str] | Categories of models that can be placed in a basket. | `Path(resource_filename(__name__, "proc_gen_kitchen_data/categories_in_basket.txt")).read_text().split("
")` |
| `KINEMATIC_CATEGORIES` | List[str] | Objects in these categories will be kinematic. | `Path(resource_filename(__name__, "proc_gen_objects_data/kinematic_categories.txt")).read_text().split("
")` |
| `KITCHEN_TABLES_WITH_CENTERPIECES` | List[str] | Kitchen table models that can have centerpieces. | `["dining_room_table",` |
| `MODEL_NAMES_NINETY_DEGREES` | List[str] | The names of the models that are rotated 90 degrees. | `Path(resource_filename(__name__, "proc_gen_objects_data/model_names_ninety_degrees.txt")).read_text().split("
")` |
| `NUMBER_OF_CHAIRS_AROUND_TABLE` | Dict[str, List[str]] | The number of chairs around kitchen tables. Key = The number as a string. Value = A list of model names. | `loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/chairs_around_tables.json")).read_text())` |
| `OBJECT_ROTATIONS` | Dict[str, Dict[str, int]] | A dictionary of canonical rotations for kitchen objects. Key = The model name. Value = A dictionary: Key = The wall as a string. Value = The rotation in degrees. | `loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/object_rotations.json")).read_text())` |
| `ON_SHELF` | List[str] | Categories of models that can be placed on a shelf. | `Path(resource_filename(__name__, "proc_gen_kitchen_data/categories_on_shelf.txt")).read_text().split("
")` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "proc_gen_objects_data/on_top_of.json")).read_text())` |
| `RADIATOR_ROTATIONS` | dict | The rotations of the radiator models. | `loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/radiator_rotations.json")).read_text())` |
| `RECTANGULAR_ARRANGEMENTS` | Dict[str, dict] | Parameters for rectangular arrangements. Key = Category. Value = Dictionary (`"cell_size"`, `"density"`). | `loads(Path(resource_filename(__name__, "proc_gen_objects_data/rectangular_arrangements.json")).read_text())` |
| `SECONDARY_CATEGORIES` | Dict[str, Dict[str, int]] | Categories of "secondary objects". | `loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/secondary_categories.json")).read_text())` |
| `SHELF_DIMENSIONS` | Dict[str, dict] | Data for shelves. Key = model name. Value = Dictionary: "size" (a 2-element list), "ys" (list of shelf y's). | `loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/shelf_dimensions.json")).read_text())` |
| `TALL_CATEGORIES` | List[str] | Categories of models that are tall and might obscure windows. | `["refrigerator", "shelf"]` |
| `WALL_CABINET_Y` | float | The y value (height) of the wall cabinets. | `1.289581` |

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

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### add_rectangular_arrangement

**`self.add_rectangular_arrangement(size, position, categories)`**

**`self.add_rectangular_arrangement(size, position, categories, density=0.4, cell_size=0.05)`**

Get a random arrangement of objects in a rectangular space.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| size |  Tuple[float, float] |  | The size of the rectangle in worldspace coordinates. |
| position |  Dict[str, float] |  | The position of the center of the rectangle. |
| categories |  List[str] |  | Models will be randomly chosen from these categories. |
| density |  float  | 0.4 | The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects. |
| cell_size |  float  | 0.05 | The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement. |

_Returns:_  The IDs of the objects.

#### add_object_with_other_objects_on_top

**`self.add_object_with_other_objects_on_top(record, category, position, rotation)`**

Add a root object and add objects on  top of it.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| record |  ModelRecord |  | The model record of the root object. |
| category |  str |  | The category of the root object. |
| position |  Dict[str, float] |  | The position of the root object. |
| rotation |  float |  | The rotation of the root object. |

#### reset

**`self.reset()`**

**`self.reset(set_random_seed=False, random_seed=False)`**

Reset the procedural generator. Call this when resetting the scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| set_random_seed |  bool  | False | If True, set a new random seed. |
| random_seed |  bool  | False | The random seed. If None, a random seed is randomly selected. Ignored if `set_random_seed == False` |

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

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### create

**`self.create(room)`**

Create a kitchen. Populate it with a table and chairs, kitchen counters and wall cabinets, and appliances.
Objects may be on top of or inside of larger objects.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| room |  Room |  | The [`Room`](../scene_data/room.md) that the kitchen is in. |