# CollisionBase

`from tdw.collision_data.collision_base import CollisionBase`

Abstract base class for collision data.

***

## Fields

- `points` The contact point positions.

- `normals` The contact point normals.

- `state` The state of the collision.

***

## Functions

#### \_\_init\_\_

**`CollisionBase(collision)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision |  Union[Collision, EnvironmentCollision] |  | The collision output data. |