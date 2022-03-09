# KitchenCounterTop

`from tdw.proc_gen.arrangements.kitchen_counter_top import KitchenCounterTop`

A floating kitchen counter top along a wall.

- The kitchen counter top is placed next to a wall and at a height equal to the height of the kitchen counter models.
  - The kitchen counter top's position is automatically adjusted to set it flush to the wall.
- The kitchen counter top will have a rectangular arrangement of objects on top of it. The objects are chosen randomly; see `KitchenCounterTop.ON_TOP_OF["kitchen_counter"]`.
- The kitchen counter top is kinematic.

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `MODEL_CATEGORIES` | Dict[str, List[str]] | A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`. | `loads(Path(resource_filename(__name__, "data/models.json")).read_text())` |
| `DEFAULT_CELL_SIZE` | float | The default span used for arranging objects next to each other. | `0.6096` |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. | `loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())` |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. | `loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())` |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. | `loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())` |

***

## Fields

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `root_object_id` The ID of the root object.

- `object_ids` A list of all of the object IDs in this arrangement.

- `object_ids` A list of all of the object IDs in this arrangement.

***

## Functions

#### \_\_init\_\_

**`KitchenCounterTop(cabinetry, wall, corner, distance)`**

**`KitchenCounterTop(cabinetry, wall, corner, distance, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| cabinetry |  KitchenCabinetSet |  | The [`KitchenCabinetSet`](kitchen_cabinets/kitchen_cabinet_set.md). |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
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