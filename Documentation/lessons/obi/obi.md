##### Physics (Obi)

# Obi - Overview (the `Obi` add-on)

[Obi](http://obi.virtualmethodstudio.com/tutorials/) is a particle physics engine for Unity that is built on top of [PhysX](../physx/physx.md). Unlike PhysX, Obi has deformable objects such as soft bodies, cloth, and fluids.

## The `Obi` add-on

For almost all use-cases, we recommend using the [`Obi` add-on](../../python/add_ons/obi.md). The `Obi` add-on automates a fairly complex initialization process and encapsulates most of the Obi API.

With the `Obi` add-on, initializing a scene is as simple as adding your objects to the scene and adding the add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi

c = Controller()
# Create the Obi add-on.
obi = Obi()
c.add_ons.append(obi)
# Create a scene and add the object.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=Controller.get_unique_id()))
# Send the commands and initialize Obi.
c.communicate(commands)
c.communicate([])
```

In this minimal example, notice that `c.communicate()` is called twice. This is because `Obi` requires 2 `communicate()` frames to initialize. On the first frame, it requests output data to determine which objects, robots, etc. are in the scene and on the second frame it obi-ifies everything that it found.

This controller doesn't actually change behavior in the scene. It merely enables everything--in this case the `rh10` model and the scene floor--for interactions with Obi actors.

## Core concepts of Obi

In Unity, a **GameObject** is a spatial position and rotation that can optionally have additional functionality such as visual meshes or physics colliders. All [objects in TDW](../core_concepts/objects.md) are GameObjects but GameObjects are silently used for lots of other non-visual non-physical purposes in TDW, such as handling data manager classes.

In Obi, a **solver** is a component script that can be attached to a GameObject. At least one solver must be present in the scene in order to use Obi.

An Obi **actor** is the component script that makes a GameObject behave as an Obi object. For example, a *fluid emitter* is a type of Obi actor. Every Obi actor must be assigned a solver.

Objects in a scene that *aren't* Obi actors still require specialized Obi components. In the minimal example above, `rh10` is automatically initialized for Obi by the `Obi` add-on.

The `Obi` add-on does a lot of automated initialization and setup. The other documents in this tutorial will cover what exactly it does and how to override parts of the initialization process.

## Reset Obi

Whenever you [reset a scene](../scene_setup_high_level/reset_scene.md), call `obi.reset()`. This will reinitialize Obi and tell the add-on to search for new objects in the scene.

## Limitations

- At present, only Obi fluids and cloth have been implemented in TDW. Softbody objects will be added soon.
- Robots aren't fully supported in Obi and Magnebots won't work at all. For more information, [read this](robots.md).

## Obi documentation

If you want to learn more about how Obi works on the backend, we recommend reading [the Obi documentation](http://obi.virtualmethodstudio.com/tutorials/).

***

**Next: [Fluids](fluids.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [obi_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/obi/obi_minimal.py) A minimal implementation of Obi.

Python API:

- [`Obi`](../../python/add_ons/obi.md)