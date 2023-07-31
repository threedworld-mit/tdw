# PyImpact and Clatter

PyImpact was added to TDW in 2019, version 1.5.0. Clatter is an upgraded version of PyImpact that was added to TDW in 2023, version 1.11.4. If you have a new TDW audio project, you should always use Clatter instead of PyImpact. This document highlights key differences between PyImpact and Clatter and includes recommendations for how to upgrade an existing project.

## Frontend

### Audio initialization

Audio initialization is the same in PyImpact and in Clatter; [read this for more information.](../audio/initialize_audio.md)

### Replaced `AudioMaterial` with `ImpactMaterial`

`ImpactMaterial` is a renamed `AudioMaterial` for the sake of clarity. The Clatter Python code always uses `ImpactMaterial`, not `AudioMaterial`. To import:

```python
from tdw.physics_audio.impact_material import ImpactMaterial
```

### objects.csv

Like PyImpact, Clatter loads default audio data from objects.csv. This data hasn't been changed. Clatter converts the data into a `ClatterObject` instead of a `ObjectAudioStatic`. A `ClatterObject` doesn't load *all* information from objects.csv, just the information required for Clatter. It also includes an optional `ScrapeModel` (see below).

To load default Clatter object data:

```python
from tdw.physics_audio.clatter_object import DEFAULT_OBJECTS
```

### Non-default object data and scrape model data

In PyImpact, you can add your own static object data overrides by setting the `static_audio_data_overrides` parameter in the constructor. You can add your own scrape model overrides by setting the `scrape_objects` parameter in the constructor:

```python
from tdw.physics_audio.object_audio_static import ObjectAudioStatic
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.scrape_model import ScrapeModel
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.physics_audio.scrape_sub_object import ScrapeSubObject
from tdw.add_ons.py_impact import PyImpact

model_name = "iron_box"
material = AudioMaterial.wood_medium
object_id = 0
o = ObjectAudioStatic(name=model_name,
                      material=material,
                      mass=1,
                      bounciness=0.48,
                      amp=0.01,
                      size=4,
                      resonance=0.25,
                      object_id=object_id)
scrape_model = ScrapeModel(model_name=model_name,
                           visual_material="cardboard_corrugated",
                           audio_material=material,
                           scrape_material=ScrapeMaterial.plywood,
                           sub_objects=[ScrapeSubObject(name="ir",
                                                        material_index=0)])
py_impact = PyImpact(static_audio_data_overrides={object_id: o},
                     scrape_objects={object_id: scrape_model})
```

In Clatter, you can add your own object data overrides by setting the `objects` parameter in the constructor. Each object has an optional `scrape_model` parameter that you can set:

```python
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.scrape_model import ScrapeModel
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.physics_audio.scrape_sub_object import ScrapeSubObject
from tdw.add_ons.clatter import Clatter

model_name = "iron_box"
material = ImpactMaterial.wood_medium
object_id = 0
scrape_model = ScrapeModel(model_name=model_name,
                           visual_material="cardboard_corrugated",
                           audio_material=material,
                           scrape_material=ScrapeMaterial.plywood,
                           sub_objects=[ScrapeSubObject(name="ir",
                                                        material_index=0)])
o = ClatterObject(impact_material=material,
                  amp=0.01,
                  size=4,
                  resonance=0.25, 
                  scrape_model=scrape_model)
clatter = Clatter(objects={object_id: o})
```

### Constructor parameters and class variables

In PyImpact, global variables are spread out across multiple classes. In Clatter, they have all been consolidated as constructor parameters:

| PyImpact constructor parameter | Clatter constructor parameter |
| ------------------------------ | ----------------------------- |
| rng                            | random_seed                   |
| initial_amp                    | simulation_amp                |
| floor                          | environment                   |
| prevent_distortion             | prevent_impact_distortion     |
| min_time_between_impact_events | min_time_between_impacts      |
| resonance_audio                | resonance_audio               |
| auto                           |                               |
| scrape                         |                               |

| PyImpact class variable                                      | Clatter constructor parameter |
| ------------------------------------------------------------ | ----------------------------- |
| CollisionAudioEvent.IMPACT_AREA_NEW_COLLISION                | area_new_collision            |
| CollisionAudioEvent.IMPACT_AREA_RATIO                        | impact_area_ratio             |
| CollisionAudioEvent.ROLL_ANGULAR_VELOCITY                    | roll_angular_speed            |
| PyImpact.SCRAPE_MAX_VELOCITY                                 | max_scrape_speed              |
| PyImpact.DEFAULT_AMP<br>PyImpact.DEFAULT_MATERIAL<br>PyImpact.DEFAULT_SIZE | default_object                |
| PyImpact.FLOOR_AMP<br>PyImpact.FLOOR_SIZE<br>PyImpact.FLOOR_MASS | environment                   |
| PyImpact.ROBOT_JOINT_MATERIAL                                | robot_material                |
| PyImpact.VR_HUMAN_MATERIAL                                   | human_material                |
| PyImpact.SCRAPE_M_PER_PIXEL                                  |                               |
| PyImpact.ROBOT_JOINT_BOUNCINESS                              |                               |
| PyImpact.VR_HUMAN_BOUNCINESS                                 |                               |

Clatter also contains additional constructor parameters:

- dsp_buffer_size
- min_collision_speed
- scrape_angle
- max_contact_separation
- filter_duplicates
- max_num_contacts
- sound_timeout
- clamp_impact_contact_time
- max_time_between_impacts
- loop_scrape_audio
- max_num_events
- dsp_buffer_size
- rolll_substitute

### Collisions

Because Clatter handles audio generation within the build, the Python code doesn't need to listen to collision events. Accordingly, while `PyImpact` is a subclass of `CollisionManager`, `Clatter` is a subclass of `AddOn`. If you want collision data in addition to Clatter audio, you'll need to add a `CollisionManager` to your controller.

Clatter's algorithm for converting collision states (enter, stay, exit) into audio types (impact, scrape, roll, none) is somewhat different than PyImpact. For the most part, this is because Clatter fixes some bugs that would be difficult to fix in PyImpact due to how TDW is structured.

### Generate audio without a controller

In PyImpact, it is possible to write a Python script that generates audio without a controller.

In Clatter, you can use the command-line executable (clatter.exe on Windows) to generate wav files. You can call this executable from Python using subprocess. For more information, [read this.](../clatter/cli.md)

## Backend

The most significant difference between PyImpact and Clatter is the backend architecture.

PyImpact's audio synthesis is handled in Python, in the `tdw` module. Once audio samples are generated, they are serialized into a base64 string, sent to the build within a command dictionary, deserialized, and played. The process of serializiation, sending data over the wire, and deserialization is slow. Additionally, PyImpact can only generate audio sequentially.

Clatter exists mostly within the build and all of its audio synthesis is handled in C# libraries. It is not part of the private TDW backend C# repo (TDWBase); instead, Clatter exists in its own publicly available repo. [Read the backend documentation here.](https://alters-mit.github.io/clatter/index.html)

Clatter doesn't need to serialize or deserialize anything. It also handles each audio event on a separate thread, making it by far faster than PyImpact in cases where there is concurrent audio.

### Benchmarks

| Test                                                         | Time elapsed (seconds) |
| ------------------------------------------------------------ | ---------------------- |
| PyImpact generates 100 impact sounds without a controller    | 0.62                   |
| PyImpact generates 100 impact sounds and plays them in a controller. Each impact sound is sent on a separate communicate() call. | 1.75                   |
| Clatter generates 100 impact sounds without a controller and without threading. | 0.54                   |
| Clatter generates 100 impact sounds without a controller and with threading. | 0.10                   |
| Clatter generates 100 impact sounds with threading and plays them in a controller. | 0.30*                  |

\* Time elapsed in this case is the sum of the time elapsed only for the frames in which collisions occurred.

### Data classes

Both PyImpact and Clatter use many data classes in addition to the add-on classes. In Clatter, most of these have been moved to the C# repo. PyImpact and Clatter share only a few classes:

| PyImpact            | Clatter (Python) | Clatter (C#)                                                 |
| ------------------- | ---------------- | ------------------------------------------------------------ |
| PyImpact            | Clatter          | AudioGenerator<br>Impact<br>ImpactMaterialData<br>Scrape<br>ScrapeMaterialData<br>ClatterManager |
| AudioMaterial       | ImpactMaterial   | ImpactMaterialUnsized                                        |
| Base64Sound         |                  | Samples                                                      |
| CollisionAudioEvent |                  | CollisionEvent<br>ClatterObject                              |
| CollisionAudioInfo  |                  | AudioEvent                                                   |
| CollisionAudioType  |                  | AudioEventType                                               |
| Modes               |                  | Modes                                                        |
| ObjectAudioStatic   | ClatterObject    | ClatterObjectData                                            |
| ScrapeMaterial      | ScrapeMaterial   | ScrapeMaterial                                               |
| ScrapeModel         | ScrapeModel      |                                                              |
| ScrapeSubObject     | ScrapeSubObject  |                                                              |

## Audio synthesis algorithms

Clatter's audio synthesis algorithms have, in general, been written to match PyImpact's as closely as possible.

In many cases, an exact 1:1 porting of a PyImpact algorithm isn't possible; usually this is because PyImpact is using numpy code that is difficult to rewrite in C#. Clatter uses code snippets originally found in .NET math libraries (and then optimized for Clatter).

### Converting collision events to audio events

Clatter and PyImpact have *similar* algorithms for converting collision events (enter, stay, exit) into audio events (impact, scrape, roll, none). Clatter's algorithm is more sophisticated and eliminates some prevalent bugs that would be difficult to fix in PyImpact. Clatter also reorganizes and expands upon the static variables you can use to control this algorithm (notably, there is a better system for differentiating between an impact and a scrape, and a user-end variable for deciding how to handle roll events).

### Modes, impulse responses, and impacts

The algorithms used by modes, impulse response synthesis, and impact audio synthesis are nearly the same in Clatter and PyImpact.

### Scrapes

Clatter's scrape algorithm is different from PyImpact's. It's actually a port of [this unmerged pull request](https://github.com/threedworld-mit/tdw/pull/509). This is because the pull request algorithm works better and is much faster than the algorithm used in the master branch version of PyImpact. There is one major difference between Clatter's scrape implementation to the implementation in the PyImpact pull request: Clatter doesn't try, or need to, scale arrays by the simulator framerate.

In PyImpact, scrape audio is sent in chunks to Unity. If the framerate is too slow, there will be gaps of silence between the gaps. If the framerate is too fast, the audio chunks will overlap. In Clatter, scrape audio chunks are stored internally in a queue. There can still be gaps of silence in Clatter while new scrape audio is being generated. To solve this, Clatter plays each scrape audio chunk in a loop until a new audio chunk is available. This is not "realistic" per se but tends to work well (and isn't any worse than the overlapping audio in PyImpact). This behavior can optionally be disabled by setting `loop_scrape_audio=False` in the `Clatter` add-on constructor.