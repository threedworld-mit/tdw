##### Audio

# Recording audio

*To learn how to record physically-derived audio using Clatter, [read this.](../clatter/record_audio.md)*

*If you want to record audio AND video, [read this](../video/audio.md). It's difficult to align audio recorded with one program with video recorded with another program; they should both be captured with the same program. This document describes how to record audio-only data.*

[As mentioned at the start of this tutorial](overview.md), unlike all other output data in TDW, audio data can't be passed directly from the build to the controller. Audio must be recorded from with an external program. TDW includes wrapper functions to do this.

## Requirements

- [See audio playback requirements.](initialize_audio.md)
- The controller and build must be on the same computer.
- [fmedia](https://stsaz.github.io/fmedia/) See below for how to install.
- Your audio drivers must be set up to allow for recording off of the system. To check if you have the correct audio device, run this program; if it raises an exception, you don't have an appropriate audio device:
  
  ```python
  from tdw.audio_utils import AudioUtils
  AudioUtils.get_system_audio_device()
  ```
  
    - *Windows and Linux:* The correct audio device is "Stereo Mix"; if your computer doesn't have this audio device,  upgrade or replace your audio drivers; how to do this will vary greatly by operating system and hardware.
  
    - *OS X:* The correct audio device is "iShowU Audio Capture"; see below for how to install it. 

### Install fmedia

#### Windows

1. [Download fmedia.](https://stsaz.github.io/fmedia/)
2. Unpack archive to the directory of your choice.
3. Run the following command from console (cmd.exe): `"C:\Program Files\fmedia\fmedia.exe" --install`

#### OS X

1. [Download fmedia.](https://stsaz.github.io/fmedia/)
2. Unpack archive to the directory of your choice.
3. [Add the location of the fmedia directory to the $PATH variable.](https://www.architectryan.com/2012/10/02/add-to-the-path-on-mac-os-x-mountain-lion/)
4. Download [iShowU Audio Capture](https://support.shinywhitebox.com) or [BlackHole](https://github.com/ExistentialAudio/BlackHole).
5. Go to “Audio MIDI Setup” on your Mac and create a new device with multiple output channels that should include the “iShowU Audio Capture” and the usual device that you use for audio output in your computer.

#### Linux

1. [Download fmedia](https://stsaz.github.io/fmedia/)
2. Unpack archive to the directory of your choice:  `tar Jxf ./fmedia-1.0-linux-amd64.tar.xz -C /usr/local`  
3. Create a symbolic link: `ln -s /usr/local/fmedia-1/fmedia /usr/local/bin/fmedia`


## Record audio with `AudioUtils`

[`AudioUtils`](../../python/audio_utils.md) is a wrapper class for controlling fmedia audio recording.

- `AudioUtils.start(path, until)` Start recording. `path` is the path to the output .wav file. `until` is an optional parameter; if not None, it should be an (int, int) tuple where the first element is minutes and the second element is seconds. `until=(0, 10)` means that `AudioUtils` will stop recording after 10 seconds.
- `AudioUtils.stop()` Stop an ongoing recording.
- `AudioUtils.is_recording()` Returns True if the fmedia process is running.

In this example controller, an object will fall. TDW will create audio using [`Clatter`](../clatter/overivew.md) and record audio using `AudioUtils` (the Clatter documentation includes a somewhat more sophisticated example, using a [`PhysicsAudioRecorder`](../clatter/record_audio.md)).

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.audio_utils import AudioUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.clatter import Clatter
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
camera = ThirdPersonCamera(position={"x": 0, "y": 1, "z": -1.5}, avatar_id="a")
clatter = Clatter()
audio = AudioInitializer(avatar_id="a")
c.add_ons.extend([audio, camera, clatter])
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         object_id=0,
                                         position={"x": 0, "y": 2, "z": 0}))
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("audio_utils/audio.wav")
print(f"Audio will be saved to: {path}")
AudioUtils.start(output_path=path)
c.communicate(commands)
for i in range(200):
    c.communicate([])
AudioUtils.stop()
c.communicate({"$type": "terminate"})
```

## Record audio from a microphone

To record audio from a non-default audio device such as a microphone, set the `device_name` parameter in `AudioUtils.start()`:

```python
from tdw.audio_utils import AudioUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("audio_utils/audio.wav")
print(f"Audio will be saved to: {path}")
AudioUtils.start(output_path=path, device_name="Headset Microphone")
```

## Use a `PhysicsAudioRecorder`

`PhysicsAudioRecorder` is an add-on meant to be used in conjunction with Clatter that simplifies physics-driven audio recording. [Read this for more information.](../clatter/record_audio.md)

#### Arguments

***

**Next: [Audio perception](audio_perception.md)**

[Return to the README](../../../README.md)

Python API:

- [`AudioUtils`](../../python/audio_utils.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`Clatter`](../../python/add_ons/clatter.md)
