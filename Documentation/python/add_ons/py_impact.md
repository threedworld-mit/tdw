# PyImpact

`from add_ons.py_impact import PyImpact`

Generate impact sounds from physics data.

Sounds are synthesized as described in: [Traer,Cusimano and McDermott, A PERCEPTUALLY INSPIRED GENERATIVE MODEL OF RIGID-BODY CONTACT SOUNDS, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf)

Sounds can be synthesized automatically (for general use-cases) or manually (for advanced use-cases).

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a",
                                       position={"x": 1, "y": 1.6, "z": -2},
                                       look_at={"x": 0, "y": 0.5, "z": 0}))
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=c.get_unique_id()))
audio_initializer = AudioInitializer(avatar_id="a")
py_impact = PyImpact()
c.add_ons.extend([audio_initializer, py_impact])
c.communicate(commands)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `SILENCE_50MS` | AudioSegment | 50ms of silence. Used for scrapes. |
| `SCRAPE_MAX_VELOCITY` | float | The maximum velocity allowed for a scrape. |
| `SCRAPE_M_PER_PIXEL` | float | Meters per pixel on the scrape surface. |
| `DEFAULT_AMP` | float | The default amp value for objects. |
| `DEFAULT_MATERIAL` | AudioMaterial | The default [material](../physics_audio/audio_material.md) for objects. |
| `DEFAULT_RESONANCE` | float | The default resonance value for objects. |
| `DEFAULT_SIZE` | int | The default audio size "bucket" for objects. |
| `ROBOT_JOINT_BOUNCINESS` | float | The assumed bounciness value for robot joints. |
| `ROBOT_JOINT_MATERIAL` | AudioMaterial | The [material](../physics_audio/audio_material.md) used for robot joints. |
| `FLOOR_AMP` | float | The amp value for the floor. |
| `FLOOR_SIZE` | int | The size "bucket" for the floor. |
| `FLOOR_MASS` | int | The mass of the floor. |

***

## Fields

- `rng` The random number generator.

- `initial_amp` The initial amplitude, i.e. the "master volume". Must be > 0 and < 1.

- `prevent_distortion` If True, clamp amp values to <= 0.99

- `logging` If True, log mode properties for all colliding objects, as json.

- `object_modes` The collision info per set of objects.

- `resonance_audio` If True, the simulation is using Resonance Audio.

- `floor` The floor material.

- `material_data` Cached material data.

- `scrape_surface_data` Cached scrape surface data.

- `_scrape_objects` A dictionary of all [scrape models](../physics_audio/scrape_model.md) in the scene. If `scrape == False`, this dictionary is empty. Key = Object ID.

- `mode_properties_log` The mode properties log.

- `auto` If True, PyImpact will evalulate the simulation state per `communicate()` call and automatically generate audio.

- `collision_events` Collision events on this frame. Key = Object ID. Value = [`CollisionAudioEvent`](../physics_audio/collision_audio_event.md).

***

## Functions

#### \_\_init\_\_

**`PyImpact()`**

**`PyImpact(initial_amp=0.5, prevent_distortion=True, logging=False, static_audio_data_overrides=None, resonance_audio=False, floor=AudioMaterial.wood_medium, rng=None, auto=True, scrape=True, scrape_objects=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| initial_amp |  float  | 0.5 | The initial amplitude, i.e. the "master volume". Must be > 0 and < 1. |
| prevent_distortion |  bool  | True | If True, clamp amp values to <= 0.99 |
| logging |  bool  | False | If True, log mode properties for all colliding objects, as json. |
| static_audio_data_overrides |  Dict[int, ObjectAudioStatic] | None | If not None, a dictionary of audio data. Key = Object ID; Value = [`ObjectAudioStatic`](../physics_audio/object_audio_static.md). These audio values will be applied to these objects instead of default values. |
| resonance_audio |  bool  | False | If True, the simulation is using Resonance Audio. |
| floor |  AudioMaterial  | AudioMaterial.wood_medium | The floor material. |
| rng |  np.random.RandomState  | None | The random number generator. If None, a random number generator with a random seed is created. |
| auto |  bool  | True | If True, PyImpact will evalulate the simulation state per `communicate()` call and automatically generate audio. |
| scrape |  bool  | True | If True, initialize certain objects as scrape surfaces: Change their visual material(s) and enable them for scrape audio. See: `tdw.physics_audio.scrape_model.DEFAULT_SCRAPE_MODELS` |
| scrape_objects |  Dict[int, ScrapeModel] | None | If `scrape == True` and this is not None, this dictionary can be used to manually set scrape surfaces. Key = Object ID. Value = [`ScrapeModel`](../physics_audio/scrape_model.md). |

#### get_initialization_commands

**`self.get_initialization_commands()`**

_Returns:_  The name of the floor material.

#### on_send

**`self.on_send()`**

_Returns:_  The name of the floor material.

#### get_impact_sound

**`self.get_impact_sound(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_normals, primary_mass, secondary_mass)`**

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

**`self.get_impact_sound_command(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_points, contact_normals, primary_mass, secondary_mass)`**

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
| contact_points |  List[np.array] |  | The collision contact points. |
| contact_normals |  List[np.array] |  | The collision contact normals. |
| primary_mass |  float |  | The mass of the primary (target) object. |
| secondary_mass |  float |  | The mass of the secondary (target) object. |

_Returns:_  A `play_audio_data` or `play_point_source_data` command that can be sent to the build via `Controller.communicate()`.

#### get_scrape_sound_command

**`self.get_scrape_sound_command(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_points, contact_normals, primary_mass, secondary_mass, scrape_material)`**


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
| contact_points |  np.array |  | The collision contact points. |
| contact_normals |  List[np.array] |  | The collision contact normals. |
| primary_mass |  float |  | The mass of the primary (target) object. |
| secondary_mass |  float |  | The mass of the secondary (target) object. |
| scrape_material |  ScrapeMaterial |  | The [scrape material](../physics_audio/scrape_material.md). |

_Returns:_  A command to play a scrape sound.

#### get_scrape_sound

**`self.get_scrape_sound(primary_id, primary_material, secondary_id, secondary_material, primary_amp, secondary_amp, resonance, velocity, contact_normals, primary_mass, secondary_mass, scrape_material)`**

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
| scrape_material |  ScrapeMaterial |  | The [scrape material](../physics_audio/scrape_material.md). |

_Returns:_  A [`Base64Sound`](../physics_audio/base64_sound.md) object or None if no sound.

#### reset

**`self.reset()`**

**`self.reset(initial_amp=0.5, static_audio_data_overrides=None, scrape_objects=None)`**

Reset PyImpact. This is somewhat faster than creating a new PyImpact object per trial.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| initial_amp |  float  | 0.5 | The initial amplitude, i.e. the "master volume". Must be > 0 and < 1. |
| static_audio_data_overrides |  Dict[int, ObjectAudioStatic] | None | If not None, a dictionary of audio data. Key = Object ID; Value = [`ObjectAudioStatic`](../physics_audio/object_audio_static.md). These audio values will be applied to these objects instead of default values. |
| scrape_objects |  Dict[int, ScrapeModel] | None | A dictionary of [scrape objects](../physics_audio/scrape_model.md) in the scene. Key = Object ID. Ignored if None or `scrape == False` in the constructor. |

