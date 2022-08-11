# CompositeObjectDynamic

`from tdw.object_data.composite_object.composite_object_dynamic import CompositeObjectDynamic`

Dynamic data for a composite object and its sub-objects.

Note that not all sub-objects will be in this output data because some of them don't have specialized dynamic properties.
For example, non-machines have dynamic positions, velocities, etc. but these can be found in `Transforms` and `Rigidbodies` data, respectively.

***

## Fields

- `object_id` The ID of the root object.

- `hinges` A dictionary of [`HingeDynamic`](sub_object/hinge_dynamic.md) sub-objects, which includes all hinges, springs, and motors.

- `lights` A dictionary of [`LightDynamic`](sub_object/light_dynamic.md) sub-objects such as lamp lightbulbs.

***

## Functions

#### \_\_init\_\_

**`CompositeObjectDynamic(object_id, hinges, lights)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the root object. |
| hinges |  Dict[int, HingeDynamic] |  | A dictionary of [`HingeDynamic`](sub_object/hinge_dynamic.md) sub-objects, which includes all hinges, springs, and motors. |
| lights |  Dict[int, LightDynamic] |  | A dictionary of [`LightDynamic`](sub_object/light_dynamic.md) sub-objects such as lamp lightbulbs. |

