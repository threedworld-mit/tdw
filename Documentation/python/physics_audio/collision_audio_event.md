# CollisionAudioEvent

`from tdw.physics_audio.collision_audio_event import CollisionAudioEvent`

Data for a collision audio event.
Includes collision data as well as the "primary" and "secondary" objects and the type of audio event.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `ROLL_ANGULAR_VELOCITY` | float | If the angular velocity is this or greater, the event is a roll, not a scrape. | `0.5` |
| `IMPACT_AREA_RATIO` | float | If the area of the collision increases by at least this factor during a stay event, the collision is actually an impact. | `5` |
| `IMPACT_AREA_NEW_COLLISION` | float | On a stay event, if the previous area is None and the current area is greater than this, the collision is actually an impact. | `1e-5` |

***

## Fields

- `collision` [The collision data.](../collision_data/collision_base.md)

- `area` The area of the collision contact points.

- `collision_type` [The collision audio event type.](collision_audio_type.md)

- `primary_id` The ID of the primary object.

- `secondary_id` The ID of the secondary object. If this is an environment collision, the value of this field is `None`.

- `magnitude` A value to mark the overall "significance" of the collision event.

- `velocity` The velocity vector.

***

## Functions

#### \_\_init\_\_

**`CollisionAudioEvent(collision, object_0_static, object_0_dynamic, previous_areas)`**

**`CollisionAudioEvent(collision, object_0_static, object_0_dynamic, previous_areas, object_1_static=None, object_1_dynamic=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision |  CollisionBase |  | [The collision data.](../collision_data/collision_base.md) |
| object_0_static |  ObjectAudioStatic |  | [Static data](object_audio_static.md) for the first object. |
| object_0_dynamic |  Rigidbody |  | [Dynamic data](../object_data/rigidbody.md) for the first object. |
| previous_areas |  Dict[int, float] |  | Areas of collisions from the previous frame. |
| object_1_static |  ObjectAudioStatic  | None | [Static data](object_audio_static.md) for the second object. If this is an environment collision, the value of this parameter should be `None`. |
| object_1_dynamic |  Rigidbody  | None | [Dynamic data](../object_data/rigidbody.md) for the second object. If this is an environment collision, the value of this parameter should be `None`. |

