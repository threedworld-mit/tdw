# PyImpact

`from tdw.add_ons.py_impact import PyImpact`

Generate impact sounds from physics data.

Sounds are synthesized as described in: [Traer,Cusimano and McDermott, A PERCEPTUALLY INSPIRED GENERATIVE MODEL OF RIGID-BODY CONTACT SOUNDS, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf)

For a general guide on impact sounds in TDW, read [this](../misc_frontend/impact_sounds.md).

For example usage, see: `tdw/Python/example_controllers/impact_sounds.py`

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`PyImpact()`**

**`PyImpact(initial_amp=0.5, prevent_distortion=True, logging=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| initial_amp |  float  | 0.5 | The initial amplitude, i.e. the "master volume". Must be > 0 and < 1. |
| prevent_distortion |  bool  | True | If True, clamp amp values to <= 0.99 |
| logging |  bool  | False | If True, log mode properties for all colliding objects, as json. |

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

#### get_log

**`self.get_log()`**

_Returns:_  The mode properties log.

#### get_sound

**`self.get_sound(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_normals, primary_mass, secondary_mass)`**

Produce sound of two colliding objects as a byte array.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| primary_id |  int |  | The object ID for the primary (target) object. |
| primary_material |  str |  | The material label for the primary (target) object. |
| secondary_id |  Optional[int] |  | The object ID for the secondary (other) object. |
| secondary_material |  str |  | The material label for the secondary (other) object. |
| primary_amp |  float |  | Sound amplitude of primary (target) object. |
| secondary_amp |  float |  | Sound amplitude of the secondary (other) object. |
| resonance |  float |  | The resonances of the objects. |
| velocity |  np.array |  | The velocity. |
| contact_normals |  List[np.array] |  | The collision contact normals. |
| primary_mass |  float |  | The mass of the primary (target) object. |
| secondary_mass |  float |  | The mass of the secondary (target) object. |

_Returns:_  Sound data as a Base64Sound object.

#### get_impact_sound_command

**`self.get_impact_sound_command(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_normals, primary_mass, secondary_mass)`**

Create an impact sound, and return a valid command to play audio data in TDW.
"target" should usually be the smaller object, which will play the sound.
"other" should be the larger (stationary) object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| primary_id |  int |  | The object ID for the primary (target) object. |
| primary_material |  str |  | The material label for the primary (target) object. |
| secondary_id |  Optional[int] |  | The object ID for the secondary (other) object. |
| secondary_material |  str |  | The material label for the secondary (other) object. |
| primary_amp |  float |  | Sound amplitude of primary (target) object. |
| secondary_amp |  float |  | Sound amplitude of the secondary (other) object. |
| resonance |  float |  | The resonances of the objects. |
| velocity |  np.array |  | The velocity. |
| contact_normals |  List[np.array] |  | The collision contact normals. |
| primary_mass |  float |  | The mass of the primary (target) object. |
| secondary_mass |  float |  | The mass of the secondary (target) object. |

_Returns:_  A `play_audio_data` or `play_point_source_data` command that can be sent to the build via `Controller.communicate()`.

#### make_impact_audio

**`self.make_impact_audio(amp2re1, mass, id1, id2, resonance)`**

**`self.make_impact_audio(mat1='cardboard', mat2='cardboard', amp2re1, mass, id1, id2, resonance)`**

Generate an impact sound.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| mat1 |  str  | 'cardboard' | The material label for one of the colliding objects. |
| mat2 |  str  | 'cardboard' | The material label for the other object. |
| amp2re1 |  float |  | The sound amplitude of object 2 relative to that of object 1. |
| mass |  float |  | The mass of the smaller of the two colliding objects. |
| id1 |  int |  | The ID for the one of the colliding objects. |
| id2 |  int |  | The ID for the other object. |
| resonance |  float |  | The resonance of the objects. |

_Returns:_  The sound, and the object modes.

#### get_impulse_response

**`self.get_impulse_response(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_normals, primary_mass, secondary_mass)`**

Generate an impulse response from the modes for two specified objects.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| primary_id |  int |  | The object ID for the primary (target) object. |
| primary_material |  str |  | The material label for the primary (target) object. |
| secondary_id |  int |  | The object ID for the secondary (other) object. |
| secondary_material |  str |  | The material label for the secondary (other) object. |
| primary_amp |  float |  | Sound amplitude of primary (target) object. |
| secondary_amp |  float |  | Sound amplitude of the secondary (other) object. |
| resonance |  float |  | The resonances of the objects. |
| velocity |  np.array |  | The velocity. |
| contact_normals |  List[np.array] |  | The collision contact normals. |
| primary_mass |  float |  | The mass of the primary (target) object. |
| secondary_mass |  float |  | The mass of the secondary (target) object. |

_Returns:_  The impulse response.

#### get_scrape_sound_command

**`self.get_scrape_sound_command(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_normals, primary_mass, secondary_mass)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| primary_id |  int |  | The object ID for the primary (target) object. |
| primary_material |  str |  | The material label for the primary (target) object. |
| secondary_id |  Optional[int] |  | The object ID for the secondary (other) object. |
| secondary_material |  str |  | The material label for the secondary (other) object. |
| primary_amp |  float |  | Sound amplitude of primary (target) object. |
| secondary_amp |  float |  | Sound amplitude of the secondary (other) object. |
| resonance |  float |  | The resonances of the objects. |
| velocity |  np.array |  | The velocity. |
| contact_normals |  List[np.array] |  | The collision contact normals. |
| primary_mass |  float |  | The mass of the primary (target) object. |
| secondary_mass |  float |  | The mass of the secondary (target) object. |

_Returns:_  A command to play a scrape sound.

#### get_scrape_sound

**`self.get_scrape_sound(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_normals, primary_mass, secondary_mass)`**

Create a scrape sound, and return a valid command to play audio data in TDW.
"target" should usually be the smaller object, which will play the sound.
"other" should be the larger (stationary) object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| primary_id |  int |  | The object ID for the primary (target) object. |
| primary_material |  str |  | The material label for the primary (target) object. |
| secondary_id |  int |  | The object ID for the secondary (other) object. |
| secondary_material |  str |  | The material label for the secondary (other) object. |
| primary_amp |  float |  | Sound amplitude of primary (target) object. |
| secondary_amp |  float |  | Sound amplitude of the secondary (other) object. |
| resonance |  float |  | The resonances of the objects. |
| velocity |  np.array |  | The velocity. |
| contact_normals |  List[np.array] |  | The collision contact normals. |
| primary_mass |  float |  | The mass of the primary (target) object. |
| secondary_mass |  float |  | The mass of the secondary (target) object. |

_Returns:_  A [`Base64Sound`](../physics_audio/base64_sound.md) object or None if no sound.

#### synth_impact_modes

**`PyImpact(AddOn).synth_impact_modes(modes1, modes2, mass, resonance)`**

_This is a static function._

Generate an impact sound from specified modes for two objects, and the mass of the smaller object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| modes1 |  Modes |  | Modes of object 1. A numpy array with: column1=mode frequencies (Hz); column2=mode onset powers in dB; column3=mode RT60s in milliseconds; |
| modes2 |  Modes |  | Modes of object 2. Formatted as modes1/modes2. |
| mass |  float |  | the mass of the smaller of the two colliding objects. |
| resonance |  float |  | The resonance of the objects. |

_Returns:_  The impact sound.

#### get_static_audio_data

**`PyImpact(AddOn).get_static_audio_data()`**

**`PyImpact(AddOn).get_static_audio_data(csv_file="")`**

_This is a static function._

Returns ObjectInfo values.
As of right now, only a few objects in the TDW model libraries are included. More will be added in time.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| csv_file |  Union[str, Path] | "" | The path to the .csv file containing the object info. By default, it will load `tdw/py_impact/objects.csv`. If you want to make your own spreadsheet, use this file as a reference. |

_Returns:_  A list of default ObjectInfo. Key = the name of the model. Value = object info.

#### reset

**`self.reset()`**

**`self.reset(initial_amp=0.5)`**

Reset PyImpact. This is somewhat faster than creating a new PyImpact object per trial.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| initial_amp |  float  | 0.5 | The initial amplitude, i.e. the "master volume". Must be > 0 and < 1. |

#### log_modes

**`self.log_modes(count, mode_props, id1, id2, modes_1, modes_2, amp, mat1, mat2)`**

Log mode properties info for a single collision event.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| count |  int |  | Mode count for this material-material collision. |
| mode_props |  dict |  | Dictionary to log to. |
| id1 |  int |  | ID of the "other" object. |
| id2 |  int |  | ID of the "target" object. |
| modes_1 |  Modes |  | Modes of the "other" object. |
| modes_2 |  Modes |  | Modes of the "target" object. |
| amp |  float |  | Adjusted amplitude value of collision. |
| mat1 |  str |  | Material of the "other" object. |
| mat2 |  str |  | Material of the "target" object. |

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



