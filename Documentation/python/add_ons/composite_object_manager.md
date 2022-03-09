# CompositeObjectManager

`from tdw.add_ons.composite_object_manager import CompositeObjectManager`

Manager add-on for static and dynamic composite object data.

Note that some useful information, such as the positions, rotations, names, of the objects, is not included here. See: [`ObjectManager`](object_manager.md).

***

## Fields

- `static` A dictionary of [`CompositeObjectStatic`](../object_data/composite_object/composite_object_static.md) data that is set when this add-on intializes. Key = The object ID.

- `dynamic` A dictionary of [`CompositeObjectDynamic`](../object_data/composite_object/composite_object_dynamic.md) data that is set per-frame. Key = The object ID.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`CompositeObjectManager()`**

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

#### is_open

**`self.is_open(object_id, sub_object_id)`**

**`self.is_open(object_id, sub_object_id, open_at=30)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the root object. |
| sub_object_id |  int |  | The ID of one of the root object's hinges, motors, or springs. |
| open_at |  float  | 30 | A threshold of 'openness' in degrees. If the sub-object's angle is greater than or equal to this, it is considered 'open'. |

_Returns:_  True if the hinge, motor, or spring is open.

#### reset

**`self.reset()`**

Reset this add-on. Call this when resetting the scene.