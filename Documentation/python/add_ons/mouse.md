# Mouse

`from tdw.add_ons.mouse import Mouse`

Listen to mouse movement, button events, and whether the mouse is over an object.

***

## Fields

- `avatar_id` The ID of the avatar.

- `left_button_pressed` If True, the left button was pressed on this frame.

- `left_button_held` If True, the left button was held on this frame (and pressed on a previous frame).

- `left_button_released` If True, the left button was released on this frame.

- `middle_button_pressed` If True, the middle button was pressed on this frame.

- `middle_button_held` If True, the middle button was held on this frame (and pressed on a previous frame).

- `middle_button_released` If True, the middle button was released on this frame.

- `right_button_pressed` If True, the right button was pressed on this frame.

- `right_button_held` If True, the right button was held on this frame (and pressed on a previous frame).

- `right_button_released` If True, the right button was released on this frame.

- `screen_position` The (x, y) pixel position of the mouse on the screen.

- `scroll_wheel_delta` The (x, y) scroll wheel delta.

- `world_position` The (x, y, z) world position of the mouse. The z depth coordinate is derived via a raycast.

- `mouse_is_over_object` If True, the mouse is currently over an object.

- `mouse_over_object_id` If `self.mouse_is_over_object == True`, this is the ID of the object.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Mouse()`**

**`Mouse(avatar_id="a")`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | "a" | The ID of the avatar. This is used to convert the mouse screen position to a world position. |

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