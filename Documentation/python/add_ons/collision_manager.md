# CollisionManager

`from tdw.add_ons.collision_manager import CollisionManager`

Manager add-on for all collisions on this frame.

***

## Fields

- `obj_collisions` All collisions between two objects that occurred on the frame.
Key = An `IntPair` (a pair of object IDs). Value = [The collision.](../collision_data/collision_obj_obj.md)

- `env_collisions` All collisions between an object and the environment that occurred on the frame.
Key = the object ID. Value = [The collision.](../collision_data/collision_obj_env.md)

***

## Functions

#### \_\_init\_\_

**`CollisionManager()`**

**`CollisionManager(enter=True, stay=False, exit=False, objects=True, environment=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| enter |  bool  | True | If True, listen for collision enter events. |
| stay |  bool  | False | If True, listen for collision stay events. |
| exit |  bool  | False | If True, listen for collision exit events. |
| objects |  bool  | True | If True, listen for collisions between objects. |
| environment |  bool  | True | If True, listen for collisions between an object and the environment. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

#### on_send

**`self.on_send()`**

