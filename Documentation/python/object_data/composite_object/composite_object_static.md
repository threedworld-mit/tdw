# CompositeObjectStatic

`from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic`

Static data for a composite object and its sub-objects.

***

## Fields

- `object_id` The ID of the root object.

- `non_machines` [`NonMachineStatic`](sub_object/non_machine_static.md) sub-objects such as puzzle pieces. Key = The sub-object ID.

- `lights` [`LightStatic`](sub_object/light_static.md) sub-objects such as lamp lightbulbs. Key = The sub-object ID.

- `hinges` [`HingeStatic`](sub_object/hinge_static.md) sub-objects such as doors. Key = The sub-object ID.

- `springs` [`SpringStatic`](sub_object/spring_static.md) sub-objects such as an oven door (which has a damper value). Key = The sub-object ID.

- `motors` [`MotorStatic`](sub_object/motor_static.md) sub-objects such as a ceiling fan. Key = The sub-object ID.

- `prismatic_joints` [`PrismaticJointStatic`](sub_object/prismatic_joint_static.md) sub-objects such as a desk drawer. Key = The sub-object ID.

- `sub_object_ids` A flat list of all sub-object IDs.

***

## Functions

#### \_\_init\_\_

**`CompositeObjectStatic(static_composite_objects, object_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| static_composite_objects |  StaticCompositeObjects |  | The `StaticCompositeObjects` output data. |
| object_index |  int |  | The index in `static_composite_objects.get_object_id()`. |

