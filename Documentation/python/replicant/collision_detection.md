# CollisionDetection

`from tdw.replicant.collision_detection import CollisionDetection`

Parameters for how a Replicant handles collision detection.

***

## Fields

- `walls` If True, the Replicant will stop when it collides with a wall.

- `floor` If True, the Replicant will stop when it collides with the floor.

- `objects` If True, the Replicant will stop when it collides with an object unless the is in the `exclude_objects`.

- `avoid` If True, while walking, the Replicant will try to stop *before* colliding with objects.

- `exclude_objects` The Replicant will ignore a collision with any object in this list, *regardless* of whether or not `objects == True` or the mass of the object. Can be None.

- `previous_was_same` If True, the Replicant will stop if the previous action resulted in a collision and was the same sort of action as the current one.

***

## Functions

#### \_\_init\_\_

**`CollisionDetection()`**

**`CollisionDetection(walls=True, floor=False, objects=False, avoid=True, exclude_objects=None, previous_was_same=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| walls |  bool  | True | If True, the Replicant will stop when it collides with a wall. |
| floor |  bool  | False | If True, the Replicant will stop when it collides with the floor. |
| objects |  bool  | False | If True, the Replicant will stop when it collides with an object unless the is in the `exclude_objects`. |
| avoid |  bool  | True | If True, while walking, the Replicant will try to stop *before* colliding with objects. |
| exclude_objects |  List[int] | None | The Replicant will ignore a collision with any object in this list, *regardless* of whether or not `objects == True`. Can be None. |
| previous_was_same |  bool  | True | If True, the Replicant will stop if the previous action resulted in a collision and was the same sort of action as the current one. |

