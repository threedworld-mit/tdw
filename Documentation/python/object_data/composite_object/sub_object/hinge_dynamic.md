# HingeDynamic

`from tdw.object_data.composite_object.sub_object.hinge_dynamic import HingeDynamic`

Dynamic data for a hinge, motor, or spring sub-object of a composite object.

***

## Fields

- `angle` The angle in degrees of the hinge relative to its resting position.

- `velocity` The angular velocity in degrees per second of the hinge.

- `sub_object_id` The ID of this sub-object.

***

## Functions

#### \_\_init\_\_

**`HingeDynamic(angle, velocity, sub_object_id)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| angle |  float |  | The angle in degrees of the hinge relative to its resting position. |
| velocity |  float |  | The angular velocity in degrees per second of the hinge. |
| sub_object_id |  int |  | The ID of this sub-object. |