# ObjectAudioStatic

`from physics_audio.object_audio_static import ObjectAudioStatic`

Impact sound data for an object in a TDW model library.
The audio values here are just recommendations; you can apply different values if you want.

***

## Fields

- `amp` The sound amplitude.

- `material` The audio material.

- `name` The name of the object.

- `bounciness` The bounciness value for a Unity physics material.

- `resonance` The resonance value for the object.

- `size` Integer representing the size "bucket" this object belongs to (0-5).

- `object_id` The ID of the object.

***

## Functions

#### \_\_init\_\_

**`ObjectAudioStatic(name, amp, mass, material, bounciness, resonance, size, object_id)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The model name. |
| amp |  float |  | The sound amplitude. |
| mass |  float |  | The object mass. |
| material |  AudioMaterial |  | The audio material. |
| bounciness |  float |  | The bounciness value for a Unity physics material. |
| resonance |  float |  | The resonance value for the object. |
| size |  int |  | Integer representing the size "bucket" this object belongs to (0-5). |
| object_id |  int |  | The ID of the object. |

