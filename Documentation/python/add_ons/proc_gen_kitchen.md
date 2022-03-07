# ProcGenKitchen

`from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen`

TODO

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `TALL_CATEGORIES` | List[str] | Categories of models that are tall and might obscure windows. |
| `SECONDARY_CATEGORIES` | Dict[str, Dict[str, int]] | Categories of "secondary objects". |

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `rng` The random number generator

- `room` The kitchen [`Room`](../scene_data/room.md).

- `cabinetry` The [`KitchenCabinetSet`](../proc_gen/kitchen_cabinets/kitchen_cabinet_set.md). This is set randomly.

***

## Functions

#### \_\_init\_\_

**`ProcGenKitchen(scene)`**

**`ProcGenKitchen(scene, create_scene=True, room_index=0, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| scene |  Union[str, SceneRecord, Room] |  | The scene. Can be `str` (the name of the scene), [`SceneRecord`](../../python/librarian/scene_librarian.md), [`Room`](../scene_data/room.md). The scene must at least one room; see `SceneRecord.rooms`. |
| create_scene |  bool  | True | If True, create the scene as part of the scene setup (assuming that `scene` is `str` or `SceneRecord`). |
| room_index |  int  | 0 | The index of the room in `SceneRecord.rooms`. If `scene` is type `Room`, this parameter is ignored. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed, a random number generator, or None. If None, a new random number generator is created. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(scene, create_scene, room_index, rng)`**

Reset the add-on. Call this when you reset a scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| scene |  |  | The scene. Can be `str` (the name of the scene), [`SceneRecord`](../../python/librarian/scene_librarian.md), or [`Room`](../scene_data/room.md). The scene must at least one room; see `SceneRecord.rooms`. |
| create_scene |  |  | If True, create the scene as part of the scene setup (assuming that `scene` is `str` or `SceneRecord`). |
| room_index |  |  | The index of the room in `SceneRecord.rooms`. If `scene` is type `Room`, this parameter is ignored. |
| rng |  |  | Either a random seed, a random number generator, or None. If None, a new random number generator is created. |

#### reset

**`self.reset(scene)`**

**`self.reset(scene, create_scene=True, room_index=0, rng=None)`**

Reset the add-on. Call this when you reset a scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| scene |  Union[str, SceneRecord, Room] |  | The scene. Can be `str` (the name of the scene), [`SceneRecord`](../../python/librarian/scene_librarian.md), or [`Room`](../scene_data/room.md). The scene must at least one room; see `SceneRecord.rooms`. |
| create_scene |  bool  | True | If True, create the scene as part of the scene setup (assuming that `scene` is `str` or `SceneRecord`). |
| room_index |  int  | 0 | The index of the room in `SceneRecord.rooms`. If `scene` is type `Room`, this parameter is ignored. |
| rng |  Union[int, np.random.RandomState] | None | Either a random seed, a random number generator, or None. If None, a new random number generator is created. |

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



