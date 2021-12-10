# Base64Sound

`from tdw.physics_audio.base64_sound import Base64Sound`

A sound encoded as a base64 string.

***

## Fields

- `bytes` Byte data of the sound.

- `wav_str` A base64 string of the sound. Send this to the build.

- `length` The length of the byte array.

***

## Functions

#### \_\_init\_\_

**`Base64Sound(snd)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| snd |  np.array |  | The sound byte array. |

#### write

**`self.write(path)`**

Write audio to disk.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path] |  | The path to the .wav file. |

