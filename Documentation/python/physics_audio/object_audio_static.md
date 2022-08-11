# ObjectAudioStatic

`from tdw.physics_audio.object_audio_static import ObjectAudioStatic`

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

#### get_static_audio_data

**`self.get_static_audio_data()`**

**`self.get_static_audio_data(csv_file="")`**

Returns ObjectInfo values.
As of right now, only a few objects in the TDW model libraries are included. More will be added in time.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| csv_file |  Union[str, Path] | "" | The path to the .csv file containing the object info. By default, it will load `tdw/physics_audio/objects.csv`. If you want to make your own spreadsheet, use this file as a reference. |

_Returns:_  A list of default ObjectInfo. Key = the name of the model. Value = object info.

