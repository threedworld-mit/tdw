##### Physics (Flex)

# Move, rotate, and scale Flex objects

**Always move, rotate, and scale objects *before* sending a Flex actor command.** Flex will act unpredictably if you adjust an object after assigning a Flex actor.

In this example, we'll add an object, then scale it, then assign a Flex actor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "convexify_proc_gen_room"},
               {"$type": "create_flex_container"},
               c.get_add_object(model_name="rh10",
                                object_id=object_id,
                                position={"x": 0, "y": 1, "z": 0}),
               {"$type": "scale_object",
                "id": object_id,
                "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}},
               {"$type": "set_flex_solid_actor",
                "id": object_id,
                "mass_scale": 5,
                "particle_spacing": 0.05},
               {"$type": "assign_flex_container",
                "id": object_id,
                "container_id": 0}])
c.communicate({"$type": "terminate"})
```

This, on the other hand, is a *bad* example. In this example, we add an object, then assign a Flex actor, then scale it. The resulting behavior might be very buggy and strange.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

print("THIS IS A BAD EXAMPLE. DON'T DO IT.")
c = Controller()
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "convexify_proc_gen_room"},
               {"$type": "create_flex_container"},
               c.get_add_object(model_name="rh10",
                                object_id=object_id,
                                position={"x": 0, "y": 1, "z": 0}),
               {"$type": "set_flex_solid_actor",
                "id": object_id,
                "mass_scale": 5,
                "particle_spacing": 0.05},
               {"$type": "assign_flex_container",
                "id": object_id,
                "container_id": 0},
               {"$type": "scale_object",
                "id": object_id,
                "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}}])
c.communicate({"$type": "terminate"})
```

***

**Next: [`FlexParticles` output data](output_data.md)**

[Return to the README](../../../README.md)