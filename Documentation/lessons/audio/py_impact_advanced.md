##### Audio

# `PyImpact` (advanced API)

In the [previous document](py_impact.md) we discussed how to use the basic automated functionality of PyImpact. PyImpact supports a more advanced API for researchers who need more granular controls.

This document is divided into examples of how to used the PyImpact API.

NOTE: Even when manually generating sounds using PyImpact, you should still call `py_impact.reset()` between trials to clear accumulated static object data and [`Modes`](../../python/physics_audio/modes.md) data.

## Example A: Play an implausible sound

It's possible to generate "implausible" sounds by setting [`ObjectAudioStatic`](../../python/physics_audio/object_audio_static.md) that mismatches the object's [static physics values](../physx/physics_objects.md):

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.add_ons.py_impact import PyImpact
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.object_audio_static import ObjectAudioStatic
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

rng = np.random.RandomState(0)
c = Controller()
floor_visual_material = "parquet_long_horizontal_clean"
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_material(material_name=floor_visual_material),
            {"$type": "set_proc_gen_floor_material",
             "name": floor_visual_material}]
object_id = c.get_unique_id()
model_name = "vase_02"
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         object_id=object_id,
                                         position={"x": 0, "y": 2, "z": 0}))
# Set random static audio data values.
object_audio = ObjectAudioStatic(name=model_name,
                                 object_id=object_id,
                                 mass=float(rng.uniform(4, 40)),
                                 material=rng.choice([a for a in AudioMaterial]),
                                 bounciness=float(rng.uniform(0, 1)),
                                 amp=float(rng.uniform(0.1, 1)),
                                 resonance=float(rng.uniform(0.1, 1)),
                                 size=int(rng.randint(1, 6)))
# Add a listener.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 1.6, "z": -2},
                           look_at={"x": 0, "y": 0.5, "z": 0})
# Initialize audio.
audio = AudioInitializer(avatar_id="a")
# Set a non-wood floor material.
floor_material = AudioMaterial.metal
# Initialize PyImpact.
py_impact = PyImpact(initial_amp=0.9, static_audio_data_overrides={object_id: object_audio}, floor=floor_material)
# Add a recorder.
recorder = PhysicsAudioRecorder()
c.add_ons.extend([camera, audio, py_impact, recorder])
# Create the scene.
c.communicate(commands)
# Start recording.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("implausible_audio/audio.wav")
print(f"Audio will be saved to: {path}")
if not path.parent.exists():
    path.parent.mkdir(parents=True)
recorder.start(path=path)
while recorder.recording:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

## Example B: Set plausible object audio values

- Deciding what `material` to assign to an object is mostly a common-sense process.

- You can likewise guess the object's `mass`. Or, you can derive it from the object's material, density, and volume (though this assumes that the object isn't hollow):

  ```python
  from tdw.librarian import ModelLibrarian
  from tdw.physics_audio.audio_material_constants import DENSITIES
  from tdw.physics_audio.audio_material import AudioMaterial
  
  model_name = "cabinet_24_door_drawer_wood_beach_honey"
  record = ModelLibrarian().get_record(model_name)
  material = AudioMaterial.wood_medium
  density = DENSITIES[material]
  volume = record.volume
  mass = volume * density
  ```

- `size` is an integer between 0 and 5. The value is derived from the extents of the model's bounds. Get the size value by calling `PyImpact.get_size(model_record)`:

```python
from tdw.librarian import ModelLibrarian
from tdw.add_ons.py_impact import PyImpact

model_name = "cabinet_24_door_drawer_wood_beach_honey"
record = ModelLibrarian().get_record(model_name)
size = PyImpact.get_size(model=record)
print(size)  # 4
```

- Decide on a `bounciness` value that makes sense for the object; the value must be between 0 and 1.
- When setting values for the relative amplitude values of objects (`amp`), it may be helpful to consider the object's:

  - **Thickness**: Thin objects (boards, sheets, planks, hollow boxes) make more sound than thick solid blocks
  - **Material**: Hard objects (metal, glass, ceramic) make more sound than soft (foam, rubber). Cardboard is a bit of outlier because it is soft, but is also almost always really, really thin which makes it surprisingly loud.
  - **Size**: For objects of similar thickness, bigger are usually louder than smaller.
  - In PyImpact, these object amplitude values are scaled relative to the initial amplitude value passed in via `p = PyImpact(initial_amp=0.5)`. This value must be > 0 and < 1. In certain situations, such as multiple closely-packed collision events, distortion of the audio can occur if this value is set too high.
- The `resonance` values should usually be less than 1.0, and small solid objects (e.g. dominos) should have very small values i.e. around 0.15. Thin-walled objects, especially made from materials such as glass or metal, can have values slightly > 1.0 but going too high can create unnatural-sounding resonances.
- Having set values, define an `ObjectAudioStatic` object and pass it into `PyImpact`:

```python
from tdw.librarian import ModelLibrarian
from tdw.physics_audio.object_audio_static import ObjectAudioStatic
from tdw.physics_audio.audio_material_constants import DENSITIES
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.add_ons.py_impact import PyImpact

model_name = "cabinet_24_door_drawer_wood_beach_honey"
record = ModelLibrarian().get_record(model_name)
material = AudioMaterial.wood_medium
density = DENSITIES[material]
volume = record.volume
mass = volume * density
object_id = 0
o = ObjectAudioStatic(name=model_name,
                      material=material,
                      mass=mass,
                      bounciness=0.48,
                      amp=0.01,
                      size=4,
                      resonance=0.25,
                      object_id=object_id)
py_impact = PyImpact(initial_amp=0.5, static_audio_data_overrides={object_id: o})
```

## Example C: Generate impact sounds without a controller

It's possible to generate impact sound without a controller by calling `py_impact.get_impact_sound()`. This example will generate 5 audio clips and save them to disk.

Remember that you can easily look up the default audio values of an object:

```python
from tdw.physics_audio.object_audio_static import DEFAULT_OBJECT_AUDIO_STATIC_DATA

audio = DEFAULT_OBJECT_AUDIO_STATIC_DATA["vase_02"]
print(audio.material)
print(audio.mass)
print(audio.resonance)
print(audio.bounciness)
print(audio.size)
```

- `contact_normals` are normal vectors at each contact point in the collision. In the underlying Unity engine, contact normals are always in multiples of 3 (in this example, there are only 3 contact normals but there could be more).
- The *primary* object (`primary_id`, `primary_mass`, etc.) is the "collider" or "target" object. For impact sounds this is always the object with the less mass.
- The *secondary* object (`secondary_id`, `secondary_mass`, etc.) is the "collidee" or "other" object. If the primary object is colliding with the floor, `secondary_id` is None.
- The `primary_material` and `secondary_material` fields are strings rather than [`AudioMaterial`](../../python/physics_audio/audio_material.md). This is because they have a *size bucket* suffix. Sizes range from 0 to 5. Floor materials should generally be size 4 or 5. For example, if the floor is `AudioMaterial.stone` and the size is 4, then `secondary_material="stone_4"`.
- `primary_resonance` and `secondary_resonance` values correspond to the primary and secondary objects.
- The object returned by `get_impact_sound()` is a [`Base64Sound`](../../python/physics_audio/base64_sound.md), which contains the raw sound byte data and a base64 string that can be sent to the TDW build.

```python
from typing import List
import numpy as np
from tdw.add_ons.py_impact import PyImpact
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

py_impact = PyImpact()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("impact_without_controller")
if not output_directory.exists():
    output_directory.mkdir()
print(f"Audio will be saved to: {output_directory}")
contact_normals: List[np.array] = list()
for i in range(3):
    contact_normals.append(np.array([0, 1, 0]))
for i in range(5):
    sound = py_impact.get_impact_sound(velocity=np.array([0, -1.5, 0]),
                                       contact_normals=contact_normals,
                                       primary_id=0,
                                       primary_material="metal_1",
                                       primary_amp=0.2,
                                       primary_mass=1,
                                       secondary_id=None,
                                       secondary_material="stone_4",
                                       secondary_amp=0.5,
                                       secondary_mass=100,
                                       primary_resonance=0.2,
                                       secondary_resonance=0.1)
    sound.write(path=output_directory.joinpath(f"{i}.wav"))
    py_impact.reset()
```

## Example D: Generate impact sounds without an object

It is possible to generate and play impact sounds in TDW without there being an object or collision by calling `py_impact.get_impact_sound_command()`.

In this example, impact sounds will be generated near the listener. Each time there is a new impact sound, it will be 15 degrees clockwise of the previous sound. This is best experienced with headphones.

- This uses [Resonance Audio](resonance_audio.md) for spatialization.
- `contact_points` is the points of the collision. Every collision in [PhysX](../physx/physx.md) generates *n* contact points and contact normals, where *n* is a multiple of 3. PyImpact uses these points to decide where to place the audio source.
- `get_impact_sound_command()` is a wrapper for `get_impact_sound()` (see above) with the addition of `contact_points`. It creates a sound and then converts a command ([`play_audio_data`](../../api/command_api.md#play_audio_data) if using Unity's built-in audio system or [`play_point_source_data`](../../api/command_api.md#play_audio_data) if using Resonance Audio).

```python
from time import sleep
from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.audio_utils import AudioUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
# Add a camera and initialize audio.
y = 2
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": y, "z": 0})
resonance_audio_floor = "metal"
resonance_audio_wall = "brick"
resonance_audio_ceiling = "acousticTile"
audio = ResonanceAudioInitializer(avatar_id="a",
                                  floor=resonance_audio_floor,
                                  front_wall=resonance_audio_wall,
                                  back_wall=resonance_audio_wall,
                                  left_wall=resonance_audio_wall,
                                  right_wall=resonance_audio_wall,
                                  ceiling=resonance_audio_ceiling)
c.add_ons.extend([camera, audio])
# Initialize the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
# Initialize PyImpact but DON'T add it as an add-on.
py_impact_floor = ResonanceAudioInitializer.AUDIO_MATERIALS[resonance_audio_floor]
impact_sound_floor = py_impact_floor.name + "_4"
py_impact = PyImpact(initial_amp=0.9, floor=py_impact_floor, resonance_audio=True)
# Generate contact normals and set the collision velocity.
contact_normals: List[np.array] = list()
for i in range(3):
    contact_normals.append(np.array([0, 1, 0]))
velocity = np.array([0, -1.5, 0])
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("impact_with_controller/audio.wav")
print(f"Audio will be saved to: {path}")
if not path.parent.exists():
    path.parent.mkdir(parents=True)
AudioUtils.start(output_path=path)
# Add sounds in a circle around the avatar.
distance = 1.5
theta = 0
d_theta = 15
contact_radius = 0.0625
while theta < 360:
    # Get the position of the sound.
    rad = np.radians(theta)
    x = np.cos(rad) * distance
    z = np.sin(rad) * distance
    # Generate contact points around the sound's position.
    contact_points: List[np.array] = list()
    contact_angle = 0
    for i in range(3):
        r = np.radians(contact_angle)
        contact_x = np.cos(r) * contact_radius + x
        contact_z = np.sin(r) * contact_radius + z
        contact_points.append(np.array([contact_x, y, contact_z]))
    # Get a sound.
    c.communicate(py_impact.get_impact_sound_command(velocity=velocity,
                                                     contact_points=contact_points,
                                                     contact_normals=contact_normals,
                                                     primary_id=0,
                                                     primary_material="metal_1",
                                                     primary_amp=0.4,
                                                     primary_mass=4,
                                                     secondary_id=None,
                                                     secondary_material=impact_sound_floor,
                                                     secondary_amp=0.5,
                                                     secondary_mass=100,
                                                     primary_resonance=0.1,
                                                     secondary_resonance=0.2))
    sleep(0.15)
    theta += d_theta
    py_impact.reset(initial_amp=0.5)
sleep(0.15)
AudioUtils.stop()
c.communicate({"$type": "terminate"})
```

## Example E: Get the collision audio type

To get the collision events on this frame, see `py_impact.collision_events`. This is a dictionary where the key is an object ID and value is a [`CollisionAudioEvent`](../../python/physics_audio/collision_audio_event.md). The `CollisionAudioEvent` includes a [`collision_type`](../../python/physics_audio/collision_audio_type.md) which is used by PyImpact to decide whether to generate an impact, scrape, roll, or no sound.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a",
                                       position={"x": 1, "y": 1.6, "z": -2},
                                       look_at={"x": 0, "y": 0.5, "z": 0}))
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=c.get_unique_id()))
audio_initializer = AudioInitializer(avatar_id="a")
py_impact = PyImpact()
c.add_ons.extend([audio_initializer, py_impact])
c.communicate(commands)
for i in range(200):
    if len(py_impact.collision_events) > 0:
        for object_id in py_impact.collision_events:
            print(i, object_id, py_impact.collision_events[object_id].collision_type)
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Output:

```
77 15124673 CollisionAudioType.impact
78 15124673 CollisionAudioType.impact
107 15124673 CollisionAudioType.impact
108 15124673 CollisionAudioType.scrape
109 15124673 CollisionAudioType.scrape
110 15124673 CollisionAudioType.scrape
111 15124673 CollisionAudioType.scrape
112 15124673 CollisionAudioType.scrape
113 15124673 CollisionAudioType.impact
116 15124673 CollisionAudioType.scrape
```

You can also get the collision audio type *without* PyImpact by using a [`CollisionManager`](../../python/add_ons/collision_manager.md) and [`ObjectManager`](../../python/add_ons/object_manager.md).

- `object_0_dynamic` is [`Rigidbody` data](../../python/object_data/rigidbody.md) (not to be confused with [`Rigidbodies` *output data*](../../api/output_data.md#Rigidbodies); `Rigidbody` is cached dynamic data for a single object).
- `object_0_static` is [`ObjectAudioStatic` data](../../python/physics_audio/object_audio_static.md).
- `object_1_dynamic` and `object_1_static` are None if this is a collision with the floor.
- `previous_areas` is the area of each collision per primary object. If collision *state* is `"stay"` but the *current* area is significantly different from the *previous* area, then the event type is `impact`.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.collision_manager import CollisionManager
from tdw.add_ons.object_manager import ObjectManager
from tdw.physics_audio.collision_audio_event import CollisionAudioEvent
from tdw.physics_audio.collision_audio_type import CollisionAudioType
from tdw.physics_audio.object_audio_static import DEFAULT_OBJECT_AUDIO_STATIC_DATA

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a",
                                       position={"x": 1, "y": 1.6, "z": -2},
                                       look_at={"x": 0, "y": 0.5, "z": 0}))
model_name = "vase_02"
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=c.get_unique_id()))
object_audio = DEFAULT_OBJECT_AUDIO_STATIC_DATA[model_name]
object_manager = ObjectManager(transforms=False, rigidbodies=True, bounds=False)
collision_manager = CollisionManager(enter=True, stay=True, exit=True, objects=False, environment=True)
c.add_ons.extend([collision_manager, object_manager])
c.communicate(commands)
previous_areas = dict()
for i in range(200):
    for object_id in collision_manager.env_collisions:
        event = CollisionAudioEvent(collision=collision_manager.env_collisions[object_id],
                                    object_0_dynamic=object_manager.rigidbodies[object_id],
                                    object_0_static=object_audio,
                                    object_1_dynamic=None,
                                    object_1_static=None,
                                    previous_areas=previous_areas)
        previous_areas = {object_id: event.area}
        if event.collision_type != CollisionAudioType.none:
            print(i, event.collision_type)
    c.communicate([])
c.communicate({"$type": "terminate"})
```


Output:

```
77 15124673 CollisionAudioType.impact
78 15124673 CollisionAudioType.impact
107 15124673 CollisionAudioType.impact
108 15124673 CollisionAudioType.scrape
109 15124673 CollisionAudioType.scrape
110 15124673 CollisionAudioType.scrape
111 15124673 CollisionAudioType.scrape
112 15124673 CollisionAudioType.scrape
113 15124673 CollisionAudioType.impact
116 15124673 CollisionAudioType.scrape
```

## Example F: Generate scrape sounds

It's possible to generate scrape sounds without using a TDW controller by calling `py_impact.get_scrape_sound()`. The parameters are nearly the same as in `get_impact_sound()` with two difference: `secondary_id` must be an integer (rather than optionally be None) and you must set [`scrape_material`](../../python/physics_audio/scrape_material.md).

In terms of implementation, the main difference in generating scrape sounds is that we want to append multiple frames of a scrape to the .wav file, so we'll add a second loop within a loop:

```python
from typing import List, Optional
import numpy as np
from tdw.add_ons.py_impact import PyImpact
from tdw.physics_audio.base64_sound import Base64Sound
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

py_impact = PyImpact()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape_without_controller")
if not output_directory.exists():
    output_directory.mkdir()
print(f"Audio will be saved to: {output_directory}")
contact_normals: List[np.array] = list()
for i in range(3):
    contact_normals.append(np.array([0, 1, 0]))
for i in range(5):
    sound: Optional[Base64Sound] = None
    for j in range(5):
        s = py_impact.get_scrape_sound(velocity=np.array([1.5, 0, 0]),
                                       contact_normals=contact_normals,
                                       primary_id=0,
                                       primary_material="metal_1",
                                       primary_amp=0.2,
                                       primary_mass=1,
                                       secondary_id=1,
                                       secondary_material="stone_4",
                                       secondary_amp=0.5,
                                       secondary_mass=100,
                                       primary_resonance=0.2,
                                       secondary_resonance=0.1,
                                       scrape_material=ScrapeMaterial.ceramic)
        if sound is None:
            sound = s
        elif s is not None:
            sound.bytes += s.bytes
            sound.length += s.length
    sound.write(path=output_directory.joinpath(f"{i}.wav"))
```

You can also generate scrape audio TDW command by calling `py_impact.get_scrape_command()`:

```python
from time import sleep
from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.audio_utils import AudioUtils
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
# Add a camera and initialize audio.
y = 2
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": y, "z": 0})
resonance_audio_floor = "metal"
resonance_audio_wall = "brick"
resonance_audio_ceiling = "acousticTile"
audio = ResonanceAudioInitializer(avatar_id="a",
                                  floor=resonance_audio_floor,
                                  front_wall=resonance_audio_wall,
                                  back_wall=resonance_audio_wall,
                                  left_wall=resonance_audio_wall,
                                  right_wall=resonance_audio_wall,
                                  ceiling=resonance_audio_ceiling)
c.add_ons.extend([camera, audio])

# Initialize the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))

# Initialize PyImpact but DON'T add it as an add-on.
py_impact_floor = ResonanceAudioInitializer.AUDIO_MATERIALS[resonance_audio_floor]
impact_sound_floor = py_impact_floor.name + "_4"
py_impact = PyImpact(initial_amp=0.9, floor=py_impact_floor, resonance_audio=True, rng=np.random.RandomState(0))

# Generate contact normals and set the collision velocity.
contact_normals: List[np.array] = list()
for i in range(3):
    contact_normals.append(np.array([0, 1, 0]))
velocity = np.array([1.5, 0, 0])

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape_with_controller/audio.wav")
print(f"Audio will be saved to: {path}")
if not path.parent.exists():
    path.parent.mkdir(parents=True)
AudioUtils.start(output_path=path)
# Add sounds in a circle around the avatar.
distance = 1.5
theta = 0
d_theta = 15
contact_radius = 0.0625
while theta < 360:
    # Get the position of the sound.
    rad = np.radians(theta)
    x = np.cos(rad) * distance
    z = np.sin(rad) * distance
    # Generate contact points around the sound's position.
    contact_points: List[np.array] = list()
    contact_angle = 0
    for i in range(3):
        r = np.radians(contact_angle)
        contact_x = np.cos(r) * contact_radius + x
        contact_z = np.sin(r) * contact_radius + z
        contact_points.append(np.array([contact_x, y, contact_z]))

    # Get a sound.
    for i in range(5):
        c.communicate(py_impact.get_scrape_sound_command(velocity=velocity,
                                                         contact_points=contact_points,
                                                         contact_normals=contact_normals,
                                                         primary_id=0,
                                                         primary_material="metal_1",
                                                         primary_amp=0.4,
                                                         primary_mass=4,
                                                         secondary_id=None,
                                                         secondary_material="ceramic_4",
                                                         secondary_amp=0.5,
                                                         secondary_mass=100,
                                                         primary_resonance=0.4,
                                                         secondary_resonance=0.2,
                                                         scrape_material=ScrapeMaterial.ceramic))
        py_impact.reset()
    sleep(0.15)
    theta += d_theta
sleep(0.15)
AudioUtils.stop()
c.communicate({"$type": "terminate"})
```

## Example G: Generate roll sounds

Roll sounds have not yet been implemented in PyImpact.

***

**Next: [Audio perception](audio_perception.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [collision_events.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/collision_events.py) Get collision audio event types without using PyImpact.
- [implausible_audio.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/implausible_audio.py) Generate audio using audio physics parameters that don't match the object's actual physics parameters.
- [impact_with_controller.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/impact_with_controller.py) Generate impact sounds with PyImpact without using physics data and play the audio in a circle around the avatar listener.
- [impact_without_controller.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/impact_without_controller.py) Generate impact sounds with PyImpact without using a TDW controller.
- [scrape_with_controller.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/scrape_with_controller.py) Generate impact sounds with PyImpact without using physics data and play the audio in a circle around the avatar listener.
- [scrape_without_controller.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/scrape_without_controller.py) Generate scrape sounds with PyImpact without using a TDW controller.

Python API:

- [`PyImpact`](../../python/add_ons/py_impact.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`ResonanceAudioInitializer`](../../python/add_ons/resonance_audio_initializer.md)
- [`CollisionManager`](../../python/add_ons/collision_manager.md)
- [`ObjectManager`](../../python/add_ons/object_manager.md)
- [`AudioMaterial`](../../python/physics_audio/audio_material.md)
-  [`Base64Sound`](../../python/physics_audio/base64_sound.md)
- [`ObjectAudioStatic`](../../python/physics_audio/object_audio_static.md)
- [`CollisionAudioType`](../../python/physics_audio/collision_audio_type.md)
- [`CollisionAudioEvent`](../../python/physics_audio/collision_audio_event.md)
-  [`Modes`](../../python/physics_audio/modes.md)
-  [`ScrapeMaterial`](../../python/physics_audio/scrape_material.md)

Command API:

- [`play_audio_data`](../../api/command_api.md#play_audio_data) 
- [`play_point_source_data`](../../api/command_api.md#play_audio_data)

Output Data:

- [`Rigidbodies`](../../api/output_data.md#Rigidbodies)
