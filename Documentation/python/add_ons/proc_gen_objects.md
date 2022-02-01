# ProcGenObjects

`from tdw.add_ons.proc_gen_objects import ProcGenObjects`

Procedurally arrange objects using spatial relations and categories.
For example, certain object categories can be *on top of* other object categories.

Note regarding categories: Every "category" parameter *always* refers to specialized "proc-gen categories" that overlap with `record.wcategory` but are not the same. To get a mapping:

```python
from tdw.add_ons.proc_gen_objects import ProcGenObjects

categories = ProcGenObjects.get_categories_and_wcategories()
for model_name in categories:
    print(model_name, categories[model_name]["category"], categories[model_name]["wcategory"], categories[model_name]["wnid"])
```

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | The names of models suitable for proc-gen. Key = The category. Value = A list of model names. |
| `KINEMATIC_CATEGORIES` | List[str] | Objects in these categories will be kinematic. |
| `RECTANGULAR_ARRANGEMENTS` | Dict[str, dict] | Parameters for rectangular arrangements. Key = Category. Value = Dictionary (`"cell_size"`, `"density"`). |
| `MODEL_NAMES_NINETY_DEGREES` | List[str] | The names of the models that are rotated 90 degrees. |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. |

***

## Fields

- `random_seed` The random seed.

- `rng` The random number generator.

- `scene_bounds` The [`SceneBounds`](../scene_data/scene_bounds.md). This is set after initializing or resetting `ProcGenObjects` and then calling `c.communicate()`.

- `cell_size` The cell size in meters. This is also used to position certain objects in subclasses of `ProcGenObjects`.

***

## Functions

#### \_\_init\_\_

**`ProcGenObjects()`**

**`ProcGenObjects(random_seed=None, cell_size=0.6096, print_random_seed=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| random_seed |  int  | None | The random seed. If None, a random seed is randomly selected. |
| cell_size |  float  | 0.6096 | The cell size in meters. This is also used to position certain objects in subclasses of `ProcGenObjects`. |
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

#### fits_inside_parent

**`ProcGenObjects(AddOn).fits_inside_parent(parent, child)`**

_This is a static function._


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| parent |  ModelRecord |  | The record of the parent object. |
| child |  ModelRecord |  | The record of the child object. |

_Returns:_  True if the child object fits in the the parent object.

#### model_fits_in_region

**`self.model_fits_in_region(record, position, region)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| record |  ModelRecord |  | The model record. |
| position |  Dict[str, float] |  | The position of the object. |
| region |  int |  | The index of the region in `self.scene_bounds.rooms`. |

_Returns:_  True if the model fits in the region.

#### get_model_that_fits_in_region

**`self.get_model_that_fits_in_region(category, position, region)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| category |  str |  | The model category. |
| position |  Dict[str, float] |  | The position of the object. |
| region |  int |  | The index of the region in `self.scene_bounds.rooms`. |

_Returns:_  A random model that fits in the region at `position`. If this returns None, no model fits.

#### add_rotation_commands

**`self.add_rotation_commands(parent_object_id, child_object_ids, rotation)`**

Add commands to parent the child objects to the parent object, rotate the parent object, and unparent the child objects.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| parent_object_id |  int |  | The ID of the parent object. |
| child_object_ids |  List[int] |  | The IDs of the child objects. |
| rotation |  float |  | The rotation of the parent object. |

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

**`ProcGenObjects(AddOn).get_categories_and_wcategories()`**

_This is a static function._

_Returns:_  A dictionary of the categories of every model that can be used by `ProcGenObjects`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).

#### get_rectangular_arrangement_parameters

**`ProcGenObjects(AddOn).get_rectangular_arrangement_parameters(category)`**

_This is a static function._

Given a category, get the default rectangular arrangement parameters.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| category |  str |  | The category |

_Returns:_  Tuple: The cell size and density.

#### get_lateral_length

**`ProcGenObjects(AddOn).get_lateral_length(model_name)`**

_This is a static function._


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_name |  str |  | The model name. |

_Returns:_  The model bound's longest extent.

#### get_longer_walls

**`self.get_longer_walls(region)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| region |  int |  | The index of the region in `self.scene_bounds.rooms`. |

_Returns:_  Tuple: A list of the longer walls as [`CardinalDirection` values](../cardinal_direction.md), the length of the wall.

#### get_shorter_walls

**`self.get_shorter_walls(region)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| region |  int |  | The index of the region in `self.scene_bounds.rooms`. |

_Returns:_  Tuple: A list of the shorter walls as [`CardinalDirection` values](../cardinal_direction.md), the length of the wall.

#### get_corners_from_wall

**`ProcGenObjects(AddOn).get_corners_from_wall(wall)`**

_This is a static function._


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../cardinal_direction.md). |

_Returns:_  The corners of the wall as a 2-element list of [`OrdinalDirection`](../ordinal_direction.md).

