# ResonanceAudioInitializer

`from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer`

Initialize Resonance Audio.

This assumes that an avatar corresponding to `avatar_id` has already been added to the scene.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `IMPACT_MATERIALS` | Dict[str, ImpactMaterial] | A dictionary. Key = A Resonance Audio material string. Value = An [`ImpactMaterial`](../physics_audio/impact_material.md). | `{k: ImpactMaterial[v] for k, v in loads(Path(resource_filename(__name__, "../physics_audio/resonance_audio_materials.json")).read_text()).items()}` |
| `RESONANCE_AUDIO_MATERIALS` | Dict[ImpactMaterial, str] | A dictionary. Key = An [`ImpactMaterial`](../physics_audio/impact_material.md). Value = A Resonance Audio material string. | `{v: k for k, v in IMPACT_MATERIALS.items()}` |

***

## Fields

- `region_id` The ID of the scene region (room) to enable reverberation in. If -1, the reverb space will encapsulate the entire scene instead of a single room.

- `floor` The floor material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)

- `ceiling` The ceiling material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)

- `front_wall` The front wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)

- `back_wall` The back wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)

- `left_wall` The left wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)

- `right_wall` The right wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)

- `avatar_id` The ID of the listening avatar.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ResonanceAudioInitializer()`**

**`ResonanceAudioInitializer(avatar_id="a", region_id=-1, floor="parquet", ceiling="acousticTile", front_wall="smoothPlaster", back_wall="smoothPlaster", left_wall="smoothPlaster", right_wall="smoothPlaster", framerate=30, physics_time_step=0.02)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | "a" | The ID of the avatar. |
| region_id |  int  | -1 | The ID of the scene region (room) to enable reverberation in. If -1, the reverb space will encapsulate the entire scene instead of a single room. |
| floor |  str  | "parquet" | The floor material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple) |
| ceiling |  str  | "acousticTile" | The ceiling material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple) |
| front_wall |  str  | "smoothPlaster" | The front wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple) |
| back_wall |  str  | "smoothPlaster" | The back wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple) |
| left_wall |  str  | "smoothPlaster" | The left wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple) |
| right_wall |  str  | "smoothPlaster" | The right wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple) |
| framerate |  int  | 30 | The target simulation framerate. |
| physics_time_step |  float  | 0.02 | The physics timestep. |

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

#### play

**`self.play(path, position)`**

**`self.play(path, position, audio_id=None, object_id=None, loop=False)`**

Load a .wav file and prepare to send a command to the build to play the audio.
The command will be sent on the next `Controller.communicate()` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path] |  | The path to a .wav file. |
| position |  Optional[POSITION] |  | The position of audio source. Can be a numpy array or x, y, z dictionary. If None, the audio is not spatialized. |
| audio_id |  int  | None | The unique ID of the audio source. If None, a random ID is generated. |
| object_id |  int  | None | If not None, parent the audio source to this object. Ignored if `position` is None. |
| loop |  bool  | False | If True, the audio will loop. |