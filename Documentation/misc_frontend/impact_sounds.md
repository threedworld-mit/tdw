# Impact Sounds in TDW

There are several ways to generate impact sounds in TDW:

1. You can use the [PyImpact class](../python/py_impact.md).  

2. You can use your own audio-samples.

## PyImpact

The PyImpact class contains scripts to synthesize novel plausible impact sounds for any object. The sound synthesis method roughly follows that described in [Traer,Cusimano and McDermott, A PERCEPTUALLY INSPIRED GENERATIVE MODEL OF RIGID-BODY CONTACT SOUNDS, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf). Upon every call the sound resonant modes will be randomly sampled and the impacts will sound slightly different.  Thus, two different objects in the same scene with the same material will create similar but unique sounds.  And the same scene run repeatedly will generate similar but unique sounds at every run.  This is designed to emulate the real world, where tapping the same object repeatedly yields slightly different sounds on each impact.

## Simple usage

The "simple" version of PyImpact loads default physics and audio values for each object in the scene and automatically generates impact sounds.

At minimum, you need to:

1. Create a scene, initialize PyImpact, and set the target framerate to 100 (to align with the default physics timestep of 0.01 seconds):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.py_impact import PyImpact, AudioMaterial
from tdw.object_init_data import AudioInitData

c = Controller()
c.start()
p = PyImpact(initial_amp=0.25)
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_target_framerate",
             "framerate": 100}]
```

2. Set the floor and wall audio materials. These will be used whenever an object collides with a floor or wall:

```python
floor = AudioMaterial.ceramic
wall = AudioMaterial.wood
```

3. Add an avatar and give it an audio sensor:

```python
commands.extend(TDWUtils.create_avatar(avatar_type="A_Img_Caps_Kinematic",
                                       position={"x": 1, "y": 1.2, "z": 1.2},
                                       look_at=TDWUtils.VECTOR3_ZERO))
commands.append({"$type": "add_audio_sensor"})
```

4. Add objects. You should create objects using the [`AudioInitData` class](../python/object_init_data.md), which will automatically assign physics values such as mass and friction:

```python
surface_name = "glass_table_round"
obj_name = "spoon1"
# Get initialization data from the default audio data (which includes mass, friction values, etc.).
surface_init_data = AudioInitData(name=surface_name,
                                  position={"x": 0, "y": 0, "z": 0})
obj_init_data = AudioInitData(name=obj_name,
                              position={"x": 0.1, "y": 2, "z": 0},
                              rotation={"x": 34, "y": 0.4, "z": 135})
# Convert the initialization data to commands.
surface_id, surface_commands = surface_init_data.get_commands()
obj_id, obj_commands = obj_init_data.get_commands()
# Add the objects.
commands.extend(surface_commands)
commands.extend(obj_commands)
```

5. Cache the names and objects in PyImpact. This will allow PyImpact to locate audio values given an object ID:

```python
object_names = {surface_id: surface_name,
                obj_id: obj_name}
p.set_default_audio_info(object_names=object_names)
```

6. Optionally, apply a force to an object (it will also fall due to gravity):

```python
commands.append( {"$type": "apply_force_to_object",
                  "force": {"x": 0, "y": -0.01, "z": 0},
                  "id": obj_id})
```

7. Request collision and rigidbody output data:

```python
commands.extend([{"$type": "send_collisions",
                  "enter": True,
                  "stay": False,
                  "exit": False,
                  "collision_types": ["obj", "env"]},
                 {"$type": "send_rigidbodies",
                  "frequency": "always"}])
```

8. Let the simulation run. Per-frame, PyImpact will try to create commands that play audio, given the output data from the build (which includes whether or not objects are colliding):

```python
# Send the commands.
resp = c.communicate(commands)
# Let the object fall.
for i in range(200):
    # Get impact sounds.
    commands = p.get_audio_commands(resp=resp, floor=floor, wall=wall)
    resp = c.communicate(commands)
c.communicate({"$type": "terminate"})
```

### Example controller

For a slightly more complicated example controller, see: `tdw/Python/example_controllers/impact_sounds.md`

### Resonance Audio

Resonance Audio will add reverberation to the audio playback. To set up a scene with Resonance Audio, make the following changes:

1. After adding the objects, include the `set_reverb_space_simple` command. (There are many other materials available. You can also set the wall materials. For a more thorough description, [read this](../api/command_api.md#set_reverb_space_simple).)

```python
commands.append({"$type": "set_reverb_space_simple",
                 "env": -1,
                 "reverb_floor_material": "marble"})
```

2. Replace `{"$type": "add_audio_sensor"}` with `{"$type": "add_environ_audio_sensor"}`
3. In the loop, set `resonance_audio=True`:

```python
# Send the commands.
resp = c.communicate(commands)
# Let the object fall.
for i in range(200):
    # Get impact sounds.
    commands = p.get_audio_commands(resp=resp, floor=floor, wall=wall, resonance_audio=True)
    resp = c.communicate(commands)
c.communicate({"$type": "terminate"})
```

### Avoiding "droning" effects

Occasionally, a vibrating object will create a "droning" or distorted audio effect. This happens because there are sometimes multiple collisions per object on the same frame (for example, the object collides with a chair, a table leg, and the floor).

`PyImpact.get_audio_commands()` will try to allow only one collision per object per frame. You can improve this filter by listening for `enter`, `stay`, and `exit` collision events (rather than just `enter`); PyImpact will ignore a collision if there is more than one event on the same frame (for example, if the object entered and stayed on the same other object).

However, the build will often generate many `stay` events per frame; this can be quite performance-intensive for complex scenes. To avoid this, you can add objects to the scene, let them settle into place, and *then* listen for `stay` events. The build listens for `stay` events only if it also listens for `enter` events; so if it doesn't listen for `enter` events as the objects settle into place, it won't hear any `stay` events either (which in this case you want).

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Rigidbodies

c = Controller(launch_build=False)
c.start()
commands = [TDWUtils.create_empty_room(12, 12)]

add_object_commands = []  # Your code here.

commands.extend(add_object_commands)
# Get rigidbody data.
commands.append({"$type": "send_rigidbodies",
                 "frequency": "always"})
resp = c.communicate(add_object_commands)

# Wait for all objects to settle.
sleeping = False
count = 0
while not sleeping and count < 200:
    sleeping = True
    for i in range(len(resp) - 1):
        # Get the rigidbody data and check if all objects are sleeping.
        r_id = OutputData.get_data_type_id(resp[i])
        if r_id == "rigi":
            rigidbodies = Rigidbodies(resp[i])
            for j in range(rigidbodies.get_num()):
                if not rigidbodies.get_sleeping(j):
                    sleeping = False
    count += 1

commands = [] # Add an object that you want to drop, the avatar, the audio sensor, etc.

# Get rigidbody data for all objects, including the dropping object.
commands.append({"$type": "send_rigidbodies",
                 "frequency": "always"})

# Listen for enter and stay events.
commands.append({"$type": "send_collisions",
                 "enter": True,
                 "exit": True,
                 "stay": True,
                 "collision_types": ["obj", "env"]})
resp = c.communicate(commands)
```

## Resetting PyImpact

You need to reset PyImpact between trials; otherwise, sounds will be "sharper" and higher pitched over time. There are two ways to reset:

1. Instantiate a new PyImpact object per trial:

```python
def trial():
    p = PyImpact()
    
    # Your code here.
```

2. Call the `reset()` function:

```python
p = PyImpact()

def trial():
    p.reset()
    
    # Your code here.
```

These two methods are functionally equivalent; however, because PyImpact's constructor reads files off the disk and then caches the data, calling `reset()` is more efficient.

Be sure to also call re-build the `object_names` dictionary (see above example) and call `p.set_default_audio_info(object_names)`.

## Advanced usage

It's possible to use PyImpact without applying default values. In these cases, you don't need to call `p.set_default_audio_info(object_names)` and you can use `p.get_impact_sound_command()` to manually set parameters.

For example implementation, see: `tdw/Python/use_cases/rube_goldberg/rube_goldberg.py`

### Inputs

TDW uses material, mass, and sound amplitudes (relative to an arbitrary standard) to create unique synthetic impact sounds.

A small portion of the [model library](../python/librarian/model_librarian.md) has default "recommended" values for PyImpact;  these include the model's mass, relative amplitude, audio material and "bounciness" These parameters are listed in a spreadsheet — `tdw/Python/tdw/py_impact/objects.csv`-- and can be accessed via `PyImpact.get_object_info()`. See below for guidelines on assigning values to these parameters.

More objects will be added to the list over time. It is possible to write your own list and load that instead by passing a `path` parameter to `get_object_info()`. See `tdw/Python/tdw/py_impact/objects.csv` for how to organize the spreadsheet.

#### Guidelines For Setting Object Parameters

Deciding what audio material to assign to an object is mostly a common-sense process. To some extent this is also true for an object's mass, though some amount of trial and error may be required to get the desired physics behavior.  Same for bouciness. When setting values for the relative amplitude values of objects ("amp"), it may be helpful to consider the object's:

- **Thickness**: Thin objects (boards, sheets, planks, hollow boxes) make more sound than thick solid blocks
- **Material**: Hard objects (metal, glass, ceramic) make more sound than soft (foam, rubber). Cardboard is a bit of outlier because it is soft, but is also almost always really, really thin which makes it surprisingly loud.
- **Size**: For objects of similar thickness, bigger are usually louder than smaller.

In PyImpact, these object amplitude values are scaled relative to the initial amplitude value passed in via `p = PyImpact(initial_amp=0.5)` (see code example below). This value must be > 0 and < 1. In certain situations, such as multiple closely-packed collision events, distortion of the audio can occur if this value is set too high. For example, the value used in the `impact_sound.py` example controller is 0.5, which is appropriate for a single event involving two objects. However the value used in `rube_goldberg.py` use-case example is much lower — 0.01 — due to the complex collision interactions involved.

The "resonance" values for objects, as set in `tdw/Python/tdw/py_impact/objects.csv`are guidelines and can be altered by the user if desired. Most objects should have values less than 1.0, and small solid objects (e.g. dominos) would have very small values, around 0.15 or thereabouts. Thin-walled objects, especially made from materials such as glass or metal, can have values slightly > 1.0 but going too high can create unnatural-sounding resonances.

Default values of material or relative amplitude can be overwritten in the `impact_sound_command = p.get_impact_sound_command(...)` command. 

See the `Python/example_controllers/impact_sounds.py` for a more detailed example.

### Supported materials

Currently supported materials: 

- ceramic 
- metal 
- glass 
- hardwood 
- softwood
- cardboard  

More are planned to be added in later releases. 

### Known limitations

#### Settling 

A rapid series of implausible impact sounds  can be created when an object is settling to rest. Until this is fixed more elegantly, it can be prevented by increasing the dynamic friction and decreasing the bounciness of the object in question. This will prevent a large number of low-amplitude bounces.

#### Object size

The current implementation uses sound synthesis parameters measured from small hand-held objects.  Thus the synthetic sounds are plausible for small "plinky" objects, but not for large objects.  Expanding the range of impact sounds to include larger sizes is planned for future releases.

#### Object mass

If you try to create impact sounds for objects with low masses (e.g. 0.01), PyImpact might throw a divide by zero error.

#### Scraping/Rolling sounds

Scraping/rolling sounds are not yet supported. 

#### Audio Drivers

PyImpact requires audio drivers and therefore might not work on most Linux servers.

#### Silence

Very occasionally, a low-resonant object will have a very "unlucky" sampling, resulting in an empty audio byte array. In these cases, `PyImpact.get_impact_sound_command` will return a `do_nothing` command (which does nothing) rather than an audio command.

## Using pre-recorded audio samples

TDW can play arbitrary audio samples as well; simply load a .wav file into memory and send a `play_audio_data` command:

```python
from tdw.controller import Controller
import base64
import wave

wav = wave.open("sound.wav", "rb")
wav_bytes = wav.readframes(wav.getparams().nframes)
wav_str = base64.b64encode(wav_bytes).decode('utf-8')
wav_len = len(wav_bytes)

c = Controller()

# TDW code here to create scene, objects, and start motion.
# ...

if PyImpact.is_valid_collision(collision):
    c.communicate({"$type": "play_audio_data",
                   "id": ball_id,
                   "num_frames": wav_len,
                   "num_channels": 1,
                   "frame_rate": 44100,
                   "wav_data": wav_str,
                   "y_pos_offset": 0.1})
```

