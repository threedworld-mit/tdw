# NavMesh

`from tdw.add_ons.nav_mesh import NavMesh`

Create a NavMesh and make objects NavMeshObstacles.

Each NavMeshObstacle will be set according to the position, size, and kinematic state of the object.

This add-on requires 2 `communicate(commands)` calls to initialize.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`NavMesh()`**

**`NavMesh(exclude_objects=None, max_y=0.1, exclude_area=0.05, small_area=1, small_area_scale=1, large_area_scale=1.25, roundness_threshold=0.95)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| exclude_objects |  List[int] | None | A list of object IDs to exclude. These won't be made into NavMeshObstacles. |
| max_y |  float  | 0.1 | If an object's y positional value is greater than this, the object won't be made into a NavMeshObstacle. |
| exclude_area |  float  | 0.05 | If an object's (x, z) area is less than this, the object won't be made into a NavMeshObstacle. |
| small_area |  float  | 1 | If an object's (x, z) area is smaller than this, its NavMeshObstacle will be scaled. |
| small_area_scale |  float  | 1 | If the object has a small area (see above), its NavMeshObstacle will be scaled by this factor. |
| large_area_scale |  float  | 1.25 | If the object has a large area (see above), its NavMeshObstacle will be scaled by this factor. |
| roundness_threshold |  float  | 0.95 | If the ration of the x and z extents of the object is less than this, the NavMeshObstacle will carve a box shape. Otherwise, it will carve a capsule shape. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### get_early_initialization_commands

**`self.get_early_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

These commands are added to the list being sent on `communicate()` *before* any other commands, including those added by the user and by other add-ons.

Usually, you shouldn't override this function. It is useful for a small number of add-ons, such as loading screens, which should initialize before anything else.

_Returns:_  A list of commands that will initialize this add-on.

#### reset

**`self.reset()`**

**`self.reset(exclude_objects=None)`**

Call this to reset the add-on.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| exclude_objects |  List[int] | None | A list of object IDs to exclude. These won't be made into NavMeshObstacles. |