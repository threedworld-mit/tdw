# CompositeObjectDynamic

`from tdw.object_data.composite_object.composite_object_dynamic import CompositeObjectDynamic`

Static data for a composite object and its sub-objects.

Note that not all sub-objects will be in this output data because some of them don't have specialized dynamic properties.
For example, non-machines have dynamic positions, velocities, etc. but these can be found in `Transforms` and `Rigidbodies` data, respectively.

***

## Fields

- `object_id` The ID of the root object.

- `lights` [`LightDynamic`](sub_object/light_dynamic.md) sub-objects such as lamp lightbulbs. Key = The sub-object ID.

- `hinges` [`HingeDynamic`](sub_object/hinge_dynamic.md) sub-objects. *This includes the root object's hinges, springs, and motors.* Key = The sub-object ID.

***

## Functions

#### \_\_init\_\_

**`CompositeObjectDynamic(dynamic_composite_objects, object_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| dynamic_composite_objects |  DynamicCompositeObjects |  | The `DynamicCompositeObjects` output data. |
| object_index |  int |  | The index in `dynamic_composite_objects.get_object_id()`. |

