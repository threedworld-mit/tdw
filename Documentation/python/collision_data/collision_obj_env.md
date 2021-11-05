# CollisionObjEnv

`from collision_data.collision_obj_env import CollisionObjEnv`

A collision between an object and the environment.

***

## Fields

- `points` The contact point positions.

- `normals` The contact point normals.

- `state` The state of the collision.

- `floor` True if this is a collision with the floor.

***

## Functions

#### \_\_init\_\_

**`CollisionObjEnv(collision)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision |  EnvironmentCollision |  | The collision output data. |

