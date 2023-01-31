##### Clatter

# Overview

*Clatter relies on TDW's audio system. Please read [the documentation for TDW audio.](../audio/overview.md)*

**Clatter can synthesize plausible sounds from physics-driven events.** Given a collision, the mass of the two objects, their "audio materials", the relative velocity, and so on, Clatter will generate a unique sound. Currently, Clatter is capable of generating impact and scrape sounds.

## Architecture

Clatter is a C# library. [Documentation for the C# library can be found here](TODO.html). The Clatter C# library is embedded within the TDW build. There are several TDW commands for interfacing from Python to Clatter.

The `tdw` Python module includes a [`Clatter`](../../python/add_ons/clatter.md) add-on that calls the TDW commands to initialize Clatter in TDW. 

Additionally, Clatter can be used as a [command-line executable](cli.md), which can be used to write .wav files without needing to reference TDW, or to manually generate audio to play in TDW.

In most cases, you'll use the `Clatter` add-on. You might occasionally the command-line executable. It's unlikely you'll ever need to reference the C# codebase or API directly but it may be helpful to read through if you want to better understand how Clatter works.

The rest of this documentation will refer to Clatter interchangeably as either the `Clatter` Python code or the underlying Clatter library.

## Minimal example

To create a Clatter-enabled scene, you must do the following:

- Create a scene with at least one object
- [Add a camera and audio initializer.](../audio/initialize_audio.md)
- Add `Clatter` add-on.
- Let the simulation run.

**For best results, add all objects *and* the Clatter add-on on the same communicate() call.**

This is a minimal example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=c.get_unique_id()))
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 1, "z": -1},
                           look_at={"x": 0, "y": 0.5, "z": 0})
audio_initializer = AudioInitializer(avatar_id="a")
clatter = Clatter()
c.add_ons.extend([camera, audio_initializer, clatter])
c.communicate(commands)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

## Constructor parameters

The `Clatter` add-on has *many* constructor parameters, all of which are optional. You can, for example, set the overall simulation volume (`simulation_amp`), include object-specific override data (`objects`), set the random seed (`random_seed`), and so on. [Read the API documentation for a full list of constructor parameters.](../../python/add_ons/clatter.md)

## How to record Clatter audio

You can record Clatter audio just like you would record any other audio in TDW. [This document explains how to record audio in TDW and includes some examples that use Clatter.](../audio/record_audio.md)

## Clatter and PyImpact

Clatter is an upgrade and replacement of PyImpact. If you're new to TDW, you should always use Clatter instead of PyImpact. If you want to upgrade from PyImpact to Clatter, [read this.](../py_impact/py_impact_and_clatter.md)

***

**Next: [Object audio data](clatter_objects.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [clatter_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/clatter_minimal.py) A minimal example of Clatter.
- [clatter_benchmark.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/clatter_benchmark.py) A simple performance benchmark controller.

Python API:

- [`Clatter`](../../python/add_ons/clatter.md)