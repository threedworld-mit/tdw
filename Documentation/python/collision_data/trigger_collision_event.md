# TriggerCollisionEvent

`from tdw.collision_data.trigger_collision_event import TriggerCollisionEvent`

Data for a trigger collision event.

***

## Fields

- `trigger_id` The ID of the trigger collider.

- `collidee_id` The ID of the collidee object (the object that has the trigger collider).

- `collider_id` The ID of the collider object (the object the collided with the trigger collider).

- `state` The state of the collision.

***

## Functions

#### \_\_init\_\_

**`TriggerCollisionEvent(collision)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision |  TriggerCollision |  | The [`TriggerCollision`](../../api/output_data.md#TriggerCollision) output data. |

