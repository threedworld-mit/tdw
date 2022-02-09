##### Physics (PhysX)

# Composite objects (objects with affordances)

**Composite objects** are objects in TDW that have multiple "sub-objects". Sub-objects are different from [sub-*meshes*](../objects_and_scenes/materials_textures_colors.md) in that they appear in [output data](../core_concepts/output_data.md) as separate objects with separate IDs and [segmentation colors](../visual_perception/id.md).

Composite objects can be:

- Objects with hinged joints such as a fridge with doors
- Objects with hinged motorized joints such as a fan
- Multiple disconnected objects such as a pot with a lid 
- An object with a light source such as a lamp

## Composite objects in the model library

Usually, composite objects in the [model library](../core_concepts/objects.md) have a `_composite` suffix in their names. However, a more reliable way to find composite objects is to test the `composite_object` boolean value:

```python
from tdw.librarian import ModelLibrarian

lib = ModelLibrarian()
for record in lib.records:
    if record.composite_object and not record.do_not_use:
        print(record.name)
```

## Manipulating composite objects

### Specialist sub-object commands

Some sub-objects have specialized commands, depending on which *machine type* they are. To determine the machine type, you must first send [`send_composite_objects`](../../api/command_api.md#send_composite_objects) which returns [`CompositeObjects`](../../api/output_data.md#CompositeObjects) output data:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData,CompositeObjects

c = Controller()
object_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="puzzle_box_composite",
                                       object_id=object_id),
                      {"$type": "send_composite_objects"}])
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "comp":
        composite_objects = CompositeObjects(resp[i])
        # Iterate through each composite object.
        for j in range(composite_objects.get_num()):
            # Get the target composite object.
            if composite_objects.get_object_id(j) == object_id:
                # Iterate through each sub-object.
                for k in range(composite_objects.get_num_sub_objects(j)):
                    sub_object_id = composite_objects.get_sub_object_id(j, k)
                    sub_object_machine_type = composite_objects.get_sub_object_machine_type(j, k)
                    print(sub_object_id, sub_object_machine_type)
    c.communicate({"$type": "terminate"})
```

The "sub-object machine type" determines which API command can be used for this sub-object:

| Machine type        | Behavior                                                     | Example                | Command(s)                                                   |
| ------------------- | ------------------------------------------------------------ | ---------------------- | ------------------------------------------------------------ |
| `"light"`           | Can be turned on and off.                                    | A lightbulb            | [`set_sub_object_light`](../../api/command_api.md#set_sub_object_light) |
| `"motor"`           | Can rotate on a pivot point around an axis by applying a target velocity and a force magnitude. | A helicopter propeller | [`set_motor_force`](../../api/command_api.md#set_motor_force)<br>[`set_motor_target_velocity`](../../api/command_api.md#set_motor_target_velocity)<br/>[`set_hinge_limits`](../../api/command_api.md#set_hinge_limits) |
| `"hinge"`           | Swings freely on a pivot point around an axis.               | A box with a lid       | [`set_hinge_limits`](../../api/command_api.md#set_hinge_limits) |
| `"spring"`          | Can rotate on a pivot point around an axis by applying a target position. The motion will appear "spring-like". | An oven door           | [`set_spring_target_position`](../../api/command_api.md#set_spring_target_position)<br>[`set_spring_damper`](../../api/command_api.md#set_spring_damper)<br>[`set_spring_force`](../../api/command_api.md#set_spring_force)<br>[`set_hinge_limits`](../../api/command_api.md#set_hinge_limits) |
| `"prismatic_joint"` | Can move linearly along an axis                              | A chest of drawers     |                                                              |
| `"none"`            | (no mechanism)                                               | A basket with a lid    |                                                              |

### Kinematic states

If you send [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state) for a composite object, the command will only affect the [kinematic state](physics_objects.md) of the top-level object. To set the state for the top-level object *and* all sub-objects, send  [`set_composite_object_kinematic_state`](../../api/command_api.md#set_composite_object_kinematic_state):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                object_id=object_id),
               {"$type": "set_composite_object_kinematic_state",
                "id": object_id,
                "is_kinematic": True,
                "use_gravity": False,
                "sub_objects": True}])
c.communicate({"$type": "terminate"})
```

### General object commands and kinematic states

Sub-objects will respond to TDW commands just like any other object; you can, for example, [apply forces](forces.md) to individual sub-objects. Sub-objects likewise appear as separate objects in the output data.

In the previous example, we used `set_composite_object_kinematic_state` to uniformly set the kinematic states of *all* sub-objects. In this example, we'll use `CompositeObjects` output data to get the IDs and machine types of each sub-object and set only hinges to be non-kinematic:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, CompositeObjects

"""
Make a composite object kinematic but make its sub-objects non-kinematic.
"""

c = Controller()
# Create the scene and add the object.
object_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                       object_id=object_id),
                      {"$type": "send_composite_objects",
                       "frequency": "once"}])
# Get the composite object IDs. Assign each object a random color.
commands = []
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "comp":
        composite_objects = CompositeObjects(resp[i])
        for j in range(composite_objects.get_num()):
            if composite_objects.get_object_id(j) == object_id:
                # Make the root object kinematic.
                commands.append({"$type": "set_kinematic_state",
                                 "id": object_id,
                                 "is_kinematic": True,
                                 "use_gravity": False})
                # Make the sub-objects non-kinematic.
                for k in range(composite_objects.get_num_sub_objects(j)):
                    machine_type = composite_objects.get_sub_object_machine_type(i, k)
                    if machine_type == "hinge":
                        commands.append({"$type": "set_kinematic_state",
                                         "id": composite_objects.get_sub_object_id(j, k),
                                         "is_kinematic": False,
                                         "use_gravity": True})
c.communicate({"$type": "terminate"})

```

***

**Next: [Skip physics frames](step_physics.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [composite_object.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/physx/composite_object.py) Demonstration of how to use composite sub-objects with a test model.
- [kinematic_composite_object.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/physx/kinematic_composite_object.py) Make a composite object kinematic but make its sub-objects non-kinematic.

Python API:

- [`ModelRecord.composite_object`](../../python/librarian/model_librarian.md) True if the record is for a composite object.

Command API:

- [`set_sub_object_light`](../../api/command_api.md#set_sub_object_light)
- [`set_motor_force`](../../api/command_api.md#set_motor_force)
- [`set_motor_target_velocity`](../../api/command_api.md#set_motor_target_velocity)
- [`set_spring_target_position`](../../api/command_api.md#set_spring_target_position)
- [`set_spring_damper`](../../api/command_api.md#set_spring_damper)
- [`set_spring_force`](../../api/command_api.md#set_spring_force) 
- [`set_hinge_limits`](../../api/command_api.md#set_hinge_limits)
- [`send_composite_objects`](../../api/command_api.md#send_composite_objects)
- [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state)
- [`set_composite_object_kinematic_state`](../../api/command_api.md#set_composite_object_kinematic_state)

Output Data:

- [`CompositeObjects`](../../api/output_data.md#CompositeObjects) 