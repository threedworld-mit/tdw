# EmptyObjectManager

`from tdw.add_ons.empty_object_manager import EmptyObjectManager`

A manager add-on for empty objects.

In TDW, empty objects are typically used to set affordance points on objects, such as the handle of a coffee mug. These affordance points can then be targeted by agents.

This add-on allows you to add your own empty objects to TDW objects and track their positions per `communicate()` call.

***

## Fields

- `empty_objects` The positions of the empty objects. This is updated after every `communicate()` call. Key = Parent object ID. Value = Dictionary. Key = Empty object ID. Value = Empty object position as a numpy array, in world space coordinates.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`EmptyObjectManager(empty_object_positions)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| empty_object_positions |  Dict[int, List[dict] |  | A dictionary of empty object positions. Key = Parent object ID. Value = Positions relative to the parent object's bottom-center. Can be None. |

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

**`self.reset(empty_object_positions)`**

Reset the add-on.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| empty_object_positions |  Dict[int, List[dict] |  | A dictionary of empty object positions. Key = Parent object ID. Value = Positions relative to the parent object's bottom-center. Can be None. |