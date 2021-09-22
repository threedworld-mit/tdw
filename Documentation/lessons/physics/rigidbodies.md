##### Physics

# `Rigidbodies` output data

Send the command [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies) to receive [`Rigidbodies` output data](../../api/output_data.md#Rigidbodies):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Rigidbodies

c = Controller()
c.communicate(TDWUtils.create_empty_room(12, 12))

object_id = c.get_unique_id()
commands = c.get_add_physics_object(model_name="iron_box",
                                    object_id=object_id,
                                    position={"x": 0, "y": 7, "z": 0})
commands.append({"$type": "send_rigidbodies",
                 "frequency": "once"})
resp = c.communicate(commands)

for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "rigi":
        rigidbodies = Rigidbodies(resp[i])
        for j in range(rigidbodies.get_num()):
            if rigidbodies.get_id(j) == object_id:
                print(object_id)
                print(rigidbodies.get_mass(j))
                print(rigidbodies.get_kinematic(j))
                print(rigidbodies.get_sleeping(j))
                print(rigidbodies.get_velocity(j))
                print(rigidbodies.get_angular_velocity(j))
c.communicate({"$type": "terminate"})
```

The `send_rigidbodies` command and `Rigidbodies` output data are very similar to [`send_transforms` and `Transforms`](../core_concepts/output_data.md) and [`send_bounds` and `Bounds`](../objects_and_scenes/bounds.md):

- All three commands have a `"frequency"` parameter that can be set to `"once"`, `"always"`, or `"never"`.
- All three output data types are structured around indexed lists that must be iterated through like `for j in range(rigidbodies.get_num()):`

`Rigidbodies` output data contains some data that is static:

- Mass

- Kinematic state ([whether the object responds to physics](physics_objects.md))

`Rigidbodies` output data also contains data that is dynamic (changes per frame):

- Velocity (the directional velocity)
- Angular velocity
- Sleeping: [PhysX](physx.md) makes a low-level distinction between objects that are moving and objects that are inert; inert objects are considered "sleeping".

## The `ObjectManager` add-on

We've seen the [`ObjectManager` add-on in the Core Concepts documentation.](../core_concepts/output_data.md) If you need to frequently use rigidbody data, you can use the `ObjectManager` which will conveniently sort all rigidbody data by object per frame. If `rigidbodies=True` in the constructor, the `ObjectManager` will send `send_rigidbodies` when it is first initialized and parse `Rigidbodies` data per frame.

Note that in `Rigidbodies` output data, velocity and angular velocity as (x, y, z) tuples, but in the `ObjectManager` these parameters are conveniently converted into numpy arrays.

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

- [physics_values.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/physics/physics_values.py) Drop an object with varying physics values and observe its behavior.

Python API:

- [`ObjectManager`](../../python/add_ons/object_manager.md)

Command API:

- [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies)

Output Data API:

- [`Rigidbodies`](../../api/output_data.md#Rigidbodies)

