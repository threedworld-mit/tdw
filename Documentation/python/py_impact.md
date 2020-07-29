# `py_impact.py`

## `PyImpact`

`from tdw.py_impact import PyImpact`

Generate impact sounds from physics data.

Sounds are synthesized as described in: [Traer,Cusimano and McDermott, A PERCEPTUALLY INSPIRED GENERATIVE MODEL OF RIGID-BODY CONTACT SOUNDS, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf)

For a general guide on impact sounds in TDW, read [this](../misc_frontend/impact_sounds.md).

Usage:

```python
from tdw.controller import Controller
from tdw.py_impact import PyImpact

p = PyImpact()
c = Controller()
c.start()

# Your code here.

c.communicate(p.get_impact_sound_command(arg1, arg2, ... ))
```

***

#### `__init__(self, initial_amp: float = 0.5, prevent_distortion: bool = True)`


| Parameter | Description |
| --- | --- |
| initial_amp | The initial amplitude, i.e. the "master volume". Must be > 0 and < 1. |
| prevent_distortion | If True, clamp amp values to <= 0.99 |

***

#### `get_sound(self, collision: Union[Collision, EnvironmentCollision], rigidbodies: Rigidbodies, id1: int, mat1: str, id2: int, mat2: str, amp2re1: float) -> Optional[Base64Sound]`

Produce sound of two colliding objects as a byte array.

| Parameter | Description |
| --- | --- |
| collision | TDW `Collision` or `EnvironmentCollision` output data. |
| rigidbodies | TDW `Rigidbodies` output data. |
| id1 | The object ID for one of the colliding objects. |
| mat1 | The material label for one of the colliding objects. |
| id2 | The object ID for the other object. |
| mat2 | The material label for the other object. |
| amp2re1 | The sound amplitude of object 2 relative to that of object 1. |

_Returns:_ Sound data as a Base64Sound object.

***

#### `get_impact_sound_command(self, collision: Union[Collision, EnvironmentCollision], rigidbodies: Rigidbodies, target_id: int, target_mat: str, target_amp: float, other_id: int, other_mat: str, other_amp: float, play_audio_data: bool = True) -> dict`

Create an impact sound, and return a valid command to play audio data in TDW.
"target" should usually be the smaller object, which will play the sound.
"other" should be the larger (stationary) object.

| Parameter | Description |
| --- | --- |
| collision | TDW `Collision` or `EnvironmentCollision` output data. |
| target_amp | The target's amp value. |
| target_mat | The target's audio material. |
| other_amp | The other object's amp value. |
| other_id | The other object's ID. |
| other_mat | The other object's audio material. |
| rigidbodies | TDW `Rigidbodies` output data. |
| target_id | The ID of the object that will play the sound. |
| play_audio_data | If True, return a `play_audio_data` command. If False, return a `play_point_source_data` command (useful only with Resonance Audio; see Command API). |

_Returns:_ A `play_audio_data` or `play_point_source_data` command that can be sent to the build via `Controller.communicate()`.

***

#### `make_impact_audio(self, amp2re1: float, mass: float, id1: int, id2: int, mat1: str = 'cardboard', mat2: str = 'cardboard') -> (np.array, Modes, Modes)`

Generate an impact sound.

| Parameter | Description |
| --- | --- |
| mat1 | The material label for one of the colliding objects. |
| mat2 | The material label for the other object. |
| amp2re1 | The sound amplitude of object 2 relative to that of object 1. |
| mass | The mass of the smaller of the two colliding objects. |
| id1 | The ID for the one of the colliding objects. |
| id2 | The ID for the other object. |

_Returns:_ The sound, and the object modes.

***

#### `synth_impact_modes(modes1: Modes, modes2: Modes, mass: float) -> np.array`

_This is a static function._

Generate an impact sound from specified modes for two objects, and the mass of the smaller object.

| Parameter | Description |
| --- | --- |
| modes1 | Modes of object 1. A numpy array with: column1=mode frequencies (Hz); column2=mode onset powers in dB; column3=mode RT60s in milliseconds; |
| modes2 | Modes of object 2. Formatted as modes1/modes2. |
| mass | the mass of the smaller of the two colliding objects. |

_Returns:_ The impact sound.

***

#### `get_object_info(csv_file: Union[str, Path] = "") -> Dict[str, ObjectInfo]`

_This is a static function._

Returns ObjectInfo values.
As of right now, only a few objects in the TDW model libraries are included. More will be added in time.

| Parameter | Description |
| --- | --- |
| csv_file | The path to the .csv file containing the object info. By default, it will load `tdw/py_impact/objects.csv`. If you want to make your own spreadsheet, use this file as a reference. |

_Returns:_  A list of default ObjectInfo. Key = the name of the model. Value = object info.

***

#### `get_collisions(resp: List[bytes]) -> Tuple[List[Collision], List[EnvironmentCollision], Optional[Rigidbodies]]`

_This is a static function._

Parse collision and rigibody data from the output data.

| Parameter | Description |
| --- | --- |
| resp | The response from the build. |

_Returns:_  A list of collisions on this frame (can be empty), a list of environment collisions on this frame (can be empty), and Rigidbodies data (can be `None`).

***

#### `is_valid_collision(collision: Union[Optional[Collision], Optional[EnvironmentCollision]]) -> bool`

_This is a static function._


| Parameter | Description |
| --- | --- |
| collision | Collision or EnvironmentCollision output data from the build. |

_Returns:_  True if this collision can be used to generate an impact sound.

***

#### `reset(self, initial_amp: float = 0.5) -> None`

Reset PyImpact. This is somewhat faster than creating a new PyImpact object per trial.

| Parameter | Description |
| --- | --- |
| initial_amp | The initial amplitude, i.e. the "master volume". Must be > 0 and < 1. |

***

## `AudioMaterial(Enum)`

`from tdw.py_impact import AudioMaterial`

These are the materials currently supported for impact sounds in pyImpact.  More will be added in time.

Enum values:

- `ceramic`
- `glass`
- `metal`
- `hardwood`
- `wood`
- `cardboard`

***

## `ObjectInfo`

`from tdw.py_impact import ObjectInfo`

Impact sound data for an object in a TDW model library.
The audio values here are just recommendations; you can apply different values if you want.

***

#### `__init__(self, name: str, amp: float, mass: float, material: AudioMaterial, library: str, bounciness: float)`


| Parameter | Description |
| --- | --- |
| name | The model name. |
| amp | The sound amplitude. |
| mass | The object mass. |
| material | The audio material. |
| library | The path to the model library (see ModelLibrarian documentation). |
| bounciness | The bounciness value for a Unity physics material. |

***

## `Base64Sound`

`from tdw.py_impact import Base64Sound`

A sound encoded as a base64 string.

***

#### `__init__(self, snd: np.array)`


| Parameter | Description |
| --- | --- |
| snd | The sound byte array. |

***

## `Modes`

`from tdw.py_impact import Modes`

Resonant mode properties: Frequencies, powers, and times.

***

#### `__init__(self, frequencies: np.array, powers: np.array, decay_times: np.array)`


| Parameter | Description |
| --- | --- |
| frequencies | numpy array of mode frequencies in Hz |
| powers | numpy array of mode onset powers in dB re 1. |
| decay_times | numpy array of mode decay times (i.e. the time in ms it takes for each mode to decay 60dB from its onset power) |

***

#### `sum_modes(self, fs: int = 44100) -> np.array`

Create mode time-series from mode properties and sum them together.

_Returns:_ A synthesized sound.

***

#### `mode_add(a: np.array, b: np.array) -> np.array`

_This is a static function._

Add together numpy arrays of different lengths by zero-padding the shorter.

| Parameter | Description |
| --- | --- |
| a | The first array. |
| b | The second array. |

_Returns:_ The summed modes.

***

## `CollisionInfo`

`from tdw.py_impact import CollisionInfo`

Class containing information about collisions required by pyImpact to determine the volume of impact sounds.

***

#### `__init__(self, obj1_modes: Modes, obj2_modes: Modes, amp: float = 0.5, init_speed: float = 1)`


| Parameter | Description |
| --- | --- |
| amp | Amplitude of the first collision (must be between 0 and 1). |
| init_speed | The speed of the initial collision (all collisions will be scaled relative to this). |
| obj1_modes | The object's modes. |
| obj2_modes | The other object's modes. |

***

#### `count_collisions(self) -> None`

Update the counter for how many times two objects have collided.

***

## `CollisionType(Enum)`

`from tdw.py_impact import CollisionType`

The "type" of a collision, defined by the motion of the object.

none = No collision
impact = The object "entered" a collision
scrape = The object "stayed" in a collision with a low angular velocity.
roll = The object "stayed" in a collision with a high angular velocity.

Enum values:

- `none`
- `impact`
- `scrape`
- `roll`

***

## `CollisionTypesOnFrame`

`from tdw.py_impact import CollisionTypesOnFrame`

All types of collision (impact, scrape, roll, none) between an object and any other objects or the environment on this frame.

Usage:

```python
from tdw.controller import Controller
from tdw.py_impact import CollisionTypesOnFrame

object_id = c.get_unique_id()
c = Controller()
c.start()

# Your code here.

# Request the required output data (do this at the start of the simulation, not per frame).
resp = c.communicate([{"$type": "send_collisions",
"enter": True,
"exit": False,
"stay": True,
"collision_types": ["obj", "env"]},
{"$type": "send_rigidbodies",
"frequency": "always"}])

# Parse the output data and get collision type data.
ctof = CollisionTypesOnFrame(object_id, resp)

# Read the dictionaries of collidee IDs and collision types.
for collidee_id in ctof.collisions:
collision_type = ctof.collisions[collidee_id]
print(collidee_id, collision_type)

# Check the environment collision.
print(ctof.env_collision_type)
```

***

#### `__init__(self, object_id: int, resp: List[bytes])`


| Parameter | Description |
| --- | --- |
| object_id | The unique ID of the colliding object. |
| resp | The response from the build. |

***

