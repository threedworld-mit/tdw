# Base64Sound

`from tdw.physics_audio.base64_sound import Base64Sound`

This class is used only in PyImpact, which has been deprecated. See: [`Clatter`](../add_ons/clatter.md).

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
| snd |  np.ndarray |  | The sound byte array. |

#### write

**`self.write(path)`**

Write audio to disk.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  PATH |  | The path to the .wav file. |

