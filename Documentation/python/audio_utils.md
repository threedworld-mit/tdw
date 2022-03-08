# AudioUtils

`from tdw.audio_utils import AudioUtils`

Utility class for recording audio in TDW using [fmedia](https://stsaz.github.io/fmedia/).

Usage:

```python
from tdw.audio_utils import AudioUtils
from tdw.controller import Controller

c = Controller()

initialize_trial()  # Your code here.

# Begin recording audio. Automatically stop recording at 10 seconds.
AudioUtils.start(output_path="path/to/file.wav", until=(0, 10))

do_trial()  # Your code here.

# Stop recording.
AudioUtils.stop()
```

***

#### get_system_audio_device

**`AudioUtils.get_system_audio_device()`**

_This is a static function._

_Returns:_  The audio device that can be used to capture system audio.

#### start

**`AudioUtils.start(output_path, until)`**

**`AudioUtils.start(output_path, until, device=None)`**

_This is a static function._

Start recording audio.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| output_path |  Union[str, Path] |  | The path to the output file. |
| until |  Optional[Tuple[int, int] |  | If not None, fmedia will record until `minutes:seconds`. The value must be a tuple of 2 integers. If None, fmedia will record until you send `AudioUtils.stop()`. |
| device |  str  | None | The name of the audio capture device. If None, defaults to `"Stereo Mix"` (Windows and Linux) or `"iShowU Audio Capture"` (OS X). |

#### stop

**`AudioUtils.stop()`**

_This is a static function._

Stop recording audio (if any fmedia process is running).

#### is_recording

**`AudioUtils.is_recording()`**

_This is a static function._

_Returns:_  True if the fmedia recording process still exists.

