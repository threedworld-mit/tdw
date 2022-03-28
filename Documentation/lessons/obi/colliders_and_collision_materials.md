##### Physics (Obi)

# Colliders and collision materials

In Unity and in TDW, each object has *n* number of [PhysX physics colliders](../physx/physx.md). Obi adds an additional **ObiCollider** component to each PhysX collider object. Each ObiCollider might also have a **ObiCollisionMaterial**, a data class that influences how the collider behaves in a collision event.

In TDW, the  [`Obi` add-on](../../python/add_ons/obi.md) automatically adds Obi colliders and collision materials to each object in the scene. In order to do this, it sends commands requesting output data in order to determine what is in the scene. This process has three broad implications:

1. The `Obi` add-on is only aware of objects that are in the scene when it initializes and won't automatically Obi-fy anything added afterwards.
2. It is possible for the user to manually add Obi colliders to an object after `Obi` initializes by sending the relevant commands.
2. It is possible to override collision material settings within the `Obi` add-on.

## How the `Obi` add-on creates Obi colliders and collision materials

### Objects, robots, and VR rigs

When the `Obi` add-on is initialized or reset, it sends several commands, receives output data, and uses the output data to add Obi colliders on the next frame:

| Command (first frame) | Output Data (second frame) |
| ------- | ----------- |
| [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies) | [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies) |
| [`send_static_robots`](../../api/command_api.md#send_static_rigidbodies) | [`StaticRobot`](../../api/output_data.md#StaticRobot) |
| [`send_static_oculus_touch`](../../api/command_api.md#send_static_oculus_touch) | [`StaticOculusTouch`](../../api/output_data.md#StaticOculusTouch) |

In TDW and Unity, each object has a [physic material](../physx/physics_objects.md). An Obi collision material is similar to a Unity physic material; both data classes have parameters for dynamic and static friction. The `StaticRigidbodies` data includes these values. By default, `Obi` will set the Obi dynamic and static friction to match the PhysX dynamic and static friction, and set all other values to 0. Robots and VR rigs are set to defaults (friction values are 0.3, everything else is 0).

### The floor

Most, but not all, interior scenes in TDW have an explicitly-defined floor. In these scenes, `Obi` adds an Obi collider to the floor and sets its collision material to default parameters (friction values are 0.3, everything else is 0).

## How to override collision material values

In the `Obi` constructor and `reset()` function, there are three parameters that can be set to override collision material values:

- `floor_material` to set the collision material of the floor.
- `object_materials` to set the collision materials of  [objects](../core_concepts/objects.md) and [robots](../robots/overview.md) (key = object or robot ID).
- `vr_material` to set the collision material of a [VR rig](../vr/overview.md).

Each of these parameters uses the [`CollisionMaterial`](../../obi_data/collision_materials/collision_material.md) data class.

In this example, we'll create a floorplan scene with the [`Floorplan`](../../python/add_ons/floorplan.md) add-on. We'll define a very sticky `CollisionMaterial`. Using an [`ObjectManager`](../../python/add_ons/object_manager.md) add-on, we'll get the object IDs of each object in the scene. Using an `Obi` add-on, we'll assign the `CollisionMaterial` to each object:

```python
from tdw.controller import Controller
from tdw.add_ons.floorplan import Floorplan
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.obi import Obi
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial
from tdw.obi_data.collision_materials.material_combine_mode import MaterialCombineMode

c = Controller()
floorplan = Floorplan()
object_manager = ObjectManager()
obi = Obi()
c.add_ons.extend([floorplan, object_manager, obi])

# Initialize the scene.
floorplan.init_scene(scene="1a", layout=0)
c.communicate([])

# Define a sticky collision material.
collision_material = CollisionMaterial(dynamic_friction=0.3,
                                       static_friction=0.3,
                                       stickiness=1,
                                       stick_distance=0.1,
                                       stickiness_combine=MaterialCombineMode.average,
                                       friction_combine=MaterialCombineMode.average)
# Get a dictionary of object IDs and collision material.
object_materials = {object_id: collision_material for object_id in object_manager.objects_static}
# Reset Obi and apply the collision material.
obi.reset(floor_material=collision_material,
          object_materials=object_materials)
# Call `communicate()` to update the scene.
c.communicate([])
# End the simulation.
c.communicate({"$type": "terminate"})
```

## How to manually add Obi colliders

The `Obi` add-on automatically sends all of these commands; in most cases, it shouldn't be necessary for you to send them outside of the add-on.

- To add Obi colliders to an [object](../core_concepts/objects.md), send [`create_obi_colliders`](../../api/command_api.md#create_obi_colliders). 
- To set Obi collision materials for an object, send [`set_obi_collision_material`](../../api/command_api.md#set_obi_collision_material). 
- To add Obi colliders to a [robot](../robots/overview.md), send [`create_robot_obi_colliders`](../../api/command_api.md#create_robot_obi_colliders).
- To set Obi collision materials for a robot, send [`set_robot_obi_collision_material`](../../api/command_api.md#set_robot_obi_collision_material).
- To add Obi colliders to a [VR rig](../vr/overview.md), send [`create_vr_obi_colliders`](../../api/command_api.md#create_vr_obi_colliders).
- To set Obi collision materials for a VR rig, send [`set_vr_obi_collision_material`](../../api/command_api.md#set_vr_obi_collision_material).
- To add Obi colliders to the floor, send [`create_floor_obi_colliders`](../../api/command_api.md#create_floor_obi_colliders).
- To set Obi collision materials for the floor, send [`set_floor_obi_collision_material`](../../api/command_api.md#set_floor_obi_collision_material).

***

**Next: [Solvers](solvers.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [sticky_floorplan.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/obi/sticky_floorplan.py) Make a floorplan scene very sticky.

Python API:

- [`Obi`](../../python/add_ons/obi.md)
- Collision materials:
  - [`CollisionMaterial`](../../python/obi_data/collision_materials/collision_material.md)
  - [`MaterialCombineMode`](../../python/obi_data/collision_materials/material_combine_mode.md)
- [`ObjectManager`](../../python/add_ons/object_manager.md)
- [`Floorplan`](../../python/add_ons/floorplan.md)

Command API:

- [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies)
- [`send_static_robots`](../../api/command_api.md#send_static_robots)
- [`send_static_oculus_touch`](../../api/command_api.md#send_static_oculus_touch)
- [`create_obi_colliders`](../../api/command_api.md#create_obi_colliders)
- [`set_obi_collision_material`](../../api/command_api.md#set_obi_collision_material)
- [`create_robot_obi_colliders`](../../api/command_api.md#create_robot_obi_colliders)
- [`set_robot_obi_collision_material`](../../api/command_api.md#set_robot_obi_collision_material)
- [`create_vr_obi_colliders`](../../api/command_api.md#create_vr_obi_colliders)
- [`set_vr_obi_collision_material`](../../api/command_api.md#set_vr_obi_collision_material)
- [`create_floor_obi_colliders`](../../api/command_api.md#create_floor_obi_colliders)
- [`set_floor_obi_collision_material`](../../api/command_api.md#set_floor_obi_collision_material)
- [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies)

Output data:

- [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies)
- [`StaticRobot`](../../api/output_data.md#StaticRobot)
- [`StaticOculusTouch`](../../api/output_data.md#StaticOculusTouch)

