##### Audio

# Recording audio

[As mentioned at the start of this tutorial](overview.md), unlike all other output data in TDW, audio data can't be passed directly from the build to the controller. Audio must be recorded from with an external program. TDW includes wrapper functions to do this.

**If you want to record audio *and* video, [read this](../video/audio.md).** It's difficult to align audio recorded with one program with video recorded with another program; they should both be captured with the same program. This document describes how to record audio-only data.

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
4. Download [iShowU Audio Capture](https://support.shinywhitebox.com).
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

In this example controller, an object will fall. TDW will create audio using [`PyImpact`](py_impact.md) and record audio using `AudioUtils`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.audio_utils import AudioUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
py_impact = PyImpact()
audio = AudioInitializer(avatar_id="a")
c.add_ons.extend([audio, py_impact])
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 1, "z": -1.5},
                                       avatar_id="a"))
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

## Record audio with `PhysicsAudioRecorder`

[`PhysicsAudioRecorder`](../../python/add_ons/physics_audio_recorder.md) is an add-on that augments `AudioUtils` for generating audio clips of sounds created via [`PyImpact`](py_impact.md). This is most convenient when generating audio datasets.

So far, we've ended audio recordings and audio trials by just waiting a certain number of frames, i.e. `for i in range(200):`. It's possible to end the trial when the audio events are actually finished. `PhysicsAudioRecorder` starts recording when you call `start(path)` and automatically stops recording when no objects are moving and the TDW build isn't outputting any audio.

This example is similar to the previous example except that it uses a `PhysicsAudioRecorder`. Instead of `for i in range(200):`, we evaluate `while recoder.done:`.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
py_impact = PyImpact()
audio = AudioInitializer(avatar_id="a")
recorder = PhysicsAudioRecorder()
c.add_ons.extend([audio, py_impact, recorder])
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 1, "z": -1.5},
                                       avatar_id="a"))
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         object_id=0,
                                         position={"x": 0, "y": 2, "z": 0}))
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("physics_audio_recorder/audio.wav")
print(f"Audio will be saved to: {path}")
recorder.start(path=path)
c.communicate(commands)
while recorder.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

In some cases, audio events may continue for a long time (such as a ball that is rolling slightly). We can set the `max_frames` parameter in the `PhysicsAudioRecorder` constructor to set a maximum number of frames, after which the recording will stop.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder

c = Controller()
py_impact = PyImpact()
audio = AudioInitializer(avatar_id="a")
recorder = PhysicsAudioRecorder(max_frames=1000)
c.add_ons.extend([audio, py_impact, recorder])
```

You can optionally choose to make `PhysicsAudioRecorder` listen to audio events without actually saving .wav data by setting `record_audio=False` in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder

c = Controller()
audio = AudioInitializer(avatar_id="a")
recorder = PhysicsAudioRecorder(max_frames=1000, record_audio=False)
c.add_ons.extend([audio, recorder])
```

## "Rube Goldberg" example controller

[rube_goldberg.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/rube_goldberg.py) combines a [photorealistic environment](../photorealism/overview.md), a [physics simulation](../physx/physx.md), and PyImpact. It creates a "Rube Goldberg machine" from a set of objects that will collide when the first is struck by a ball.

Usage: `python3 rube_goldberg.py [ARGUMENTS]` 

#### Arguments

| Argument         | Type | Default | Description                                                  |
| ---------------- | ---- | ------- | ------------------------------------------------------------ |
| `--num`          | str  | 5       | Number of trials                                             |
| `--launch_build` |      |         | If included, [auto-launch the build](../core_concepts/launch_build.md). |

Scene setup, including the setup for all object components of the "Rube Goldberg machine", is handled through a json file -- `rube_goldberg_object.json` -- which defines the id number, position, rotation and scale for every object in the scene. For some objects, it also includes [non-default physics values](../physx/physics_objects.md).

Note that the `initial_amp` value is relatively low. This is because we have a large number of closely-occuring collisions resulting in a rapid series of "clustered" impact sounds, as opposed to a single object falling from a height. Using a higher value such as the 0.5 used in the example controller will definitely result in unpleasant distortion of the audio.

The controller supports the running of multiple sequential runs (trials), primarily to illustrate an important aspect of PyImpact's synthesis model -- stochastic sampling. Every call to PyImpact, the sound resonant modes will be randomly sampled and the impacts will sound slightly different. Thus, two different objects in the same scene with the same material will create similar but unique sounds, and running the same scene repeatedly will generate similar but unique sounds each time.

This controller will output two files per trial:

1. A log of the mode properties from PyImpact
2. A .wav file of the trial

***

**Next: [`PyImpact` (advanced API)](py_impact_advanced.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [minimal_audio_dataset.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/minimal_audio_dataset.py) A minimal example of how to record a physics audio dataset using `AudioInitializer`, `PyImpact`, and `PhysicsAudioRecorder`.
- [scrape.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/scrape.py) Record scrape sounds.
- [rube_goldberg.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/rube_goldberg.py)

Python API:

- [`AudioUtils`](../../python/audio_utils.md)
- [`PhysicsAudioRecorder`](../../python/add_ons/physics_audio_recorder.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`PyImpact`](../../python/add_ons/py_impact.md)
