# TriggerCollisionManager

`from tdw.add_ons.trigger_collision_manager import TriggerCollisionManager`

Listen for trigger collisions between objects.

***

## Fields

- `trigger_ids` A dictionary of trigger colliders. Key = The trigger ID. Value = The object ID.

- `collisions` A list of [`TriggerCollisionEvent`](../collision_data/trigger_collision_event.md) from this frame.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`TriggerCollisionManager()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### add_box_collider

**`self.add_box_collider(object_id, position, scale)`**

**`self.add_box_collider(object_id, position, scale, rotation=None, trigger_id=None)`**

Add a box-shaped trigger collider to an object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the object. |
| position |  Dict[str, float] |  | The position of the trigger collider relative to the parent object. |
| scale |  Dict[str, float] |  | The scale of the trigger collider. |
| rotation |  Dict[str, float] | None | The rotation of the trigger collider in Euler angles relative to the parent object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| trigger_id |  int  | None | The unique ID of the trigger collider. If None, an ID will be automatically assigned. |

_Returns:_  The ID of the trigger collider.

#### add_cylinder_collider

**`self.add_cylinder_collider(object_id, position, scale)`**

**`self.add_cylinder_collider(object_id, position, scale, rotation=None, trigger_id=None)`**

Add a cylinder-shaped trigger collider to an object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the object. |
| position |  Dict[str, float] |  | The position of the trigger collider relative to the parent object. |
| scale |  Dict[str, float] |  | The scale of the trigger collider. |
| rotation |  Dict[str, float] | None | The rotation of the trigger collider in Euler angles relative to the parent object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| trigger_id |  int  | None | The unique ID of the trigger collider. If None, an ID will be automatically assigned. |

_Returns:_  The ID of the trigger collider.

#### add_sphere_collider

**`self.add_sphere_collider(object_id, position, diameter)`**

**`self.add_sphere_collider(object_id, position, diameter, trigger_id=None)`**

Add a sphere-shaped trigger collider to an object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the object. |
| position |  Dict[str, float] |  | The position of the trigger collider relative to the parent object. |
| diameter |  float |  | The diameter of the trigger collider. |
| trigger_id |  int  | None | The unique ID of the trigger collider. If None, an ID will be automatically assigned. |

_Returns:_  The ID of the trigger collider.

#### reset

**`self.reset()`**

Reset this add-on. Call this before resetting a scene.