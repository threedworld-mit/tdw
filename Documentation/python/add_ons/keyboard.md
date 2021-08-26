# Keyboard

`from tdw.add_ons.keyboard import Keyboard`

Add keyboard controls to a TDW scene.

For example implementation, see: `tdw/Python/example_controllers/keyboard_controls.py`

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

#### \_\_init\_\_

**`Keyboard(key, commands, function, events)`**

Listen for when a key is pressed and send commands.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| key |  |  | The keyboard key. |
| commands |  |  | Commands to be sent when the key is pressed. |
| function |  |  | Function to invoke when the key is pressed. |
| events |  |  | Listen to these keyboard events for this `key`. Options: `"press"`, `"hold"`, `"release"`. If None, this defaults to `["press"]`. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To call it again, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this module.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### listen

**`self.listen(key, commands)`**

**`self.listen(key, commands, function=None, events=None)`**

Listen for when a key is pressed and send commands.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| key |  str |  | The keyboard key. |
| commands |  Union[dict, List[dict] |  | Commands to be sent when the key is pressed. |
| function |  Callable  | None | Function to invoke when the key is pressed. |
| events |  List[str] | None | Listen to these keyboard events for this `key`. Options: `"press"`, `"hold"`, `"release"`. If None, this defaults to `["press"]`. |

## Functions

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |



