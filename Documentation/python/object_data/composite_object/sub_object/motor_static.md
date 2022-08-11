# MotorStatic

`from tdw.object_data.composite_object.sub_object.motor_static import MotorStatic`

Static data for a motor sub-object of a composite object.

***

## Fields

- `force` The force limit.

- `has_limits` If True, the hinge has angular limits.

- `min_limit` The minimum angle from the hinge's resting position in degrees.

- `max_limit` The maximum angle from the hinge's resting position in degrees.

- `axis` The axis of rotation.

- `sub_object_id` The ID of this sub-object.

- `sub_object_id` The ID of this sub-object.

***

## Functions

#### \_\_init\_\_

**`MotorStatic(static_composite_objects, object_index, sub_object_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| static_composite_objects |  StaticCompositeObjects |  | `StaticCompositeObjects` output data. |
| object_index |  int |  | The object index. |
| sub_object_index |  int |  | The index of this sub-object. |