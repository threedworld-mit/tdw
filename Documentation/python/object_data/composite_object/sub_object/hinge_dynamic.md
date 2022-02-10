# HingeDynamic

`from tdw.object_data.composite_object.sub_object.hinge_dynamic import HingeDynamic`

Dynamic data for a hinge, motor, or spring sub-object of a composite object.

***

## Fields

- `sub_object_id` The ID of this sub-object.

- `angle` The angle in degrees of the hinge relative to its resting position.

- `velocity` The angular velocity in degrees per second of the hinge.

***

## Functions

#### \_\_init\_\_

**`HingeDynamic(dynamic_composite_objects, object_index, sub_object_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| dynamic_composite_objects |  DynamicCompositeObjects |  | `DynamicCompositeObjects` output data. |
| object_index |  int |  | The object index. |
| sub_object_index |  int |  | The index of this sub-object. |

