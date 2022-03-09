# InteriorSceneLighting

`from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting`

Add an HDRI skybox to the scene from a curated list of skyboxes and set post-processing values.

The list of skyboxes is a subset of all of the skyboxes available in TDW. They are all *exterior* skyboxes, which means that they are suitable for *interior* scenes such as `floorplan_1a` or `mm_craftroom_2b`. Note that some interior scenes are not HDRI-compatible; see `scene_record.hdri`.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES` | Dict[str, float] | A dictionary of all of the possible HDRI skyboxes. Key = The HDRI skybox name. Value = the post exposure value. | `loads(Path(resource_filename(__name__, "interior_scene_lighting_data/hdri_skyboxes.json")).read_text())` |

***

## Fields

- `hdri_skybox` The name of the current HDRI skybox.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`InteriorSceneLighting()`**

**`InteriorSceneLighting(hdri_skybox=None, rng=None, aperture=8, focus_distance=2.5, ambient_occlusion_intensity=0.125, ambient_occlusion_thickness_modifier=3.5, shadow_strength=1)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| hdri_skybox |  str  | None | The name of the HDRI skybox. If None, a random skybox will be selected. |
| rng |  np.random.RandomState  | None | The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed. |
| aperture |  float  | 8 | The depth-of-field aperture. |
| focus_distance |  float  | 2.5 | The depth-of-field focus distance. |
| ambient_occlusion_intensity |  float  | 0.125 | The intensity (darkness) of the Ambient Occlusion effect. |
| ambient_occlusion_thickness_modifier |  float  | 3.5 | The thickness modifier for the Ambient Occlusion effect; controls "spread" of the effect out from corners. |
| shadow_strength |  float  | 1 | The shadow strength of all lights in the scene. |

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

#### reset

**`self.reset()`**

**`self.reset(hdri_skybox=None, rng=None, aperture=8, focus_distance=2.5, ambient_occlusion_intensity=0.125, ambient_occlusion_thickness_modifier=3.5, shadow_strength=1)`**

Reset the HDRI skybox. Call this when resetting a scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| hdri_skybox |  str  | None | The name of the HDRI skybox. If None, a random skybox will be selected. |
| rng |  np.random.RandomState  | None | The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed. |
| aperture |  float  | 8 | The depth-of-field aperture. |
| focus_distance |  float  | 2.5 | The depth-of-field focus distance. |
| ambient_occlusion_intensity |  float  | 0.125 | The intensity (darkness) of the Ambient Occlusion effect. |
| ambient_occlusion_thickness_modifier |  float  | 3.5 | The thickness modifier for the Ambient Occlusion effect; controls "spread" of the effect out from corners. |
| shadow_strength |  float  | 1 | The shadow strength of all lights in the scene. |