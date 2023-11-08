# ContainerManager

`from tdw.add_ons.container_manager import ContainerManager`

Manage containment events for 'container' objects.

'Containers' can be concave objects such as baskets but they don't have to be. For example, a table surface can be a 'container' and if another object is on that surface, the table is currently 'containing' that object.

An object is 'contained' by a 'container' if it overlaps with a "containment" space, for example the interior of a pot.

***

## Fields

- `events` A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container shape ID (not the object ID). Value = A list of [`ContainmentEvent`](../container_data/containment_event.md) data.

- `container_shapes` A dictionary of container shape IDs. Key = The container shape ID. Value = The object ID.

- `tags` Tags describing each container shape. Key = The container shape ID. Value = [`ContainerTag`](../container_data/container_tag.md).

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ContainerManager()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### get_early_initialization_commands

**`self.get_early_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

These commands are added to the list being sent on `communicate()` *before* any other commands, including those added by the user and by other add-ons.

Usually, you shouldn't override this function. It is useful for a small number of add-ons, such as loading screens, which should initialize before anything else.

_Returns:_  A list of commands that will initialize this add-on.

#### reset

**`self.reset()`**

Reset this add-on. Call this before resetting a scene.