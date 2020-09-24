# Impact Sounds in TDW

There are several ways to generate impact sounds in TDW:

1. You can use the [PyImpact class](../python/py_impact.md).  

2. You can use your own audio-samples.

## PyImpact

The PyImpact class contains scripts to synthesize novel plausible impact sounds for any object. The sound synthesis method roughly follows that described in [Traer,Cusimano and McDermott, A PERCEPTUALLY INSPIRED GENERATIVE MODEL OF RIGID-BODY CONTACT SOUNDS, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf). Upon every call the sound resonant modes will be randomly sampled and the impacts will sound slightly different.  Thus, two different objects in the same scene with the same material will create similar but unique sounds.  And the same scene run repeatedly will generate similar but unique sounds at every run.  This is designed to emulate the real world, where tapping the same object repeatedly yields slightly different sounds on each impact.

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

The "resonance" values for objects, as set in `tdw/Python/tdw/py_impact/objects.csv`are guidelines and can be altered by the user if desired. Most objects should have values less than 1.0, and small solid objects (e.g. dominos) would have very small values, around 0.15 or thereabouts. Thin-walled objects, especially made from materials such as glass or metal, can have values slightly > 1.0 but going too high can create unnatural-souding resonances.

Here is a minimal demo of a metal spoon dropped on a glass table using default values.

```python
from tdw.py_impact import PyImpact
from tdw.controller import Controller

c = Controller()
# Initialize PyImpact.
p = PyImpact(initial_amp=0.5)
# Get object properties for two objects.
object_info = p.get_object_info()
obj1 = object_info["spoon1"]
obj2 = object_info["glass_table_round"]


# TDW code here to create scene, objects, and start motion.
# ...

commands = get_commands() # Your code here.

# Listen for collisions and rigidbodies.
commands.extend([{"$type": "send_collisions",
                  "enter": True,
                  "stay": False,
                  "exit": False, 
                  "collision_types": ["obj"]}, # Listen for object-object collisions.
                 {"$type": "send_rigidbodies",
                  "frequency": "always"}])

# If a collision occurs we create sound.
resp = c.communicate(commands)

# Parse the response from the build for collision and rigidbody data.
collisions, environment_collisions, rigidbodies = PyImpact.get_collisions(resp)

if len(collisions) == 0 and PyImpact.is_valid_collision(collision):
    # Create an impact sound command from the output data.
    impact_sound_command = p.get_impact_sound_command(
        collision=collision,
        rigidbodies=rigidbodies,
        target_id=obj2_id,
        target_mat=obj2.material,
        target_amp=obj2.amp,
        other_id=obj1_id,
        other_mat=obj2.material,
        other_amp=obj2.amp)

    # Send audio to TDW.
    resp = c.communicate(impact_sound_command)
```

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

## How to Set Up an Audio Scene

Audio scenes require the following initialization [commands](../api/command_api.md):

- An avatar (via `create_avatar`)
- An _audio sensor_ attached to the avatar (via `add_audio_sensor`)

Additionally, impact sounds require the following types of [Output Data](../api/output_data.md):

- Rigidbodies (via `send_rigidbodies`)
- Collision (via `send_collisions`)

In order for objects to have realistic collisions, you'll probably need to send these commands as well:

- `set_mass` 
- `set_physic_material` (You can use the `ObjectInfo.bounciness` value here; see [PyImpact API](../python/py_impact.md).)

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

