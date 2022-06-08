##### Semantic States

# Composite objects (objects with affordances)

*Composite objects utilize the PhysX physics engine. If you haven't done so already, please read [the documentation for PhysX in TDW](../physx/physx.md)*.

**Composite objects** are objects in TDW that have multiple "sub-objects". Sub-objects appear in [output data](../core_concepts/output_data.md) as separate objects with separate IDs and [segmentation colors](../visual_perception/id.md).

Composite objects can be:

- Objects with hinged joints such as a fridge with doors
- Objects with hinged motorized joints such as a fan
- Multiple disconnected objects such as a pot with a lid 
- An object with a light source such as a lamp

##  Add a composite object to the scene

Adding a composite object to the scene is exactly the same as adding any other object:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                object_id=c.get_unique_id())])
```

Model `b03_bosch_cbg675bs1b_2013__vray_composite` is a microwave with one sub-object (the door). Note that we needed to set the `object_id` of the *root* object; all sub-objects, in this case the microwave door, will receive random object IDs.

## Composite objects in the model library

Usually, composite objects in the [model library](../core_concepts/objects.md) have a `_composite` suffix in their names. However, a more reliable way to find composite objects is to test the `composite_object` boolean value:

```python
from tdw.librarian import ModelLibrarian

lib = ModelLibrarian()
for record in lib.records:
    if record.composite_object and not record.do_not_use:
        print(record.name)
```

All model records have a `substructure` field; this is *not* indicative of a composite object's structure and describes a totally separate concept in TDW. The "substructure" data reflects the underlying mesh data and is used [when setting the visual materials of an object](../scene_setup_low_level/materials_textures_colors.md); the data otherwise doesn't imply anything about an object's behavior or affordances. A model can have a complex substructure hierarchy while still being a single non-composite object. In TDW, a distinction is made between *sub-meshes* which are included in the substructure data and *sub-objects* which are components of composite objects.

## Machine types

Composite sub-objects have **machine types** that determine their behavior, their output data, and the commands that can be used to adjust them. In the above example, the microwave's door is a *hinge*.

 The following machine types are supported in TDW:

| Machine type    | Behavior                                                     | Example            |
| --------------- | ------------------------------------------------------------ | ------------------ |
| Light           | Can be turned on and off.                                    | A lightbulb        |
| Motor           | Can rotate on a pivot point around an axis by applying a target velocity and a force magnitude. | A ceiling fan      |
| Hinge           | Swings freely on a pivot point around an axis.               | A door             |
| Spring          | Can rotate on a pivot point around an axis by applying a target position. The motion will appear "spring-like". | An oven door       |
| Prismatic Joint | Can move linearly along an axis                              | A chest of drawers |
| None            | (no mechanism)                                               | A pot with a lid   |

## The `CompositeObjectManager` add-on

The [`CompositeObjectManager`](../../python/add_ons/composite_object_manager.md) add-on is a useful wrapper for composite object output data. To use it, add it to `c.add_ons` and add a composite object to the scene:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager

c = Controller()
# Add a composite object manager.
composite_object_manager = CompositeObjectManager()
c.add_ons.append(composite_object_manager)
# Create the scene and add the object.
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="dishwasher_4_composite",
                                object_id=c.get_unique_id())])
for object_id in composite_object_manager.static:
    print(object_id)
    composite_object = composite_object_manager.static[object_id]
    for hinge_id in composite_object.springs:
        print("Hinge ID:", hinge_id)
        hinge = composite_object_manager.static[object_id].springs[hinge_id]
        if hinge.has_limits:
            print("Hinge limits:", hinge.min_limit, hinge.max_limit)
c.communicate({"$type": "terminate"})
```

Output:

```
9662614
Hinge ID: 561661381
Hinge limits: 0.0 90.0
```

### Static data

Static data (data that isn't expected to change per-frame) is cached in `composite_object_manager.static` as a dictionary where the key is the object ID of the root object and the value is a [`CompositeObjectStatic`](../../python/object_data/composite_object/composite_object_static.md).

`CompositeObjectStatic` has dictionaries of each machine type, where the key is the sub-object ID:

| Dictionary         | Data Type                                                    |
| ------------------ | ------------------------------------------------------------ |
| `lights`           | [`LightStatic`](../../python/object_data/composite_object/sub_object/light_static.md) |
| `motors`           | [`MotorStatic`](../../python/object_data/composite_object/sub_object/motor_static.md) |
| `springs`          | [`SpringStatic`](../../python/object_data/composite_object/sub_object/spring_static.md) |
| `hinges`           | [`HingeStatic`](../../python/object_data/composite_object/sub_object/hinge_static.md) |
| `prismatic_joints` | [`PrismaticJointStatic`](../../python/object_data/composite_object/sub_object/prismatic_joint_static.md) |
| `non_machines`     | [`NonMachineStatic`](../../python/object_data/composite_object/sub_object/non_machine_static.md) |

This example prints the sub-object ID of each sub-object; in this case it will just print the ID of the dishwasher door:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager

c = Controller()
composite_object_manager = CompositeObjectManager()
c.add_ons.append(composite_object_manager)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="dishwasher_4_composite",
                                object_id=c.get_unique_id())])
for object_id in composite_object_manager.static:
    composite_object_static = composite_object_manager.static[object_id]
    for sub_object_id in composite_object_static.lights:
        print(composite_object_static.lights[sub_object_id].sub_object_id)
    for sub_object_id in composite_object_static.motors:
        print(composite_object_static.motors[sub_object_id].sub_object_id)
    for sub_object_id in composite_object_static.springs:
        print(composite_object_static.springs[sub_object_id].sub_object_id)
    for sub_object_id in composite_object_static.hinges:
        print(composite_object_static.lights[sub_object_id].sub_object_id)
    for sub_object_id in composite_object_static.prismatic_joints:
        print(composite_object_static.prismatic_joints[sub_object_id].sub_object_id)
    for sub_object_id in composite_object_static.non_machines:
        print(composite_object_static.non_machines[sub_object_id].sub_object_id)
c.communicate({"$type": "terminate"})
```

### Dynamic  data

`composite_object_manager.dynamic` is a dictionary of dynamic data that is updated per-frame. The dictionary key is the root object ID and the value is a [`CompositeObjectDynamic`](../../python/object_data/composite_object/composite_object_dynamic.md).

In this example, we'll add a microwave to the scene but set its initial position high above the floor and its initial pitch angle facing downwards; this will cause the door to open. The controller will then print the angle of the door at the start and end of the simulation:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager

c = Controller()
composite_object_manager = CompositeObjectManager()
c.add_ons.append(composite_object_manager)
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                object_id=object_id,
                                position={"x": 0, "y": 20, "z": 0},
                                rotation={"x": -90, "y": 0, "z": 0})])
# Get the ID of the door.
static = composite_object_manager.static[object_id]
door_id = list(static.hinges)[0]
# Print the initial angle of the door.
angle = composite_object_manager.dynamic[object_id].hinges[door_id].angle
print(angle)
for i in range(200):
    c.communicate([])
# Print the final angle of the door.
angle = composite_object_manager.dynamic[object_id].hinges[door_id].angle
print(angle)
c.communicate({"$type": "terminate"})
```

Output:

```
0.018078269436955452
38.08620834350586
```

`CompositeObjectDynamic` has dictionaries for only *certain* machine types; some machine types, such as non-machines, don't have specialized dynamic states. Note that if you want to receive the position, velocity, etc. of a composite-sub object, send standard object data commands such as [`send_transforms`](../../api/command_api.md#send_transforms) or use an [`ObjectManager`](../../python/add_ons/object_manager.md).

| Dictionary | Data type                                                    |
| ---------- | ------------------------------------------------------------ |
| `lights`   | [`LightDynamic`](../../python/object_data/composite_object/sub_object/light_dynamic.md) |
| `hinges`   | [`HingeDynamic`](../../python/object_data/composite_object/sub_object/hinge_dynamic.md) |

`hinges` contains data for all motors, springs and hinges, because the dynamic data (angle and velocity) is the same for all of these machine types.

### Reset

Call `composite_object_manager.reset()` whenever [resetting a scene](../scene_setup_high_level/reset_scene.md).

You can destroy composite objects with [`destroy_object`](../../api/command_api.md#destroy_object); this will destroy the root object and all of its sub-objects.

### Low-level description

When a scene is initialized, `CompositeObjectManager` sends [`send_static_composite_objects`](../../api/command_api.md#send_static_composite_objects) to receive [`StaticCompositeObjects`](../../api/output_data.md#StaticCompositeObjects) output data and caches it as a list of [`CompositeObjectStatic`](../../python/object_data/composite_object/composite_object_static.md) data objects. It also sends [`send_dynamic_composite_objects`](../../api/command_api.md#send_dynamic_composite_objects) to receive [`DynamicCompositeObjects`](../../api/output_data.md#DynamicCompositeObjects) per-frame and temporarily save it as a list of [`CompositeObjectDynamic`](../../python/object_data/composite_object/composite_object_dynamic.md) data objects.

## Manipulating composite objects

### Lights

- Turn lights on and off with [`set_sub_object_light`](../../api/command_api.md#set_sub_object_light).

### Motors

In general, you shouldn't adjust the motor force or hinge limits because these are static values. Setting the target velocity will make the motor start to move, assuming that it has a non-zero force: 

- Set the maximum motor force with [`set_motor_force`](../../api/command_api.md#set_motor_force). This is normally considered static data and won't update `composite_object_manager.static[object_id].motors[motor_id].force`
- Set the hinge limits with [`set_hinge_limits`](../../api/command_api.md#set_hinge_limits) (in the build, "motor" is a sub-category of "hinge"). This is normally considered static data and won't update `composite_object_manager.static[object_id].motors[motor_id].min_limit` or `composite_object_manager.static[object_id].motors[motor_id].max_limit`

- Set the target velocity (degrees per second) with [`set_motor_target_velocity`](../../api/command_api.md#set_motor_target_velocity). This is a dynamic property that will affect `composite_object_manager.static[object_id].motors[motor_id].velocity` and `composite_object_manager.static[object_id].motors[motor_id].angle`

### Springs

In general, you shouldn't adjust the spring force. You *can* safely adjust the damper but you usually won't need to. Setting the target position will make the spring start to move, assuming that it has a non-zero force:

- Set the spring damper value with [`set_spring_damper`](../../api/command_api.md#set_spring_damper). The damper value affects how freely the spring will swing. This is normally considered static data and won't update `composite_object_manager.static[object_id].springs[spring_id].damper`
- Set the spring force with [`set_spring_force`](../../api/command_api.md#set_spring_force). A non-zero force will allow the joint to move when a target position is set. This is normally considered static data and won't update `composite_object_manager.static[object_id].springs[spring_id].force`
- Set the hinge limits with [`set_hinge_limits`](../../api/command_api.md#set_hinge_limits) (in the build, "spring" is a sub-category of "hinge"). This is normally considered static data and won't update `composite_object_manager.static[object_id].springs[spring_id].min_limit` or `composite_object_manager.static[object_id].springs[spring_id].max_limit`
- Set the target position (angle in degrees) with [`set_spring_target_position`](../../api/command_api.md#set_spring_target_position). This is a dynamic property that *will* affect `composite_object_manager.static[object_id].springs[spring_id].velocity` and `composite_object_manager.static[object_id].springs[spring_id].angle`

### Hinges

- Set the hinge limits with [`set_hinge_limits`](../../api/command_api.md#set_hinge_limits). This is normally considered static data and won't update `composite_object_manager.static[object_id].hinges[hinge_id].min_limit` or `composite_object_manager.static[object_id].hinges[hinge_id].max_limit`

## Kinematic states

If you send [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state) for a composite object, the command will only affect the [kinematic state](../physx/physics_objects.md) of the top-level object. To set the state for the top-level object *and* all sub-objects, send  [`set_composite_object_kinematic_state`](../../api/command_api.md#set_composite_object_kinematic_state):

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

If you call `Controller.get_add_physics_object()` and set the `kinematic` parameter, it will automatically send `set_composite_object_kinematic_state` for composite objects and `set_kinematic_state` for non-composite objects.

The following example is exactly the same as the above example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                                  object_id=object_id,
                                                  kinematic=True))
c.communicate(commands)
```

## General object commands

Sub-objects will respond to TDW commands just like any other object; you can, for example, [apply forces](../physx/forces.md) to individual sub-objects. Sub-objects likewise appear as separate objects in the output data.

In this example, we'll add the microwave to the scene and make it kinematic (as explained above, the door will remain non-kinematic). Then, we'll apply a torque to the door:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Apply a torque to the door of a microwave.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": 1, "y": 1.5, "z": 0.3},
                           look_at={"x": 0, "y": 0, "z": 0})
composite_object_manager = CompositeObjectManager()
c.add_ons.extend([camera, composite_object_manager])
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                                  object_id=object_id,
                                                  kinematic=True))
c.communicate(commands)
# Get the hinge ID.
hinge_id = list(composite_object_manager.static[object_id].hinges.keys())[0]
# Apply a torque to the hinge.
c.communicate({"$type": "apply_torque_to_object",
               "id": hinge_id,
               "torque": {"x": 0.5, "y": 0, "z": 0}})
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result:

![](images/microwave_door.gif)

## Semantic States

It is possible to use composite object output data to determine **semantic states** of objects.

For **lights**, see `composite_object_manager.dynamic[object_id].lights[sub_object_id].is_on`

For **hinges, motors, and springs** it is possible to determine whether an object is "open" by defining an angle threshold; if the current angle is above the threshold, then the object is "open":

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager


class CompositeObjectOpen(Controller):
    """
    Determine when a composite object is "open".
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate(TDWUtils.create_empty_room(12, 12))
        self.composite_object_manager = CompositeObjectManager()
        self.add_ons.append(self.composite_object_manager)

    def trial(self, open_at: float):
        # Reset the composite object manager.
        self.composite_object_manager.reset()
        # Add the object.
        object_id = Controller.get_unique_id()
        self.communicate(Controller.get_add_physics_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                                           object_id=object_id,
                                                           kinematic=True))
        # Get the hinge ID.
        hinge_id = list(self.composite_object_manager.static[object_id].hinges.keys())[0]
        # Apply a torque to the hinge.
        self.communicate({"$type": "apply_torque_to_object",
                          "id": hinge_id,
                          "torque": {"x": 0.5, "y": 0, "z": 0}})
        for i in range(200):
            # Get the angle of the hinge.
            angle = self.composite_object_manager.dynamic[object_id].hinges[hinge_id].angle
            # Check if the hinge is open.
            is_open = angle >= open_at
            if is_open:
                print(f"Microwave door is open on frame {i} at angle {angle}.")
                break
            self.communicate([])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})


if __name__ == "__main__":
    c = CompositeObjectOpen()
    c.trial(open_at=30)
    c.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = CompositeObjectOpen()
    c.trial(open_at=30)
    c.communicate({"$type": "terminate"})
```

Output:

```
Microwave door is open on frame 16 at angle 30.119487762451172.
```

***

**Next: [Grasped objects](grasped.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [composite_object.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/semantic_states/composite_object.py) Demonstration of how to use composite sub-objects with a test model.
- [composite_object_torque.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/semantic_states/composite_object_torque.py) Apply a torque to the door of a microwave.
- [composite_object_open.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/semantic_states/composite_object_open.py) Determine when a composite object is "open".

Python API:

- [`ModelRecord.composite_object`](../../python/librarian/model_librarian.md) True if the record is for a composite object.
- [`ObjectManager`](../../python/add_ons/object_manager.md)
- [`CompositeObjectManager`](../../python/add_ons/composite_object_manager.md)
  - [`CompositeObjectStatic`](../../python/object_data/composite_object/composite_object_static.md)
    - [`LightStatic`](../../python/object_data/composite_object/sub_object/light_static.md)
    - [`MotorStatic`](../../python/object_data/composite_object/sub_object/motor_static.md)
    - [`SpringStatic`](../../python/object_data/composite_object/sub_object/spring_static.md)
    - [`HingeStatic`](../../python/object_data/composite_object/sub_object/hinge_static.md)
    - [`PrismaticJointStatic`](../../python/object_data/composite_object/sub_object/prismatic_joint_static.md)
    - [`NonMachineStatic`](../../python/object_data/composite_object/sub_object/non_machine_static.md)

  - [`CompositeObjectDynamic`](../../python/object_data/composite_object/composite_object_dynamic.md)
    - [`LightDynamic`](../../python/object_data/composite_object/sub_object/light_dynamic.md)
    - [`HingeDynamic`](../../python/object_data/composite_object/sub_object/hinge_dynamic.md)


Command API:

- [`set_sub_object_light`](../../api/command_api.md#set_sub_object_light)
- [`set_motor_force`](../../api/command_api.md#set_motor_force)
- [`set_motor_target_velocity`](../../api/command_api.md#set_motor_target_velocity)
- [`set_spring_target_position`](../../api/command_api.md#set_spring_target_position)
- [`set_spring_damper`](../../api/command_api.md#set_spring_damper)
- [`set_spring_force`](../../api/command_api.md#set_spring_force) 
- [`set_hinge_limits`](../../api/command_api.md#set_hinge_limits)
- [`send_static_composite_objects`](../../api/command_api.md#send_static_composite_objects)
- [`send_dynamic_composite_objects`](../../api/command_api.md#send_dynamic_composite_objects)
- [`send_transforms`](../../api/command_api.md#send_transforms)
- [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state)
- [`set_composite_object_kinematic_state`](../../api/command_api.md#set_composite_object_kinematic_state)
- [`apply_torque_to_object`](../../api/command_api.md#apply_torque_to_object)
- [`destroy_object`](../../api/command_api.md#destroy_object)

Output Data:

- [`CompositeObjectsStatic`](../../api/output_data.md#CompositeObjectsStatic) 
- [`CompositeObjectsDynamic`](../../api/output_data.md#CompositeObjectsDynamic) 