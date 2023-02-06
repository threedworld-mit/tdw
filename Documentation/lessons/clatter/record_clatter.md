##### Clatter

# Recording Clatter audio with the `PhysicsAudioRecorder` add-on

*To learn how to record non-Clatter audio, [read this.](../audio/record_audio.md)*

*If you want to record audio AND video, [read this](../video/audio.md). It's difficult to align audio recorded with one program with video recorded with another program; they should both be captured with the same program. This document describes how to record audio-only data.*

Recording Clatter audio is the same as recording other sorts of audio in TDW. The difference is that TDW includes a [`PhysicsAudioRecorder`](../../python/add_ons/physics_audio_recorder.md) that simplifies one of the most common processes in recording Clatter audio: recording until objects stop moving and audio stops playing.

## Requirements

The requirements for using a `PhysicsAudioRecorder` is the same as that of TDW audio in general. [Read this for a list of requirements.](../audio/record_audio.md)

## The `PhysicsAudioRecorder` add-on

If you want to use a `PhysicsAudioRecorder`, you *don't* need to use [`AudioUtils`](../../python/audio_utils.md) because the add-on will start and stop fmedia automatically. You just need to append the add-on and tell it to record:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.clatter import Clatter
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
camera = ThirdPersonCamera(position={"x": 0, "y": 1, "z": -1.5}, avatar_id="a")
clatter = Clatter()
audio = AudioInitializer(avatar_id="a")
recorder = PhysicsAudioRecorder()
c.add_ons.extend([audio, camera, clatter, recorder])
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         object_id=0,
                                         position={"x": 0, "y": 2, "z": 0}))
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("physics_audio_recorder/audio.wav")
print(f"Audio will be saved to: {path}")
recorder.start(path=path)
c.communicate(commands)
while not recorder.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

In some cases, audio events may continue for a long time (such as a ball that is rolling slightly). We can set the `max_frames` parameter in the `PhysicsAudioRecorder` constructor to set a maximum number of frames, after which the recording will stop.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.clatter import Clatter
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder

c = Controller()
clatter = Clatter()
audio = AudioInitializer(avatar_id="a")
recorder = PhysicsAudioRecorder(max_frames=1000)
c.add_ons.extend([audio, clatter, recorder])
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

[rube_goldberg.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/rube_goldberg.py) combines a [photorealistic environment](../photorealism/overview.md), a [physics simulation](../physx/physx.md), and Clatter. It creates a "Rube Goldberg machine" from a set of objects that will collide when the first is struck by a ball.

Usage: `python3 rube_goldberg.py [ARGUMENTS]` 

#### Arguments

| Argument         | Type | Default | Description                                                  |
| ---------------- | ---- | ------- | ------------------------------------------------------------ |
| `--num`          | str  | 5       | Number of trials                                             |
| `--launch_build` |      |         | If included, [auto-launch the build](../core_concepts/launch_build.md). |

Scene setup, including the setup for all object components of the "Rube Goldberg machine", is handled through a json file -- `rube_goldberg_object.json` -- which defines the id number, position, rotation and scale for every object in the scene. For some objects, it also includes [non-default physics values](../physx/physics_objects.md).

Note that the `simulation_amp` value is relatively low. This is because we have a large number of closely-occurring collisions resulting in a rapid series of "clustered" impact sounds, as opposed to a single object falling from a height. Using a higher value such as the 0.5 used in the example controller will definitely result in unpleasant distortion of the audio.

The controller supports the running of multiple sequential runs (trials), primarily to illustrate an important aspect of Clatter's synthesis model -- stochastic sampling. In Clatter, the sound resonant modes will be randomly sampled and the impacts will sound slightly different. Thus, two different objects in the same scene with the same material will create similar but unique sounds, and running the same scene repeatedly will generate similar but unique sounds each time.

This controller will output a .wav file per trial.

## scrape.py example controller

[scrape.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/scrape.py) is an example of how to create a simple scene that will generate scrape sounds. The controller records each "trial" (defined as an object moving along a surface until it stops) as a separate .wav file.

***

**Next: [Clatter and Resonance Audio](resonance_audio.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [minimal_audio_dataset.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/minimal_audio_dataset.py) A minimal example of how to record a physics audio dataset using `AudioInitializer`, `Clatter`, and `PhysicsAudioRecorder`.
- [scrape.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/scrape.py) Record scrape sounds.
- [rube_goldberg.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/rube_goldberg.py)

Python API:

- [`PhysicsAudioRecorder`](../../python/add_ons/physics_audio_recorder.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`Clatter`](../../python/add_ons/clatter.md)
