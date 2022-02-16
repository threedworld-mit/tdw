# ProcGenKitchen

`from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen`

Procedurally generate in a kitchen in a group of regions.

The kitchen always has 1 "main" rectangular region. It may have additional "alcoves", for example if the room is L-shaped.

The kitchen will have a "work triangle" of kitchen counters and appliances, a kitchen table with chairs and table settings (forks, knives, etc.), and "secondary objects" such as paintings and baskets.

## Procedural generation rules

### 1. Non-continuous walls, walls with windows, and wall lengths

Non-continuous walls are walls with gaps in the middle, such as doorways. Walls with windows have windows.

- Objects will never be placed along non-continuous walls.
- If a wall has windows, tall objects (see `ProcGenKitchen.TALL_CATEGORIES`) will be replaced with kitchen counters.
- If a wall has windows, paintings will never be placed on it.

For the sake of choosing walls for the "work triangles", `ProcGenKitchen` distinguishes between the two "longer walls" and the two "shorter walls" of the room.

### 2. Lateral arrangements and sub-arrangements

`ProcGenKitchen` arranges kitchen countertops and appliances in plausible “work triangles” along the region’s walls. These stretches of adjacent objects are called "lateral arrangements" within this class's code.

Each element in a lateral arrangement is a "sub-arrangement". A sub-arrangment maybe be a single object, but more often it is a group of objects, such as a kitchen counter with objects on top of it.

### 3. Work triangles

Work triangles are comprised of lateral arrangements. In some cases, the list of categories may be reversible. These categories generate sub-arrangements.

The following "work triangle" arrangements are possible:

| Shape    | Requirements                                                 | Preference                                                   | Categories                                                   | Reversible      |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------- |
| Straight | At least one continuous *longer* wall.                       | A wall with windows.                                      | `["refrigerator", "dishwasher", "sink", "kitchen_counter", "stove", "kitchen_counter", "shelf"]` | Yes             |
| Parallel | Two continuous *longer* walls.                               | *Only for the list with the "sink":* A wall with windows. | `["kitchen_counter", "stove", "kitchen_counter", "kitchen_counter", "kitchen_counter"]`<br>`["refrigerator", "dishwasher", "sink", "kitchen_counter", "kitchen_counter"]` | Yes<br>Yes      |
| L-Shape  | At least one continuous *longer* wall and one continuous *shorter* wall that share a corner. | *Longer wall:* A wall with windows.                       | *Longer wall:* `["floating_kitchen_counter_top", "sink", "dishwasher", "stove", "kitchen_counter", "shelf"]`<br><br>*Shorter wall:* `["kitchen_counter", "kitchen_counter", "refrigerator", "shelf"]` *OR* `["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"]` | No<br>No        |
| U-Shape  | At least one continuous *longer* wall. Two continuous *shorter* walls. | *Longer wall:* A wall with windows.                       | *Longer wall:* `["sink", "kitchen_counter", "stove", "kitchen_counter"]`<br>*Shorter wall:* `["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"]` *OR* `["kitchen_counter", "dishwasher", "kitchen_counter", "kitchen_counter"]` | Yes<br>No<br>No |

Additionally, the longer arrangement(s) of a "work triangle" may be extended with secondary sub-arrangements from the following categories: `["basket", "painting", "void", "radiator", "stool", "suitcase"]`.

### 4. Table arrangements

The table model is chosen randomly.

If there is at least one alcove that shares a non-continuous wall with the main region, then the table will be positioned near the shared boundary. If not, or if there are no alcoves, the table is placed in the center of the room, offset from the *used walls* of the "work triangle". For example, if the "work triangle" spans the north and west walls, then the table's position will be offset towards the southeast.

The table's position and rotation are randomly perturbed.

A table has 2-4 chairs around it depending on the model. The position and rotation of the chairs are randomly perturbed. The chairs are always the same model; the model is chosen randomly.

Each chair has a corresponding "table setting" on the table. Table settings always include a plate (the position is perturbed randomly), a fork to the left of the plate, and a knife and spoon to the right of the plate. The models for the fork, spoon, and knife are randomly selected but are the same for each table setting. The positions and rotations of the fork, knife, and spoon are randomly perturbed. A table setting sometimes includes a cup in front of the plate and spoon (“front” in this case meaning “along a vector pointing to the center of the tabletop”). The cup can be either a mug or a wineglass. Sometimes, the cup is on a coaster. The cup and/or coaster’s rotation and position are perturbed randomly. Sometimes, there is food on the plate; the food is randomly selected. The food’s rotation and position are perturbed randomly.

A table may have a random centerpiece object such as a jug or vase. The centerpiece position and rotation is perturbed randomly.

### 5. Secondary objects and arrangements

Any unused continuous walls in each region (the main region as well as the alcoves) may have arrangements of *secondary objects* along each wall.

The main region may have the following secondary sub-arrangements: side_table, basket, shelf, painting, void, radiator, stool, suitcase.

Alcove regions may have the following secondary sub-arrangements: side_table, basket, painting, void, radiator, stool, suitcase.

### 6. Model sub-arrangements

Unless otherwise noted, models will be rotated to face away from the wall they are adjacent to.

#### Shelf

A shelf model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["shelf"]`.

A shelving model has multiple “shelves”. Each shelf is a rectangular arrangement of objects from the following categories: book, bottle, bowl, candle, carving_fork, coaster, coffee_grinder, coffee_maker, coin, cork, cup, fork, house_plant, knife, ladle, jar, pan, pen, pot, scissors, soap_dispenser, spoon, tea_tray, vase

#### Kitchen counter

A kitchen counter model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["kitchen_counter"]`.

A kitchen counter can have objects on top of it from the following categories: apple, baking_sheet, banana, book, bottle, bowl, bread, candle, carving_fork, chocolate, coaster, coffee_grinder, coffee_maker, coin, cork, cup, fork, jar, jug, knife, ladle, orange, pan, pen, pepper, plate, pot, salt, sandwich, scissors, soap_dispenser, spaghetti_server, spatula, spoon, stove, tea_tray, teakettle, toaster, vase, whisk, wineglass

A 36-inch kitchen counter may instead have a microwave on top of it. The microwave can have the following objects on top of it: apple, banana, bread, bowl, cup, house_plant, jar, jug, pen, scissors, tea_tray, vase.

If the kitchen counter is on a wall that doesn’t have windows, it will also add a floating wall cabinet above it.

When `ProcGenKitchen` is initialized, it uses one of two wood visual materials for the kitchen counters and wall cabinets and corresponding counter top visual materials.

#### Floating kitchen counter top

A floating kitchen countertop is a cube primitive scaled to look like a kitchen countertop. It is used for some vertical arrangements such as the Dishwasher and also in lateral arrangements at the corner of an L shape. These countertops can have objects on top of them from the same categories as with kitchen counters; they can’t have microwaves or kitchen cabinets.

#### Refrigerator

A refrigerator model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["refrigerator"]`.

#### Stove

A stove model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["stove"]`. A stove can have objects on top of it from the following categories: baking_sheet, pan, pot, teakettle. The models, positions, and rotations are random.

#### Dishwasher

A dishwasher model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["dishwasher"]`.

A dishwasher has a floating kitchen countertop on top of it, scaled to match the dishwasher’s dimensions. See above for how floating kitchen countertop arrangements work.

#### Sink

There are no sink models at present; a sink for now is a kitchen counter (see above).

#### Basket

A basket model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["basket"]`.

The basket object has a random rotation.

A basket has objects within it. Objects are chosen from the following categories: coin, cork, fork, knife, pen, scissors, spoon. Baskets are at a random offset from the wall and have random rotations.

Objects are initially placed above the basket at increasing heights. For example, if the first object is placed at y=0.25, the next object will be placed above it. This way, the objects won’t interpenetrate. These objects have random pitch, yaw, and roll rotations.

#### Side table

A side table model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["side_table"]`.

A side table can have objects on top of it from the following categories: book, bottle, bowl, candle, coffee_grinder, coffee_maker, house_plant, jar, jug.

#### Painting

A painting model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["painting"]`.

A painting is a kinematic framed painting “hanging” on the wall. Paintings have random y values between 1.1 and a maximum defined by (room_height - painting_height).

#### Stool

A stool model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["stool"]`.

Stools have random rotations.

#### Stool

A stool model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["stool"]`.

Stools have random rotations.

#### Radiator

A radiator model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["radiator"]`.

#### Suitcase

A suitcase model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["suitcase"]`.

#### Void

A void is a special null category that just creates a gap in the secondary lateral arrangement.

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

- `scene_bounds` The [`SceneBounds`](../scene_data/scene_bounds.md). This is set after initializing or resetting `ProcGenObjects` and then calling `c.communicate()`.

- `cell_size` The cell size in meters. This is also used to position certain objects in subclasses of `ProcGenObjects`.

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



