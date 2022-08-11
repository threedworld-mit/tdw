##### Physics (PhysX)

# Object physics parameters

So far, we've added objects to a scene in TDW like this:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                object_id=object_id,
                                position={"x": 0, "y": 0, "z": 0},
                                rotation={"x": 0, "y": 0, "z": 0},
                                library="models_core.json")])
```

But this usually sets unrealistic physics parameters for an object.

Every object in TDW has additional the following additional physics parameters:

- Mass
- Dynamic friction
- Static friction
- Bounciness
- Kinematic state

Dynamic friction, static friction, and bounciness don't have precise real-world analogues. They are defined in PhysX by the object's [physic material](https://docs.unity3d.com/Manual/class-PhysicMaterial.html).

The object's kinematic state determines whether it will respond to physics. Other objects will respond to kinematic objects. This can be useful for large objects or objects "attached" to a wall such as a cabinet, where you don't want the object to move but you do want it to affect other objects.

## Default physics values and `get_add_physics_object()`

To apply default physics values to objects, the `Controller` class includes a wrapper function: [`get_add_physics_object()`](../../python/controller.md). This is similar to `Controller.get_add_object()` but there is a key difference: This controller returns a *list* of commands rather than a *single* command. **You must add this list of commands to an existing list via *extend* rather than *append*:**

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]

# Add a list of commands.
commands.extend(c.get_add_physics_object(model_name="iron_box",
                                         object_id=object_id,
                                         position={"x": 0, "y": 0, "z": 0},
                                         rotation={"x": 0, "y": 0, "z": 0}))
c.communicate(commands)
```

This example does the exact same thing as the previous example, but using only low-level TDW commands:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "add_object", 
                "name": "iron_box", 
                "url": "https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/iron_box", 
                "scale_factor": 1.0, 
                "position": {"x": 0, "y": 0, "z": 0}, 
                "category": "box", 
                "id": object_id}, 
               {"$type": "rotate_object_to_euler_angles", 
                "euler_angles": {"x": 0, "y": 0, "z": 0}, 
                "id": object_id}, 
               {"$type": "set_kinematic_state",
                "id": object_id, 
                "is_kinematic": False, 
                "use_gravity": True}, 
               {"$type": "set_mass",
                "mass": 0.65, 
                "id": object_id},
               {"$type": "set_physic_material",
                "dynamic_friction": 0.45, 
                "static_friction": 0.48, 
                "bounciness": 0.5, 
                "id": object_id}])
```

**Note all objects in TDW have default physics values.** We are continuously assigning default physics values for additional models.

Default physics values and audio values are stored in `DEFAULT_OBJECT_AUDIO_STATIC_DATA`. The keys of the dictionary are model names:

```python
from tdw.physics_audio.object_audio_static import DEFAULT_OBJECT_AUDIO_STATIC_DATA

model_name = "iron_box"
print(model_name in DEFAULT_OBJECT_AUDIO_STATIC_DATA) # True
```

If the model name is not included in `DEFAULT_OBJECT_AUDIO_STATIC_DATA`, the `get_add_physics_object()` function will derive the values by averaging out values from similar objects.

## Non-default physics values and `get_add_physics_object()`

You might want to set non-default physics values for an object for many reasons, including:

- You want to vary the object's behavior per trial
- The object doesn't have explicitly defined default physics values

`Controller.get_add_physics_object()` has optional parameters that can be set. If `default_physics_values=False`, then the function will read the non-default values:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]

commands.extend(c.get_add_physics_object(model_name="iron_box",
                                         object_id=object_id,
                                         position={"x": 0, "y": 0, "z": 0},
                                         rotation={"x": 0, "y": 0, "z": 0},
                                         default_physics_values=False,
                                         mass=0.65,
                                         dynamic_friction=0.45,
                                         static_friction=0.48,
                                         bounciness=0.5,
                                         kinematic=False,
                                         gravity=True))
c.communicate(commands)
```

Given the nature of parameters with default values in Python, it is of course possible to simplify the above example to this:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]

# This uses the default values for position and rotation (0, 0, 0) and for the kinematic state (non-kinematic, gravity-enabled).
commands.extend(c.get_add_physics_object(model_name="iron_box",
                                         object_id=object_id,
                                         default_physics_values=False,
                                         mass=0.65,
                                         dynamic_friction=0.45,
                                         static_friction=0.48,
                                         bounciness=0.5))
c.communicate(commands)
```

## How physics parameters affect an object

[As mentioned previously,](overview.md) PhysX is structured such that once an object starts moving, the physics engine will automatically update its state.

In this example, the controller's behavior is divided into "trials". In each trial, an object is created with random physics values and dropped. We'll use an [`ObjectManager`](../../python/add_ons/object_manager.md) to track whether the object is "sleeping" i.e. it has stopped moving; this will be covered in more depth [in the next document of this tutorial](rigidbodies.md). At the end of the trial, we'll reset the scene by sending [`destroy_object`](../../api/command_api.md#destroy_object).

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
c.communicate(TDWUtils.create_empty_room(12, 12))

# Do a number of trials.
num_trials = 10

# Set the 0 to another number to use a different random seed.
rng = np.random.RandomState(0)

# Add a camera and an object manager.
camera = ThirdPersonCamera(position={"x": 3, "y": 2.5, "z": -1},
                           look_at={"x": 0, "y": 0, "z": 0})
object_manager = ObjectManager(transforms=True, rigidbodies=True)
c.add_ons.extend([camera, object_manager])

# Run the trials.
for i in range(10):
    object_id = c.get_unique_id()
    # Add the object.
    c.communicate(c.get_add_physics_object(model_name="iron_box",
                                           object_id=object_id,
                                           position={"x": 0, "y": 7, "z": 0},
                                           default_physics_values=False,
                                           mass=float(rng.uniform(0.5, 6)),
                                           dynamic_friction=float(rng.uniform(0, 1)),
                                           static_friction=float(rng.uniform(0, 1)),
                                           bounciness=float(rng.uniform(0, 1))))
    done = False
    while not done:
        c.communicate([])
        done = object_manager.rigidbodies[object_id].sleeping
    # Destroy the object.
    c.communicate({"$type": "destroy_object",
                   "id": object_id})
    # Mark the object manager as requiring re-initialization.
    object_manager.initialized = False
c.communicate({"$type": "terminate"})
```

***

**Next: [`Rigidbodies` output data](rigidbodies.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [physics_values.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/physx/physics_values.py) Drop an object with varying physics values and observe its behavior.

Python API:

- [`Controller.get_add_object()`](../../python/controller.md)
- [`Controller.get_add_physics_object()`](../../python/controller.md)
- [`ObjectManager`](../../python/add_ons/object_manager.md)

Command API:

- [`add_object`](../../api/command_api.md#add_object)
- [`rotate_object_to_euler_angles`](../../api/command_api.md#rotate_object_to_euler_angles)
- [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state)
- [`set_mass`](../../api/command_api.md#set_mass)
- [`set_physic_material`](../../api/command_api.md#set_physic_material)
- [`destroy_object`](../../api/command_api.md#destroy_object)

