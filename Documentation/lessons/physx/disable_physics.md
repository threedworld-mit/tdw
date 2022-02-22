##### Physics (PhysX)

# Disable physics

By default, physics (and the PhysX physics engine) is enabled in TDW.

It is possible to *disable* physics by sending [`simulate_physics`](../../api/command_api.md#simulate_physics):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
camera = ThirdPersonCamera(position={"x": -3, "y": 2.1, "z": 0.5},
                           look_at={"x": 0, "y": 0, "z": 0})
c.add_ons.append(camera)
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "simulate_physics",
             "value": False}]
commands.extend(c.get_add_physics_object(model_name="iron_box",
                                         object_id=c.get_unique_id(),
                                         position={"x": 0, "y": 1, "z": 0}))
c.communicate(commands)

# The model will hang in mid-air.
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Typically, users want to disable physics if they are setting up a scene that involves image capture but not physics. 

Besides the obvious (objects won't move due to physics), there are some other effects of disabling physics:

1. [Collision detection](collisions.md) is disabled.
2. [Raycasts](../semantic_states/raycast.md) and [overlaps](../semantic_states/overlap.md) won't work.

***

**This is the last document in the "Physics (PhysX)" tutorial.**

[Return to the README](../../../README.md)

***

Command API:

- [`simulate_physics`](../../api/command_api.md#simulate_physics)