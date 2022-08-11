# CollisionObjObj

`from tdw.collision_data.collision_obj_obj import CollisionObjObj`

A collision between two objects.

***

## Fields

- `relative_velocity` The relative velocity of the objects.

- `impulse` The total impulse applied to the pair of objects to resolve the collision.

- `points` The contact point positions.

- `normals` The contact point normals.

- `state` The state of the collision.

***

## Functions

#### \_\_init\_\_

**`CollisionObjObj(collision)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision |  Collision |  | The collision output data. |