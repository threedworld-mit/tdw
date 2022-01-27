# InteriorSceneLighting

`from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting`

Add an HDRI skybox to the scene from a curated list of skyboxes and set post-processing values.

The list of skyboxes is a subset of all of the skyboxes available in TDW. They are all *exterior* skyboxes, which means that they are suitable for *interior* scenes such as `floorplan_1a` or `mm_craftroom_2b`. Note that some interior scenes are not HDRI-compatible; see `scene_record.hdri`.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES` | Dict[str, float] | A dictionary of all of the possible HDRI skyboxes. Key = The HDRI skybox name. Value = the post exposure value. |

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `hdri_skybox` The name of the current HDRI skybox.

***

## Functions

#### \_\_init\_\_

**`InteriorSceneLighting()`**

**`InteriorSceneLighting(hdri_skybox=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| hdri_skybox |  str  | None | The name of the HDRI skybox. If None, a random skybox will be selected. |
| rng |  np.random.RandomState  | None | The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(hdri_skybox, rng)`**

Reset the HDRI skybox. Call this when resetting a scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| hdri_skybox |  |  | The name of the HDRI skybox. If None, a random skybox will be selected. |
| rng |  |  | The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed. |

#### reset

**`self.reset()`**

**`self.reset(hdri_skybox=None, rng=None)`**

Reset the HDRI skybox. Call this when resetting a scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| hdri_skybox |  str  | None | The name of the HDRI skybox. If None, a random skybox will be selected. |
| rng |  np.random.RandomState  | None | The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed. |

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



