##### Audio

# Initialize audio and play .wav files

## Setup for playing audio

Most personal computers are already set up to play audio. If you can listen to music on your computer, you'll be able to play audio in TDW.

On a Linux server, you need to install:

- `pulseaudio`
- `socat`
- `alsa-utils`

[This Docker file](https://github.com/threedworld-mit/tdw/blob/master/Docker/Dockerfile_audio) creates a container that can play audio.

## Initialize audio in a controller

In order to initialize audio in TDW, you must:

1. [Initialize the scene](../core_concepts/scenes.md)
2. [Add an avatar](../core_concepts/avatars.md)
3. Add an **audio sensor** to the avatar

The final step can be simplified with the [`AudioInitializer` add-on](../../python/add_ons/audio_initializer.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer

c = Controller()
audio_initializer = AudioInitializer(avatar_id="a", framerate=60)
c.add_ons.append(audio_initializer)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a"))
c.communicate(commands)
```

You can do the exact same thing with a [`ThirdPersonCamera` add-on](../../python/add_ons/third_person_camera.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
audio_initializer = AudioInitializer(avatar_id="a", framerate=60)
camera = ThirdPersonCamera(avatar_id="a")
# Note the order: The camera must be added before audio is initialized.
c.add_ons.extend([camera, audio_initializer])
c.communicate(TDWUtils.create_empty_room(12, 12))
```

Or you can set up audio with low-level commands:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
camera = ThirdPersonCamera(avatar_id="a")
c.add_ons.append(camera)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend([{"$type": "set_target_framerate", 
                  "framerate": 60}, 
                 {"$type": "add_audio_sensor",
                  "avatar_id": "a"}])
c.communicate(commands)
```

## Target framerate

The *target framerate* in TDW is by default 1000 frames (`communicate()` calls) per second. The build will rarely, if ever, reach this target.

If the build is running too fast, the physics can outpace the audio, resulting in the audio layering on itself in strange ways.

In video games, a much lower target framerate is used because the goal is to ensure a steady rate of time, rather than the fastest possible rate.

By setting the target framerate to 60, the audio rate will match the physics and render rate.

## Re-initialize audio

To reset, destroy the avatar and set `audio_intializer.initialized = False`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer

c = Controller()
audio_initializer = AudioInitializer(avatar_id="a", framerate=60)
c.add_ons.append(audio_initializer)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a"))
c.communicate(commands)

c.communicate({"$type": "destroy_avatar",
               "avatar_id": "a"})
audio_initializer.initialized = False
c.communicate(commands)
```

## Play audio

You can call `audio_intializer.play(path, position)` to play a .wav file. 

- `path` is the path to the .wav file
- `position` is the position of the audio source. 
- You can optionally set the parameter `audio_id` to an integer. Each audio source has a unique ID. If you don't set this parameter, a unique ID will be generated.
- You can optionally set the parameter `object_id`. If you do, the audio source will be parented to the corresponding object such that whenever the object moves, the source will move with it. Internally, this is handled with via the command [`parent_audio_source_to_object`](../../api/command_api.md#parent_audio_source_to_object).

This `play()` function loads the .wav file and converts it into a useable byte array. It then tells the build to play the audio by sending [`play_audio_data`](../../api/command_api.md#play_audio_data).

This controller will create a scene and initialize audio. It will then play two audio clips for ten seconds before quitting. The audio clips can be found [here](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio).

```python
from time import sleep
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer

c = Controller()
object_id_0 = c.get_unique_id()
object_id_1 = c.get_unique_id()
object_position_0 = {"x": 3.16, "y": 0, "z": 4.34}
object_position_1 = {"x": -2.13, "y": 0, "z": -1.0}
# Add a camera.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": -4, "y": 1.5, "z": 0},
                           look_at={"x": 2.5, "y": 0, "z": 0})
# Initialize audio.
audio_initializer = AudioInitializer(avatar_id="a")
c.add_ons.extend([camera, audio_initializer])
# Create the scene.
c.communicate([c.get_add_scene("tdw_room"),
               c.get_add_object(model_name="satiro_sculpture",
                                object_id=object_id_0,
                                position=object_position_0,
                                rotation={"x": 0.0, "y": -108.0, "z": 0.0}),
               c.get_add_object(model_name="buddah",
                                object_id=object_id_1,
                                position={"x": -2.13, "y": 0, "z": -1.0},
                                rotation={"x": 0.0, "y": 90, "z": 0.0})])
# Start playing audio on both objects once they are created.
audio_initializer.play(path="HWL_1b.wav", position=object_position_0)
c.communicate({"$type": "set_field_of_view",
               "avatar_id": "a",
               "field_of_view": 75.0})
sleep(10)
c.communicate({"$type": "terminate"})
```

## Audio systems and spatialization

TDW includes two audio systems:

1. Unity's built-in audio system (which has been covered in this tutorial). This system supports basic audio spatialization.
2. [Resonance Audio](resonance_audio.md), which can produce physics-based reverb effects for interior environments. Resonance Audio has far more sophisticated audio spatialization than the built-in audio system.

***

**Next: [Resonance Audio](resonance_audio.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [audio.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/audio.py) Initialize and play audio.

Python API:

- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)

Command API:

- [`play_audio_data`](../../api/command_api.md#play_audio_data)
- [`add_audio_sensor`](../../api/command_api.md#add_audio_sensor)
- [`parent_audio_source_to_object`](../../api/command_api.md#parent_audio_source_to_object)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)
- [`destroy_avatar`](../../api/command_api.md#destroy_avatar)
- [`set_field_of_view`](../../api/command_api.md#set_field_of_view)