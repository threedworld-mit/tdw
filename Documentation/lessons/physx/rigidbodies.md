##### Physics (PhysX)

# `Rigidbodies` output data

Send the command [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies) to receive [`Rigidbodies`](../../api/output_data.md#Rigidbodies) dynamic data (data that changes per-frame such as velocity). Send [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies) to receive  [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies) static data (data that isn't expected to change per-frame such as mass).

`Rigidbodies` output data also contains:

- Object ID
- Velocity (the directional velocity)
- Angular velocity
- Sleeping: [PhysX](physx.md) makes a low-level distinction between objects that are moving and objects that are inert; inert objects are considered "sleeping".

`StaticRigidbodies` output data contains:

- Object ID
- Mass
- Dynamic friction
- Static friction
- Bounciness
- Kinematic state ([whether the object responds to physics](physics_objects.md))

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Rigidbodies, StaticRigidbodies

c = Controller()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       position={"x": 0, "y": 3, "z": 0},
                                       object_id=c.get_unique_id()),
                      {"$type": "send_rigidbodies",
                       "frequency": "always"},
                      {"$type": "send_static_rigidbodies",
                       "frequency": "once"}])

for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "rigi":
        rigi = Rigidbodies(resp[i])
        for j in range(rigi.get_num()):
            object_id = rigi.get_id(j)
            velocity = rigi.get_velocity(j)
            angular_velocity = rigi.get_angular_velocity(j)
            sleeping = rigi.get_sleeping(j)
    elif r_id == "srig":
        srig = StaticRigidbodies(resp[i])
        for j in range(srig.get_num()):
            object_id = srig.get_id(j)
            mass = srig.get_mass(j)
            kinematic = srig.get_kinematic(j)
            dynamic_friction = srig.get_dynamic_friction(j)
            static_friction = srig.get_static_friction(j)
            bounciness = srig.get_bounciness(j)
c.communicate({"$type": "terminate"})
```

## The `ObjectManager` add-on

We've seen the [`ObjectManager` add-on in the Core Concepts documentation.](../core_concepts/output_data.md) If you need to frequently use rigidbody data, you can use the `ObjectManager` which will conveniently sort all rigidbody data by object per frame. If `rigidbodies=True` in the constructor, the `ObjectManager` will send `send_rigidbodies` when it is first initialized and parse `Rigidbodies` data per frame.

Note that in `Rigidbodies` output data, velocity and angular velocity as (x, y, z) tuples, but in the `ObjectManager` these parameters are conveniently converted into numpy arrays.

Static rigidbody data is always cached in `objects_static` regardless of whether `rigidbodies=True`.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager

c = Controller()
c.communicate(TDWUtils.create_empty_room(12, 12))

# Add the object manager.
object_manager = ObjectManager(transforms=True, rigidbodies=True)
c.add_ons.extend([object_manager])
object_id = c.get_unique_id()
# Add the object.
c.communicate(c.get_add_physics_object(model_name="iron_box",
                                       object_id=object_id,
                                       position={"x": 0, "y": 7, "z": 0}))

for o_id in object_manager.objects_static:
    print(o_id, object_manager.objects_static[o_id].mass)

# Let the object fall.
while not object_manager.rigidbodies[object_id].sleeping:
    print(object_manager.rigidbodies[object_id].velocity)
    c.communicate([])
c.communicate({"$type": "terminate"})
```

***

**Next: [`Collision` output data](collisions.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [physics_values.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/physx/physics_values.py) Drop an object with varying physics values and observe its behavior.

Python API:

- [`ObjectManager`](../../python/add_ons/object_manager.md)

Command API:

- [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies)
- [`send_static_rigidbodies`](../../api/command_api.md#send_rsend_static_rigidbodiesigidbodies)

Output Data API:

- [`Rigidbodies`](../../api/output_data.md#Rigidbodies)
- [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies)

