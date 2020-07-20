# `rube_goldberg.py`

**Jeremy Schwartz
June 2020**

## Overview

Create a "Rube Goldberg machine" from a set of objects that will collide when the first is struck by a ball.
Impact sounds are generated for each collision.

This controller was made as a demonstration of: a) PyImpact's capabilities in generating novel plausible impact sounds for any object; b) constructing a sophisticated physics interaction scenario; and c) doing so in a photorealistic scene.  

Note: The controller supports the running of multiple sequential runs (trials), primarily to illustrate an important aspect of PyImpact's synthesis model -- stochastic sampling. Every call to PyImpact, the sound resonant modes will be randomly sampled and the impacts will sound slightly different. Thus, two different objects in the same scene with the same material will create similar but unique sounds, and running the same scene repeatedly will generate similar but unique sounds each time.

## Requirements

To run this controller, users require access to the "Full" TDW model library: [models_full.json](../../misc_frontend/models_full.md)

## Usage

1. `cd <root>/Python/use_cases/rube_goldberg`
2. `python3 rube_goldberg.py [ARGUMENTS]`
3. `<run build>`

#### Arguments

| Argument | Type | Default | Description      |
| -------- | ---- | ------- | ---------------- |
| `--num`  | str  | 5       | Number of trials |

## How It Works

Scene setup, including the setup for all object components of the "Rube Goldberg machine", is handled through a json file -- `object_setup.json` -- which defines the id number, position, rotation and scale for every object in the scene. Each entry in the file is deserialized into an `_ObjectSetup` object.

Note that all scene objects have also been added to the default audio and material data file
(Python/tdw/py_impact/objects.csv), and all required parameters entered including their masses, audio material used, bounciness and relative amplitudes. See [impact sounds documentation](../../misc_frontend/impact_sounds.md) for additional details. Additionally, physics material parameters are set on several of the objects, to "tune" their behavior when struck, and visual materials are changed on the ball and wooden board to better suit the visuals.  For details on object setup, see the `add_all_objects()` function.

For each trial, we initialize PyImpact and pass in the "master gain" amplitude value. This value must be betweem 0 and 1. The relative amplitudes of all scene objects involved in collisions will be scaled relative to this value.  Objects are added to the scene as described above, and the ball is fired at the "machine" to set off the chain-reaction. Collision data returned from the build is passed to PyImpact, which synthesizes the impact audio data and sends it to the build for playback.



## Known Limitations

- The values in the JSON file defining the setup of the "Rube Goldberg machine", as well as the mass, bounciness etc. values described above, have been carefully "tuned" to get the specific result seen (and heard) when running the controller.  Altering those values will result in different physics and audio behavior; while this can be a useful learning exercise, it is recommended you create a back-up copy of the controller so you can return to the initial, known state of the "Rube Goldberg machine".
- If the "master gain" amplitude value passed into PyImpact is too high, waveform clipping can occur and the resultant audio will be distorted. For this reason, the value used here is considerably smaller than the corresponding value used in the `impact_sounds.py` example controller. Here we have a large number of closely-occuring collisions resulting in a rapid series of "clustered" impact sounds, as opposed to a single object falling from a height. Using a higher value such as the 0.5 used in the example controller will definitely result in unpleasant distortion of the audio.
