# ProcGenKitchen

`from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen`

Procedurally generate a kitchen in a new scene or an existing scene.

## Procedural generation algorithm

This is an explanation of how `proc_gen_kitchen.create()` works.

### 1. Set the random number generator

It is possible to explicitly set the random number generator via the `rng` parameter. Doing so will allow you to recreate the exact same scene later.

### 2. Set `self.room`

If the `scene` parameter is of type [`Room`](../scene_data/room.md) this is straightforward. Otherwise, select a scene from the `scene` parameter (which will be loaded into TDW) and get the `Room` from the `room_index` parameter.

### 3. Select a set of cabinetry

[`Cabinetry`](../proc_gen/arrangements/cabinetry/cabinetry.md) always visually match each other. A `Cabinetry` data object is selected randomly.

### 4. Create a work triangle

A [work triangle](https://kbcrate.com/kitchen-design-kitchen-work-triangle-improve-workspace/) defines the overall design of the kitchen space.

A work triangle is comprised of 1 or more _lateral arrangements_ of [`Arrangement`](../proc_gen/arrangements/arrangement.md) data objects along a wall, starting at a given distance from a corner.

In all lateral arrangements in `ProcGenKitchen`, the following rules are always followed:

- In the wall has windows, tall `Arrangements` will be replaced with shorter `Arrangements`; see `ProcGenKitchen.TALL_ARRANGEMENTS`. For work triangles, tall `Arrangements` will be replaced with [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md).
- Non-continuous walls (e.g. a wall with a doorway) will never have a lateral arrangement.
- Each wall has two corresponding corners. For example, a `north` wall has corners `north_west` and `north_east`. One of these corners is selected for the start of the lateral arrangement. Unless otherwise noted, the corner is chosen randomly.
- A lateral arrangement has a list of `Arrangements`. They may not all fit along the wall, in which case as many `Arrangements` are added as possible.

Work triangle lateral arrangements have the following additional shared rules:

- Each work triangle lateral arrangement has *secondary arrangements* appended to its list to spatially lengthen it. Possibilities are: [[`Basket`](../proc_gen/arrangements/basket.md), [`Painting`](../proc_gen/arrangements/painting.md), [`Void`](../proc_gen/arrangements/void.md), [`Radiator`](../proc_gen/arrangements/radiator.md), [`Stool`](../proc_gen/arrangements/stool.md), [`Suitcase`](../proc_gen/arrangements/suitcase.md)]. The selection is random with weighted probability; see `ProcGenKitchen.SECONDARY_ARRANGEMENTS["append"]`.

In TDW there are four possible work triangles:

#### 4a. Straight

A single lateral arrangement along one of the longer walls.

**Requirements:** At least one continuous longer wall.

1. If one of the longer walls has windows, it will be used for the lateral arrangement. Otherwise, the wall is chosen randomly.
2. There are two possible lateral arrangements, chosen randomly:
  - [[`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
  - [[`Shelf`](../proc_gen/arrangements/shelf.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Sink`](../proc_gen/arrangements/sink.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md)]

#### 4b. Parallel

Two lateral arrangements along both longer walls.

**Requirements:** Two continuous longer walls.

1. If one of the longer walls has windows, it will be used for the lateral arrangement with the sink. Otherwise, each lateral arrangement uses a random longer wall.
2. For the first lateral arrangement, there are two possibilities, chosen randomly:
  - [[`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
  - [[`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Sink`](../proc_gen/arrangements/sink.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md)]
3. For the second lateral arrangement, there are two possibilities, chosen randomly:
  - [[`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
  - [[`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]

#### 4c. L-Shape

One lateral arrangement along a longer wall and one lateral arrangement along a shorter wall. The two arrangements share a common corner.

**Requirements:** At least one continuous longer wall and one continuous shorter wall.

1. If one of the longer walls has windows, it will be used for the longer lateral arrangement. Otherwise, the wall is chosen randomly.
2. There are two possible longer lateral arrangements, each with a `KitchenCounterTop` at the end. If both shorter walls are continuous, the selected lateral arrangement is random. Otherwise, `ProcGenKitchen` finds a corner shared by the longer wall and a continuous corner wall and selects the arrangement in which the `KitchenCounterTop` is placed at the common corner; for example if the longer wall is `north` and the only continuous wall is `west` then the longer arrangement is the first of the following two options because it `KitchenCounterTop` will be placed at the northwest corner.
  - [[`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md), [`Sink`](../proc_gen/arrangements/sink.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
  - [[`Shelf`](../proc_gen/arrangements/shelf.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md)]
3. The shorter lateral arrangement is placed at the corresponding valid wall (see above). There are two possibilities, chosen randomly:
  - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
  - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]

#### 4d. U-Shape

One lateral arrangement along a longer wall and two lateral arrangements along both shorter walls.

**Requirements:** At least one continuous longer wall and two continuous shorter walls.

1. If one of the longer walls has windows, it will be used for the longer lateral arrangement. Otherwise, the wall is chosen randomly.
2. There are two possible longer lateral arrangements, chosen randomly:
  - [[`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
  - [[`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
3. Each of the longer lateral arrangements will have additional 20 `KitchenCounters` appended. It is unlikely that there will ever actually be this many counters. Just before running out of space along the wall, the lateral arrangement will add a `KitchenCounterTop` instead (to anchor the corner).
4. There are two possible shorter lateral arrangements. The wall on which they appear is chosen randomly:
  - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
  - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]

***

### 5. Add a table

Add a [`KitchenTable`](../proc_gen/arrangements/kitchen_table.md).

The work triangles generate a list of commands and a list of used walls. This list of used walls is used as a parameter in `KitchenTable` to prevent chairs from intersecting with work triangle objects.

### 6. Add secondary arrangements

Add secondary lateral arrangements to unused walls in the main region of the room and the walls of the alcove regions. See: `ProcGenKitchen.SECONDARY_ARRANGEMENTS["main"]` and  `ProcGenKitchen.SECONDARY_ARRANGEMENTS["alcove"]`.

### 7. Step 50 physics frames

This allows objects to stop moving.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `SCENE_NAMES` | List[str] | The names of the default scenes. If the `scene` parameter in `self.create()` isn't set, or is set to None, a random scene from this list will be selected. | `['mm_craftroom_2a', 'mm_craftroom_2b', 'mm_craftroom_3a', 'mm_craftroom_3b', 'mm_kitchen_2a', 'mm_kitchen_2b', 'mm_kitchen_3a', 'mm_kitchen_3b']` |
| `SECONDARY_ARRANGEMENTS` | Dict[str, Dict[str, int]] | A dictionary of "secondary arrangements". Keys: `"append"` (can be appended to a work triangle lateral arrangement), `"main"` (can be added to a lateral arrangement along an unused wall in the main [region](../scene_data/interior_region.md) of [`self.room`](../scene_data/room.md)), and `"alcove"` (can be added to a lateral arrangement along an unused wall of an alcove region). Value: A dictionary of probabilities and names of arrangements; a higher value means that it is more likely for this arrangement to be randomly selected. | `loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/secondary_categories.json")).read_text())` |
| `TALL_ARRANGEMENTS` | List[str] | [`Arrangements`](../proc_gen/arrangements/arrangement.md) that are tall and might obscure windows. | `["refrigerator", "shelf"]` |

***

## Fields

- `rng` The random number generator.

- `scene_record` The `SceneRecord` for this scene. This gets set by `self.create()` and can be None if the `scene` parameter is a [`Room`](../scene_data/room.md).

- `room` The kitchen [`Room`](../scene_data/room.md). This gets set by `self.create()`.

- `cabinetry` The [`Cabinetry`](../proc_gen/arrangements/cabinetry/cabinetry.md). This is set randomly by `self.create()`.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ProcGenKitchen()`**

(no parameters)

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

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### create

**`self.create(scene)`**

**`self.create(scene, room_index=0, cabinetry_type=None, rng=None)`**

Procedurally generate a kitchen. The kitchen will be created on the next `controller.communicate()` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| scene |  Union[str, SceneRecord, Room, List[Union[str, SceneRecord] |  | Can be a string (the name of a scene), a [`SceneRecord`](../librarian/scene_librarian.md), a list of scene names and/or `SceneRecord` (one will chosen randomly), a [`Room`](../scene_data/room.md), or None. If this is a `Room`, then `ProcGenKitchen` will assume that the scene has already been loaded, and `self.scene_record` will be set to `None`. If `scene=None`, a random scene from `ProcGenKitchen.SCENE_NAMES` will be selected. |
| room_index |  int  | 0 | The index of the room in `self.scene_record.rooms` (assuming `self.scene_record is not None`; see above). |
| cabinetry_type |  CabinetryType  | None | A [`CabinetryType`](../proc_gen/arrangements/cabinetry/cabinetry_type.md) value that sets which kitchen cabinets, wall cabinets, and sinks to add to the scene. If None, a `CabinetryType` is chosen randomly. |
| rng |  Union[int, np.random.RandomState] | None | The random number generator. Can be `int` (a random seed), `np.random.RandomState`, or None (a new random seed will be selected randomly). |