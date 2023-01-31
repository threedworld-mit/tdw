##### Clatter

# Manually generate audio (Clatter CLI)

So far, this documentation has covered how to *automatically* generate audio using Clatter. You may also want to *manually* generate audio. There are two basic use-cases for manually generating audio:

1. You want to use Clatter without having to use a controller or run the build. Usually, the objective is to write .wav files for future usage.
2. You want to use Clatter in TDW but without having to define objects to generate the audio.

In both cases, you can use the Clatter command-line interface (CLI) executable. This executable is not included in TDW; you must download it separately. [Download links and documentation are here.](TODO.html)

## How to use the Clatter CLI executable *without* a controller

[Read the Clatter CLI documentation.](TODO.html) By default, you *don't* need TDW to run the Clatter CLI executable. 

## How to use the Clatter CLI executable *with* a controller

If you omit the `--path` argument, the executable will write to standard out. In the context of TDW, this can be useful because you can convert the wav data into a base64 string and send it to TDW.

In this example, a [non-physics humanoid](../non_physics_humanoids/overview.md) is followed by a [`CinematicCamera`](../camera/cinematic_camera.md). Every 16 frames, there is a footstep. Because the humanoid doesn't have colliders, it can't generate audio in Clatter. However, we can generate audio manually with the Clatter CLI executable and manually play audio in TDW. This example controller assumes that we're using Windows and that `clatter.exe` is in the same directory as the controller script:

```python
from base64 import b64encode
from random import uniform
from subprocess import run, PIPE
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Transforms
from tdw.add_ons.cinematic_camera import CinematicCamera
from tdw.add_ons.audio_initializer import AudioInitializer

c = Controller()
humanoid_id = c.get_unique_id()
initial_humanoid_position = np.array([9.03, -3, -4.57])
# Initialize the camera and audio.
initial_camera_position = np.array([initial_humanoid_position[0] + -2, 1.6, initial_humanoid_position[2] + 1])
camera = CinematicCamera(position=TDWUtils.array_to_vector3(initial_camera_position),
                         look_at=humanoid_id,
                         move_speed=0.0125)
audio = AudioInitializer(avatar_id=camera.avatar_id)
c.add_ons.extend([camera, audio])
# Get the non-physics humanoid.
animation_name = "walk_forward"
humanoid_animation_command, humanoid_animation_record = c.get_add_humanoid_animation(humanoid_animation_name=animation_name,
                                                                                     library="smpl_animations.json")
# Initialize the scene and start the animation.
resp = c.communicate([c.get_add_scene(scene_name="downtown_alleys"),
                      c.get_add_humanoid(humanoid_name="woman_business_1",
                                         object_id=humanoid_id,
                                         position=TDWUtils.array_to_vector3(initial_humanoid_position)),
                      humanoid_animation_command,
                      {"$type": "play_humanoid_animation",
                       "name": animation_name,
                       "id": humanoid_id,
                       "framerate": 60},
                      {"$type": "send_humanoids",
                       "frequency": "always"},
                      {"$type": "set_screen_size",
                       "width": 512,
                       "height": 512}])
# Move the camera to follow the humanoid.
camera.move_to_object(target=humanoid_id, offset={"x": -0.7, "y": 0.5, "z": 0})
# Run the simulation loop.
frame = 0
for i in range(300):
    frame += 1
    commands = []
    if frame % humanoid_animation_record.framerate == 0:
        # Restart the animation.
        commands.append({"$type": "play_humanoid_animation",
                         "name": animation_name,
                         "id": humanoid_id})
    if frame % 16 == 0:
        foot_position = Transforms(resp[0]).get_position(0)
        foot_position[1] = -3
        # This is approximately how far the foot is from the root body.
        foot_position[2] += 0.3
        # Generate an impact sound.
        resp = run(['./clatter.exe',
                    '--primary_material', 'wood_soft_1',
                    '--primary_amp', '0.1',
                    '--primary_resonance', '0.1',
                    '--primary_mass', '64',
                    '--secondary_material', 'stone_4',
                    '--secondary_amp', '0.5',
                    '--secondary_resonance', '0.01',
                    '--secondary_mass', '100',
                    '--speed', str(round(uniform(-1.6, -1.4))),
                    '--type', 'impact'],
                   check=True,
                   stdout=PIPE)
        # Encode the sound to a base64 string.
        audio = b64encode(resp.stdout).decode('utf-8')
        # Send a command to play the audio.
        commands.append({"$type": "play_audio_data",
                         "id": frame,
                         "position": TDWUtils.array_to_vector3(foot_position),
                         "wav_data": audio,
                         "num_frames": len(resp.stdout) // 2})
    resp = c.communicate(commands)
c.communicate({"$type": "terminate"})
```

***

**This is the last document in the "Clatter" tutorial.**

[Return to the README](../../../README.md)

***

Example Controllers:

- [footsteps.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/footsteps.py) Generate footsteps audio using Clatter.

Python API:

- [`Clatter`](../../python/add_ons/clatter.md)
- [`CinematicCamera`](../../python/add_ons/cinematic_camera.md)