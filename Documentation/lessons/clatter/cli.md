##### Clatter

# Manually generate audio

So far, this documentation has covered how to *automatically* generate audio using Clatter. You may also want to *manually* generate audio. There are two basic use-cases for manually generating audio:

1. You want to use Clatter without having to use a controller or run the build. Usually, the objective is to write .wav files for future usage.
2. You want to use Clatter in TDW but without having to define objects to generate the audio.

In either case, you have two options:

1. You can use the Clatter command-line interface (CLI) executable. This executable is not included in TDW; you must download it separately. [Download links and documentation are here.](https://alters-mit.github.io/clatter/cli_overview.html) This option is suitable for single impact events and scrape audio if the speed never changes.
2. You can import `Clatter.Core.dll` directly into your Python script. This requires more setup and insight into how Clatter works internally. [Download links and documentation are here.](https://alters-mit.github.io/clatter/) This is useful if you want to generate a series of impact events or scrape audio in which the speed changes.

## Clatter CLI

### How to use the Clatter CLI executable *without* a controller

[Read the Clatter CLI documentation.](https://alters-mit.github.io/clatter/cli_overview.html) By default, you *don't* need TDW to run the Clatter CLI executable. 

### How to use the Clatter CLI executable *with* a controller

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

## Clatter.Core.dll

To import Clatter directly into your Python script, you must first do the following:

1. [Download `Clatter.Core.dll`](https://alters-mit.github.io/clatter/). On Windows, the file might be "blocked". Right click the dll, select properties, click "Unblock", and click "OK".
2. Install pythonnet: `pip install pythonnet`
3. Copy `Clatter.Core.dll` into the same folder as your script.

You can then import C# code and use it as if it were Python code:

```python
from os.path import join
from os import getcwd
import clr

clr.AddReference(join(getcwd(), "Clatter.Core.dll"))
from Clatter.Core import ImpactMaterial

primaryMaterial = ImpactMaterial.glass_1
```

The API is exactly the same as the backend Clatter API, but it uses Python syntax instead of C# syntax. The C# syntax is very similar though:

```
ImpactMaterial primaryMaterial = ImpactMaterial.glass_1;
```

...and so you should be able to easily translate Clatter's C# examples into Python. [Read this for more information.](https://alters-mit.github.io/clatter/clatter.core_overview.html)

This example is not a TDW controller. It loads Clatter and generates audio, lerping between a sequence of two different speeds. For a similar example in C#, [read this](https://alters-mit.github.io/clatter/Scrape.html).

```python
from os.path import join
from os import getcwd
import clr
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
This script is not a controller. It is an example of how to use Clatter without TDW.

To run this script, install pythonnet: pip install pythonnet.

This folder contains the Clatter.Core.dll library. If you want to write a script based off of this one, you must copy Clatter.Core.dll as well.

On Windows, you may need to unblock the dll: Right-click the file, select Properties, click "Unblock", and press OK.
"""

clr.AddReference(join(getcwd(), "Clatter.Core.dll"))
from System import Random
from Clatter.Core import ImpactMaterial, ScrapeMaterial, ImpactMaterialData, ScrapeMaterialData, ClatterObjectData, Scrape, WavWriter

# Load the materials.
primaryMaterial = ImpactMaterial.glass_1
secondaryMaterial = ImpactMaterial.stone_4
scrapeMaterial = ScrapeMaterial.ceramic
ImpactMaterialData.Load(primaryMaterial)
ImpactMaterialData.Load(secondaryMaterial)
ScrapeMaterialData.Load(scrapeMaterial)

# Set the objects.
primary = ClatterObjectData(0, primaryMaterial, 0.2, 0.2, 1)
secondary = ClatterObjectData(1, secondaryMaterial, 0.5, 0.1, 100, scrapeMaterial)

# Initialize the scrape.
scrape = Scrape(scrapeMaterial, primary, secondary, Random())

# Define the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape_no_controller")
if not path.exists():
    path.mkdir(parents=True)
path = path.joinpath("scrape.wav")
print(f"Audio will be saved to: {path}")

# Start writing audio.
writer = WavWriter(str(path.resolve()), True)

# Define the acceleration.
a = 0.05
# Get the number of chunks per scrape.
num_events = Scrape.GetNumScrapeEvents(a)
# Define speeds.
speeds = [0, 2, 0.5, 3, 0.5]

# Generate audio.
for i in range(len(speeds) - 1):
    if speeds[i + 1] > speeds[i]:
        dv1 = speeds[i + 1] - speeds[i]
        increase = True
    else:
        dv1 = speeds[i] - speeds[i + 1]
        increase = False
    dv = 0
    while dv < dv1:
        # Accelerate.
        dv += 0.05
        v = speeds[i] + (dv if increase else -dv)
        # Generate audio.
        scrape.GetAudio(v)
        # Write to the save file.
        writer.Write(scrape.samples.ToInt16Bytes())
# Stop writing.
writer.End()
```

***

**Next: [Troubleshooting Clatter](troubleshooting.md)**

[Return to the README](../../../README.md)

***

Example Controllers:

- [footsteps.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/footsteps.py) Generate footsteps audio using Clatter.

Other Examples:

- [scrape_no_controller.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/scrape_no_controller.py) Generate scrape audio with Clatter but not with TDW.

Python API:

- [`Clatter`](../../python/add_ons/clatter.md)
- [`CinematicCamera`](../../python/add_ons/cinematic_camera.md)