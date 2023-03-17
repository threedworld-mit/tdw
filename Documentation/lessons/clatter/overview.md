##### Clatter

# Overview

*Clatter relies on TDW's audio system. Please read [the documentation for TDW audio.](../audio/overview.md)*

**Clatter can synthesize plausible sounds from physics-driven events.** Given a collision, the mass of the two objects, their "audio materials", the relative velocity, and so on, Clatter will generate a unique sound. Currently, Clatter is capable of generating impact and scrape sounds.

When using Clatter, please cite  [Traer,Cusimano and McDermott, A perceptually inspired generative model of rigid-body contact sounds, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf) and [Agarwal, Cusimano, Traer, and McDermott, Object-based synthesis of scraping and rolling sounds based on non-linear physical constraints, (DAFx), 2021](http://mcdermottlab.mit.edu/bib2php/pubs/makeAbs.php?loc=agarwal21). 

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

## Architecture

In nearly all cases, you will use the TDW [`Clatter`](../../python/add_ons/clatter.md) add-on to interface with the Clatter library. As with everything else in TDW, the `Clatter` add-on sends commands to the build. Among these, there are three Clatter-specific commands: [`initialize_clatter`](../../api/command_api.md#initialize_clatter), [`clatterize_object`](../../api/command_api.md#clatterize_object), and [`clatterize_robot_joint`](../../api/command_api.md#clatterize_robot_joint). 

These three commands access code from the underlying Clatter C# library, which is embedded in the TDW build. [Documentation for the Clatter library can be found here](https://alters-mit.github.io/clatter/index.html). In TDW, you can't access the Clatter library directly, but it may be helpful to read through the documentation to better understand how Clatter works. For more information regarding how to contribute to Clatter, [read this](contribute.md).

Additionally, Clatter can be used as a [command-line executable](cli.md), to write .wav files without needing to reference TDW, or to manually generate audio to play in TDW.

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

## Clatter and PyImpact

Clatter is an upgrade and replacement of PyImpact. If you're new to TDW, you should always use Clatter instead of PyImpact. If you want to upgrade from PyImpact to Clatter, [read this.](../py_impact/py_impact_and_clatter.md)

***

**Next: [Object audio data](clatter_objects.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [clatter_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/clatter_minimal.py) A minimal example of Clatter.
- [clatter_benchmark.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/clatter_benchmark.py) A simple performance benchmark controller.

Command API:

- [`initialize_clatter`](../../api/command_api.md#initialize_clatter)
- [`clatterize_object`](../../api/command_api.md#clatterize_object)
- [`clatterize_robot_joint`](../../api/command_api.md#clatterize_robot_joint)

Python API:

- [`Clatter`](../../python/add_ons/clatter.md)