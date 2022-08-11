##### Physics (Obi)

# `ObiParticles` output data

## Obi particle data

Obi makes a distinction between *actors* and *non-actors*. An actor has an array of *particles* which deform the geometry of the object. 

In this minimal example, the honey fluid is an *actor* and has particle data; the `rh10` model is a *non-actor*.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.cube_emitter import CubeEmitter

c = Controller()
c.communicate(TDWUtils.create_empty_room(12, 12))
fluid_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": 1.2, "y": 1.5, "z": -1.5},
                           look_at={"x": 0, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.create_fluid(fluid="honey",
                 shape=CubeEmitter(),
                 object_id=fluid_id,
                 position={"x": 0, "y": 2.35, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 speed=1)
c.communicate(Controller.get_add_physics_object(model_name="rh10",
                                                object_id=Controller.get_unique_id()))
for i in range(80):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

In TDW, each actor's particle can be sent to the controller. The [`Obi` add-on](../../python/add_ons/obi.md) automatically sends [`send_obi_particles`](../../api/command_api.md#send_obi_particles) and receives [`ObiParticles` output data](../../api/output_data.md#ObiParticles).

Compared to other output data in TDW, `ObiParticles` is difficult to use as-is. In Obi, the organization of the particle data prioritizes speed over ease of use, and that decision is reflected in TDW as well. The `Obi` add-on include a dictionary: `obi.actors`. The key of this dictionary is the ID of an actor and the value is an [`ObiActor`](../../python/obi_data/obi_actor.md), a data class that is better-organized.

This example controller adds a fluid to the scene and prints the positions and velocities of its particles per frame:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.obi_data.fluids.cube_emitter import CubeEmitter

c = Controller()
c.communicate(TDWUtils.create_empty_room(12, 12))
fluid_id = Controller.get_unique_id()
obi = Obi()
c.add_ons.append(obi)
obi.create_fluid(fluid="honey",
                 shape=CubeEmitter(),
                 object_id=fluid_id,
                 position={"x": 0, "y": 2.35, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 speed=1)
c.communicate([])
for i in range(10):
    c.communicate([])
    for actor_id in obi.actors:
        print(obi.actors[actor_id].positions)
        print(obi.actors[actor_id].velocities)
c.communicate({"$type": "terminate"})
```

## Disable particle data

To disable particle data, set `output_data=False` in the `Obi` constructor:

```python
from tdw.add_ons.obi import Obi

obi = Obi(output_data=False)
```

***

**Next: [Colliders and collision materials](colliders_and_collision_materials.md)**

[Return to the README](../../../README.md)

***


Python API:

- [`Obi`](../../python/add_ons/obi.md)
- [`ObiActor`](../../python/obi_data/obi_actor.md)

Command API:

- [`send_obi_particles`](../../api/command_api.md#send_obi_particles)

Output data:

- [`ObiParticles`](../../api/output_data.md#ObiParticles)