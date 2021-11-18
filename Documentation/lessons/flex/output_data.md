##### Physics (Flex)

# `FlexParticles` output data

Flex simulations work by affecting particle field representations of objects in the scene. In TDW, it's possible to receive Flex particle data via  [`send_flex_particles`](../../api/command_api.md#send_flex_particles), which returns [`FlexParticles`](../../api/output_data.md#FlexParticles) output data:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, FlexParticles

c = Controller()
object_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      {"$type": "convexify_proc_gen_room"},
                      {"$type": "create_flex_container"},
                      c.get_add_object(model_name="cube",
                                       library="models_flex.json",
                                       object_id=object_id),
                      {"$type": "set_flex_solid_actor",
                       "id": object_id,
                       "mass_scale": 5,
                       "particle_spacing": 0.125},
                      {"$type": "assign_flex_container",
                       "id": object_id,
                       "container_id": 0},
                      {"$type": "send_flex_particles"}])
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "flex":
        flex = FlexParticles(resp[i])
        for j in range(flex.get_num_objects()):
            print("Object ID", flex.get_id(j))
            print("Particles\n", flex.get_particles(j))
            print("Velocities\n", flex.get_velocities(j))
```

Output:

```
Object ID 5785380
Particles
 [[-0.4375      0.06184745 -0.4375      0.2       ]
 [-0.4375      0.06184745 -0.3125      0.2       ]
 [-0.4375      0.06184745 -0.1875      0.2       ]
 ...
 [ 0.4375      0.93684745  0.1875      0.2       ]
 [ 0.4375      0.93684745  0.3125      0.2       ]
 [ 0.4375      0.93684745  0.4375      0.2       ]]
Velocities
 [[ 0.         -0.09745845  0.        ]
 [ 0.         -0.09745845  0.        ]
 [ 0.         -0.09745845  0.        ]
 ...
 [ 0.         -0.09744954  0.        ]
 [ 0.         -0.09744954  0.        ]
 [ 0.         -0.09744954  0.        ]]
```

- `flex.get_particles(j)` returns a numpy array of particles. The first three elements are the particle's (x, y, z) positional coordinates. The fourth element is the particle's inverse mass.
- `flex.get_velocities(j)` returns a numpy array of (x, y, z) particle velocities.
- The *particle ID* is the index of the particle in either of the arrays.

`FlexParticles` data can be useful for analyzing the physics state of the scene and for [applying forces to Flex objects](forces.md).

As noted in the [previous document](fluid_and_source.md), `FlexParticle` output data isn't available if the simulation contains a fluid or source actor.

***

**Next: [Apply forces to Flex objects](forces.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- In the TDW repo:
  - [flex_particles.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/flex/flex_particles.py) Minimal example of how to receive FlexParticle output data.
  - [chair.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/flex/chair.py) An example of a soft-body chair that returns `FlexParticle` data.
- [tdw_physics](https://github.com/alters-mit/tdw_physics) includes a [`FlexDataset`](https://github.com/alters-mit/tdw_physics/blob/master/tdw_physics/flex_dataset.py) abstract class controller that can be used  to generate datasets of Flex particle data.

Command API:

- [`send_flex_particles`](../../api/command_api.md#send_flex_particles)

Output Data:

- [`FlexParticles`](../../api/output_data.md#FlexParticles)