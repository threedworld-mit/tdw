##### Audio

# `PyImpact` (dynamic impact sounds)

*PyImpact uses data from the PhysX physics engine to generate audio. If you haven't done so already, we strongly recommend you read the [physics tutorial](../physx/overview.md).*

`PyImpact` can synthesize novel plausible impact sounds for any object. Upon every call the sound resonant modes will be randomly sampled and the impacts will sound slightly different.  Thus, two different objects in the same scene with the same material will create similar but unique sounds.  And the same scene run repeatedly will generate similar but unique sounds at every run.  This is designed to emulate the real world, where tapping the same object repeatedly yields slightly different sounds on each impact.

When using PyImpact, please cite  [Traer,Cusimano and McDermott, A perceptually inspired generative model of rigid-body contact sounds, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf) and [Agarwal, Cusimano, Traer, and McDermott, Object-based synthesis of scraping and rolling sounds based on non-linear physical constraints, (DAFx), 2021](http://mcdermottlab.mit.edu/bib2php/pubs/makeAbs.php?loc=agarwal21). 

```
@article {4500,
	title = {A perceptually inspired generative model of rigid-body contact sounds},
	journal = {Proceedings of the 22nd International Conference on Digital Audio Effects (DAFx-19)},
	year = {2019},
	month = {09/2019},
	abstract = {<p>Contact between rigid-body objects produces a diversity of impact and friction sounds. These sounds can be synthesized with detailed simulations of the motion, vibration and sound radiation of the objects, but such synthesis is computationally expensive and prohibitively slow for many applications. Moreover, detailed physical simulations may not be necessary for perceptually compelling synthesis; humans infer ecologically relevant causes of sound, such as material categories, but not with arbitrary precision. We present a generative model of impact sounds which summarizes the effect of physical variables on acoustic features via statistical distributions fit to empirical measurements of object acoustics. Perceptual experiments show that sampling from these distributions allows efficient synthesis of realistic impact and scraping sounds that convey material, mass, and motion.</p>
},
	author = {James Traer and Maddie Cusimano and Josh H. McDermott}
}
```

```
@inproceedings{agarwal21,
     TITLE= "Object-based synthesis of scraping and rolling sounds based on non-linear physical constraints",
     AUTHOR= "V Agarwal and M Cusimano and J Traer and J H McDermott",
     booktitle= "The 24th International Conference on Digital Audio Effects (DAFx-21)",
     MONTH= "September",
     YEAR= 2021,
     PDF-URL= "http://mcdermottlab.mit.edu/papers/Agarwal_etal_2021_scraping_rolling_synthesis_DAFx.pdf",
}
```

## Requirements

- [See requirements for audio playback.](overview.md) 
- If you add to a script `from tdw.py_impact import PyImpact`, your script might print a warning about ffmpeg  when you run it. This is because ffmpeg isn't installed on  your machine. The warning can be ignored (`PyImpact` doesn't actually use ffmpeg). If you want to suppress it, install ffmpeg:
  - Windows: [Download from here](https://ffmpeg.org/download.html#build-windows) and then [add ffmpeg to your system path](https://windowsloop.com/install-ffmpeg-windows-10/).
  - OS X: [Install via brew](https://formulae.brew.sh/formula/ffmpeg)
  - Ubuntu: `apt install ffmpeg`
  - Docker: The TDW Docker container will automatically install ffmpeg

## Usage

1. [Create a scene.](../core_concepts/scenes.md)
2. [Add an avatar.](../core_concepts/avatars.md)
3. [Initialize audio.](initialize_audio.md) (Optionally, initialize [Resonance Audio](resonance_audio.md) instead.)
4. [Add an object.](../core_concepts/objects.md)
5. Add a [`PyImpact`](../../python/add_ons/py_impact.md) add-on.

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
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result: [Synthesized audio from the object colliding with the floor.](https://drive.google.com/file/d/1DkvC9HP7XpnYUGNGNW5AuXBMmCXuXmjz/view?usp=sharing)

## Auto-generated audio

By default, PyImpact will evaluate the simulation state per `c.communicate()` call and will automatically generate audio that will then be played by the build. This behavior can be suppressed by setting `auto=False` in the constructor.

PyImpact automatically requests and receives [Rigidbody data](../physx/rigidbodies.md) and [collision data](../physx/collisions.md) per-frame, as well as [`RobotJointVelocities`](../../api/output_data.md#RobotJointVelocities), a special output data type required for simulations with robots.

`PyImpact` is a sub-class of [`CollisionManager`](../../python/add_ons/collision_manager.md). You shouldn't include both a `PyImpact` add-on and a `CollisionManager` add-on.

PyImpact uses cached static object data and per-frame physics metadata (velocities, collision states, etc.) to create audio, convert the audio into TDW commands, and send the commands on the next `c.communicate()` call.

## The `initial_amp` parameter

`initial_amp` controls the overall volume of PyImpact. It must be between 0 and 1.

## Audio materials

Within the context of PyImpact, every object has a corresponding [`AudioMaterial`](../../python/physics_audio/audio_material.md). This is one of the most important factors of how audio is generated; a wood object colliding with a wood object will make a very different sound than a metal object colliding with a glass object.

The floor of the scene always has a material. Set the floor audio material by setting the `floor` parameter of the `PyImpact` constructor or by setting `py_impact.floor`:

```python
from tdw.add_ons.py_impact import PyImpact
from tdw.physics_audio.audio_material import AudioMaterial

py_impact = PyImpact(floor=AudioMaterial.wood_hard)
py_impact.floor = AudioMaterial.metal
```

## Resonance audio materials

An `AudioMaterial` is not quite the same thing as a [Resonance Audio material](resonance_audio.md); the latter is defined by third-party software. However, TDW does include a dictionary to map `AudioMaterial` to Resonance Audio material.

Note that when using Resonance Audio, you must set `resonance_audio=True` in the `PyImpact` constructor.

```python
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer

resonance_audio_material = "parquet"
audio_material = ResonanceAudioInitializer.AUDIO_MATERIALS[resonance_audio_material]
py_impact = PyImpact(floor=audio_material, resonance_audio=True)
audio_initializer = ResonanceAudioInitializer(floor=resonance_audio_material)
```

## Static object audio data

`PyImpact` uses [`ObjectAudioStatic`](../../python/physics_audio/object_audio_static.md) data to generate audio from the physical properties of an object. This data overlaps with, but is not the same as, [static physics values](../physx/physics_objects.md).

A subset of objects in TDW have *default static audio values*. These are are stored in `DEFAULT_OBJECT_AUDIO_STATIC_DATA`. The keys of the dictionary are model names:

```python
from tdw.physics_audio.object_audio_static import DEFAULT_OBJECT_AUDIO_STATIC_DATA

model_name = "iron_box"
print(model_name in DEFAULT_OBJECT_AUDIO_STATIC_DATA) # True
```

If you add a model to the scene that isn't included in `DEFAULT_OBJECT_AUDIO_STATIC_DATA`, PyImpact will derive default audio values based on similar models (models in the same category, models of roughly the same size, etc.).

You can optionally manually set an object's `ObjectAudioStatic` data by setting the optional `static_audio_data_overrides` in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.object_audio_static import ObjectAudioStatic

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a",
                                       position={"x": 1, "y": 1.6, "z": -2},
                                       look_at={"x": 0, "y": 0.5, "z": 0}))
object_id = c.get_unique_id()
name = "vase_02"
mass = 0.5
bounciness = 0.6
commands.extend(c.get_add_physics_object(model_name=name,
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=object_id,
                                         default_physics_values=False,
                                         mass=mass,
                                         bounciness=bounciness))
audio_initializer = AudioInitializer(avatar_id="a")
static_audio_data = ObjectAudioStatic(name=name,
                                      object_id=object_id,
                                      mass=mass,
                                      bounciness=bounciness,
                                      amp=0.6,
                                      resonance=0.45,
                                      size=1,
                                      material=AudioMaterial.wood_soft)
py_impact = PyImpact(static_audio_data_overrides={object_id: static_audio_data})
c.add_ons.extend([audio_initializer, py_impact])
c.communicate(commands)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result: [Synthesized audio that sounds different than the previous example.](https://drive.google.com/file/d/1b7XcQGsCxbGJhGwPsqw1EbaHnj3ngMxV/view?usp=sharing)

## Dynamic friction, static friction, and bounciness

Dynamic friction and static friction are always the same for each audio material (as opposed to varying per-object). You can get the friction values per audio material from `tdw.physics_audio.audio_material_constants`:

```python
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.audio_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION

for material in AudioMaterial:
    dynamic_friction = DYNAMIC_FRICTION[material]
    static_friction = STATIC_FRICTION[material]
    print(material, dynamic_friction, static_friction)
```

Bounciness, on the other hand, *does* vary per-object and is stored in `ObjectAudioStatic`.

## Impacts, scrapes, and rolls

PyImpact generates impact, scrapes, and rolls using three different processes.

- Impact sounds are fully implemented.
- Scrape sounds are partially implemented; they still need to be differentiated by audio/visual material.
- Rolls aren't implemented yet.

In order to decide which process to use, PyImpact must first determine the "event type" of a collision. This is  normally done automatically but it can be useful to understand how it works:

- It's possible for a pair of objects to register multiple collision events on the same `communicate()` call if [the controller is skipping physics frames](../physx/step_physics.md). In these cases, PyImpact evaluates the collision with the highest overall speed.
- If the collision state is `"exit"` or the velocity is `0`, the event is `none`.
- If the collision state is `"enter"`, the event is `impact`.
- If the collision state is `"stay"`:
  - If the contact area changed by more than 500% since the previous frame, the event is `impact`.
  - If there was no previous contact area and the contact area is greater than 0.00001, the event is `impact`.
  - Otherwise:
    - If the angular velocity is > 0.5 m/s, the event is `roll`.
    - Otherwise: the event is `scrape`.

## The `min_time_between_impact_events` parameter

`PyImpact` has an optional parameter `min_time_between_impact_events`  that sets the minimum time in seconds between impact audio events. This can be set to 0, but it will likely create an unwanted "droning" effect as objects rattle. Setting this to a higher value will remove unwanted droning but might also remove valid impact sounds. The default setting is meant to be a reasonable compromise between these two extremes that will suffice for most scenarios.

## Scrape sounds

Scrape sounds can only be generated from a predefined list of models with "scrape surfaces". Each of these models may have more than one "scrape surface", such as shelving. Each surface must have a particular visual material. When `PyImpact` is initialized, it will automatically find objects with scrape surfaces, cache relevant data, and set their visual materials. Note that the floor of the scene won't generate scrape sounds.

To get a list of models with "scrape surfaces", you can read the dictionary `tdw.physics_audio.scrape_model.DEFAULT_SCRAPE_MODELS`:

```python
from tdw.physics_audio.scrape_model import DEFAULT_SCRAPE_MODELS

for model_name in DEFAULT_SCRAPE_MODELS:
    print(model_name)
print("small_table_green_marble" in DEFAULT_SCRAPE_MODELS)  # True
```

This controller will automatically initialize model `small_table_green_marble` as a scrape surface:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a"))
commands.extend(c.get_add_physics_object(model_name="small_table_green_marble",
                                         object_id=c.get_unique_id()))
audio_initializer = AudioInitializer(avatar_id="a")
py_impact = PyImpact()
c.add_ons.extend([audio_initializer, py_impact])
c.communicate(commands)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

### Disable scrape sounds

To disable scrape sounds in `PyImpact`, set `scrape=False` in the constructor.

### Manually set scrape objects and surfaces

To manually initialize objects as scrape surfaces, set the `scrape_objects` parameter in the constructor. This is a dictionary: Key = an object ID. Value = A [`ScrapeModel`](../../python/physics_audio/scrape_model.md).

A `ScrapeModel` the following:

- An `AudioMaterial`

- A [`ScrapeMaterial`](../../python/physics_audio/scrape_material.md) Due to separate recording processes, this isn't the same as `AudioMaterial`, although it can be mapped to an `AudioMaterial`

- A visual material (a string)

- A list of [`ScrapeSubObject`](../../python/physics_audio/scrape_sub_object.md):

  - The material index (this is usually 0)
  - The name of the sub-object. See `ModelRecord.substructure`:

  ```python
  from tdw.librarian import ModelLibrarian
  
  librarian = ModelLibrarian()
  record = librarian.get_record("iron_box")
  print(record.substructure)
  ```

  Output:

  ```
  [{'materials': ['Material_#9'], 'name': 'ir'}]
  ```

This will manually initialize an `iron_box` object for scraping. Note that `iron_box` is one of the default scrape models but `scrape_objects` will override the default data:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.physics_audio.scrape_model import ScrapeModel
from tdw.physics_audio.scrape_sub_object import ScrapeSubObject

c = Controller()
object_id = c.get_unique_id()
model_name = "iron_box"
scrape_model = ScrapeModel(model_name=model_name,
                           visual_material="cardboard_corrugated",
                           audio_material=AudioMaterial.cardboard,
                           scrape_material=ScrapeMaterial.plywood,
                           sub_objects=[ScrapeSubObject(name="ir",
                                                        material_index=0)])
py_impact = PyImpact(scrape_objects={object_id: scrape_model})
audio_intializer = AudioInitializer(avatar_id="a")
c.add_ons.extend([audio_intializer, py_impact])
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         object_id=object_id))
c.communicate(commands)
```

## Roll sounds

Roll sounds have not yet been implemented in PyImpact.

## Random number generator

Impact sounds are varied using a random number generator. [For the sake of being able to recreate scenes](../scene_setup_high_level/reset_scene.md), it might be useful to use a shared random number generate by setting the `rng` parameter in the constructor:

```python
import numpy as np
from tdw.add_ons.py_impact import PyImpact

seed = 0
rng = np.random.RandomState(seed)
py_impact = PyImpact(rng=rng)
```

## `PyImpact` and robots

It is possible to generate impact sounds from the body of a [robot](../robots/overview.md). Please the [robot collision detection documentation](../robots/collision_detection.md) carefully!

Once a robot has been added to the scene and initialized for collision detection, PyImpact will automatically set static audio data for each joint:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.robot import Robot
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()

# Add a camera and a robot.
avatar_id = "a"
robot = Robot(name="ur5")
camera = ThirdPersonCamera(avatar_id=avatar_id,
                           position={"x": 0, "y": 2, "z": 2},
                           look_at={"x": 0, "y": 0, "z": 0})
c.add_ons.extend([camera, robot])

# Initialize the scene.
c.communicate(TDWUtils.create_empty_room(6, 6))

# Wait for the robot to reach its initial pose.
while robot.joints_are_moving():
    c.communicate([])

# Initialize audio. Initialize PyImpact. Add an audio recorder.
floor_material = "tile"
audio_initializer = ResonanceAudioInitializer(avatar_id=avatar_id)
py_impact = PyImpact(initial_amp=0.5,
                     resonance_audio=True,
                     floor=ResonanceAudioInitializer.AUDIO_MATERIALS[floor_material])
c.add_ons.extend([audio_initializer, py_impact])

# Add an object above the robot.
c.communicate(c.get_add_physics_object(model_name="rh10",
                                       object_id=c.get_unique_id(),
                                       position={"x": 0, "y": 6, "z": 0}))
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

## Reset `PyImpact`

**`PyImpact` must be reset every time the scene is reset.** If you don't, you'll get very buggy behavior and the controller might crash.

To reset PyImpact, call `self.reset()`. You can optionally supply new static object audio override data and scrape object data.

In this example, an object is assigned random physics and audio values and then dropped from a random height. After every trial, the object is destroyed and PyImpact is reset:

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.physics_audio.object_audio_static import ObjectAudioStatic
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.audio_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION


class ResetPyImpact(Controller):
    """
    Reset `PyImpact` between trials.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(0)

        # Add a camera.
        camera = ThirdPersonCamera(position={"x": 1, "y": 1.7, "z": -0.5},
                                   look_at={"x": 0, "y": 0.5, "z": 0},
                                   avatar_id="a")
        resonance_audio_floor = "parquet"
        py_impact_floor = ResonanceAudioInitializer.AUDIO_MATERIALS[resonance_audio_floor]
        # Initialize audio.
        audio_initializer = ResonanceAudioInitializer(avatar_id="a", floor=resonance_audio_floor)
        # Initialize PyImpact, using the controller's RNG.
        self.py_impact = PyImpact(initial_amp=0.5, floor=py_impact_floor, rng=self.rng, resonance_audio=True)
        # Initialize the scene.
        self.add_ons.extend([camera, audio_initializer, self.py_impact])
        self.communicate(TDWUtils.create_empty_room(7, 7))

    def trial(self) -> None:
        # Set the parameters for initializing the object.
        object_id: int = self.get_unique_id()
        object_name: str = "vase_02"
        object_mass: float = float(self.rng.uniform(0.5, 0.8))
        object_bounciness: float = float(self.rng.uniform(0.5, 0.7))
        object_material = AudioMaterial.wood_soft
        static_audio_data = ObjectAudioStatic(name=object_name,
                                              object_id=object_id,
                                              mass=object_mass,
                                              bounciness=object_bounciness,
                                              amp=0.6,
                                              resonance=0.45,
                                              size=1,
                                              material=object_material)
        # Reset PyImpact.
        self.py_impact.reset(static_audio_data_overrides={object_id: static_audio_data})
        # Add the object.
        self.communicate(self.get_add_physics_object(model_name=object_name,
                                                     position={"x": 0, "y": float(self.rng.uniform(3, 4)), "z": 0},
                                                     object_id=object_id,
                                                     default_physics_values=False,
                                                     mass=object_mass,
                                                     dynamic_friction=DYNAMIC_FRICTION[object_material],
                                                     static_friction=STATIC_FRICTION[object_material],
                                                     bounciness=object_bounciness))
        # Let the object fall.
        for i in range(200):
            self.communicate([])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})

    def run(self) -> None:
        for i in range(10):
            self.trial()
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ResetPyImpact()
    c.run()
```

***

**Next: [Recording audio](record_audio.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [py_impact.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/py_impact.py) A minimal implementation of `PyImpact`.
- [robot_impact_sound.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/robot_impact_sound.py) Create an impact sound between an object and a robot.
- [reset_py_impact.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/robot_impact_sound.py) Reset PyImpact after every trial.

Python API:

- [`PyImpact`](../../python/add_ons/py_impact.md)
- [`ObjectAudioStatic`](../../python/physics_audio/object_audio_static.md)
- [`AudioMaterial`](../../python/physics_audio/audio_material.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`ResonanceAudioInitializer`](../../python/add_ons/resonance_audio_initializer.md)
- [`CollisionManager`](../../python/add_ons/collision_manager.md)
- [`Robot`](../../python/add_ons/robot.md)
- [`ScrapeModel`](../../python/physics_audio/scrape_model.md)
- [`ScrapeMaterial`](../../python/physics_audio/scrape_material.md)
- [`ScrapeSubObject`](../../python/physics_audio/scrape_sub_object.md)

Output Data:

- [`Rigidbodies`](../../api/output_data.md#Rigidbodies)
- [`Collision`](../../api/output_data.md#Collision)
- [`EnvironmentCollision`](../../api/output_data.md#EnvironmentCollision)
- [`RobotJointVelocities`](../../api/output_data.md#RobotJointVelocities)