# CollisionObjEnv

`from tdw.collision_data.collision_obj_env import CollisionObjEnv`

A collision between an object and the environment.

***

## Fields

- `floor` True if this is a collision with the floor.

- `points` The contact point positions.

- `normals` The contact point normals.

- `state` The state of the collision.

***

## Functions

#### \_\_init\_\_

**`CollisionObjEnv(collision)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision |  EnvironmentCollision |  | The collision output data. |