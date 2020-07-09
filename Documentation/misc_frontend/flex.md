# NVIDIA Flex Physics


## Overview

NVIDIA  Flex is physics engine for Unity. By default, Unity uses its built-in PhysX engine. This engine is very fast and reliable, but it has a lot of limitations, chief among them being that all objects must be "rigid" (in the documentation for Unity and for TDW, these are "Rigidbodies").

Flex, by contrast, has a much more sophisticated rigid simulation, and can simulate soft bodies, cloth, liquids, etc.

## System Requirements

| OS             | Does Flex work?        |
| -------------- | ---------------------- |
| Windows        | Yes                    |
| Windows Editor | Yes                    |
| OS X           | No                     |
| Ubuntu 16      | Yes                    |
| Ubuntu 18      | No (see "Known Bugs"). |

**Other requirements:**

- Flex offloads its calculations to an NVIDIA GPU; you will want a very powerful GPU (e.g. Titan X).
- _Windows Unity Editor only:_ Make sure that the Windows build settings are enabled.
- _Ubuntu 16 only:_ Install cuda 8 first.

## Known Bugs

**These are NVIDIA bugs, and won't be fixed.**

- Flex leaks memory when destroying objects.
- If you teleport an object with `teleport_flex_object` or `teleport_and_rotate_flex_object`, the build must step through 4 phyiscs frames before the objects starts to move.
- It is very difficult to run Flex on Ubuntu 18 because it is difficult to install cuda 8 correctly.
- Fluids only work in Windows. If you try loading fluids in Ubuntu 16, the screen will flip upside-down and the fluid will be invisible.
- Adding a Flex Source Actor with the `set_flex_source_actor` command disables all particle data for all Flex objects in the scene.

## Usage

To use NVIDIA Flex Physics one first has to create a flex container in a loaded scene.
Then, each object to be subject to Flex Physics needs to be attached a "Flex Actor".

Check out the [Command API documentation](../api/command_api.md) for which arguments the Flex commands exactly take.

### Setting up a Flex Scene

To initialize a Flex scene the following commands need to be executed sequentially:

- `load_scene`
- `create_exterior_walls`
- `convexify_proc_gen_room`
- `create_flex_container`

#### Streamed scenes

By default, the colliders in a [streamed scene](../python/librarian/scene_librarian.md) are not convex, meaning that they won't interact properly with Flex objects. To use a streamed scene in Flex, you need to "convexify" the scene:

```python
from tdw.controller import Controller
from tdw.librarian import SceneLibrarian

record = c.scene_librarian.get_record("building_site")
c = Controller()
c.communicate({"$type": "add_scene",
             "name": record.name,
             "url": record.get_url(),
             "convexify": True}) # This will make the colliders convex.
```

### Adding a Flex Object

One can then load an object into the scene and make it a Flex object, i. e. attach a Flex solid, soft, or cloth actor. It is important to disable regular physics by setting the kinematic state before doing so:

- `add_object`
- `set_kinematic_state`
- `set_flex_solid_actor` / `set_flex_soft_actor` / `set_flex_cloth_actor`
- `assign_flex_container`

**Not all models can be turned into Flex objects.** This information can be found in the [model record: `record.flex`](../python/librarian/model_librarian.md).

### Manipulating Flex Objects

One can then manipulate the created Flex object by dynamically resetting it's mass, scale, teleporting it, rotate it or applying a force to it. Each of the following commands requires the object id as input:

- `resize_flex_object`
- `set_mass_flex_object`
- `teleport_flex_object`
- `rotate_flex_object_to`
- `apply_force_to_flex_object`
- `set_flex_solid_actor` / `set_flex_soft_actor` / `set_flex_cloth_actor`

A force can be either applied to an entire Flex object, in which case `particle_id` should be set to `-1` or to a particular particle of the Flex object, in which case `particle_id` should equal the `id` of the respective particle.

### Requesting Flex Data

`send_flex_particles` sends [`FlexParticles`](../api/output_data.md#FlexParticles) data.

### Bad Example A

1. `load_scene`
2. `create_exterior_walls`
3. `add_object`
4. `set_kinematic_state`
5. `create_solid_flex_actor`
6. `create_flex_container`
7. `assign_flex_container`

Creating a Flex Actor *before* without having a flex container in the scene will throw an error!

### Bad Example B

1. `load_scene`
2. `create_exterior_walls`
3. `create_flex_container`
4. `add_object`
5. `create_solid_flex_actor`
6. `assign_flex_container`

Not setting an object to kinematic *before* creating a Flex actor will lead to *unphysical* behavior!

### Good Example C

1. `load_scene`
2. `create_exterior_walls`
3. `create_flex_container`
4. `add_object`
5. `set_kinematic_state`
6. `create_solid_flex_actor`
7. `assign_flex_container`
8. `send_flex_particles`
9. `apply_force_to_flex_object`
10. ...

The correct way to setup a Flex scene is to first create a Flex container, then add objects and set them to kinematic, and then to create Flex actors for them. One can then start requesting Flex data, and observe how the Flex particle states change as one manipulates the Flex object by for instance applying a force.

### Flex Particle IDs

Some Flex commands such as `apply_forces_to_flex_object_base64` and `set_flexparticle_fixed` require _Flex particle IDs_. These are the indices of the particle data array returned in [`FlexParticles`](../api/output_data.md#FlexParticles).

```python
from tdw.controller import Controller
from tdw.output_data import FlexParticles

c = Controller()

# Your code here.

resp = c.communicate(commands)
for r in resp[:-1]:
    if FlexParticles.get_data_type_id(r) == "flex":
        fp = FlexParticles(r)
        for i in range(fp.get_num_objects()):
            particle_id = -1
            for p in fp.get_particles(i):
                particle_position = p[:-1] # (x, y, z)
                particle_mass = p[3]
                particle_id += 1
```

### Encoding Flex Forces to Base64

`apply_forces_to_flex_object_base64` requires an array of arrays encoded as a base64 string. The array is  arranged as such:

 `forces = [f0_x, f0_y, f0_z, id0, f1_x, f1_y, f1_z, id1 ... ]`

Where `f` values are coordinates for the force vector and `id` values are the particle IDs (see above).

To encode `forces` to base64 correctly, use [`TDWUtils.get_base64_flex_particle_forces`](../python/tdw_utils.md).

## Flex Primitives

TDW includes various "primitive" models with geometry that has been optimized for Flex. See [Model Librarian](../python/librarian/model_librarian.md) for information on how to access these models (use the `models_flex.json` library).

## Flex Fluids

When using Flex fluids (fluid actor or fluid source actor) in combination with other Flex objects (e.g. solid actor or soft actor) add the fluid actors *before* the other actors, otherwise the fluids will not be visible. See the `flex_fluid_object.py` example controller for details.

## Flex Fluid Types

Various fluid types (e.g. water, honey, chocolate etc.) are supported via a) visual materials in the TDW build that affect the color, reflectance etc. of the materials; and b) a JSON file that contains corresponding `viscosity`, `adhesion` and `cohesion` values for these fluid types. The file can be found at: Python/tdw/flex/fluid_types.json.

#### Example usage:

```python
from typing import Dict
from pathlib import Path
import json
from tdw.flex.fluid_type import FluidType

# Your code here.

 ft = FluidTypes()
 
 # Get the dictionary of name,,FluidTypeData
 fluid_types = ft.fluid_types
 
 # Get a list of fluid names (to randomly select a fluid type, for example)
 fluid_type_selection = choice(ft.fluid_type_names)
```

Then reference the appropriate `viscosity`, `adhesion` and `cohesion` values when creating the Flex container (e.g `fluid_types[fluid_type_selection].viscosity`). See [API document](../python/fluid_types.md) for more information.

In addition, when assigning the Flex container to the fluid object use this form of the command (e.g. for water):

```python
{"$type": "assign_flex_container",
"id": fluid_id,
"container_id": 0, 
"fluid_container": True,
"fluid_type": "water"}
```

## Example Controllers

We've included several example controllers that use Flex. See [Example Controllers](../python/example_controllers.md).
