# FirstPersonAvatar

`from tdw.add_ons.first_person_avatar import FirstPersonAvatar`

An avatar that can be moved via keyboard and mouse controls. This is a subclass of [`Mouse`](mouse.md).

A `FirstPersonAvatar` includes the position of the avatar, and screen and world position of the mouse, the object ID of the object under the mouse (if any), and mouse button events.
You can combine a `FirstPersonAvatar` with [`ImageCapture`](image_capture.md) to receive image data.

***

## Fields

- `transform` The [`Transform`](../object_data/transform.md) of the avatar.

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

**`FirstPersonAvatar()`**

**`FirstPersonAvatar(avatar_id=None, position=None, rotation=0, field_of_view=None, height=1.6, camera_height=1.6, radius=0.5, slope_limit=15, detect_collisions=True, move_speed=1.5, look_speed=50, look_x_limit=45, framerate=60, reticule_size=9)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | None | The ID of the avatar. If None, a random ID is generated. |
| position |  Dict[str, float] | None | The initial position of the avatar. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  float  | 0 | The initial rotation of the avatar in degrees. |
| field_of_view |  int  | None | If not None, set the field of view. |
| height |  float  | 1.6 | The height of the avatar. |
| camera_height |  float  | 1.6 | The height of the avatar's camera. |
| radius |  float  | 0.5 | The radius of the avatar. |
| slope_limit |  float  | 15 | The avatar can only climb slopes up to this many degrees. |
| detect_collisions |  bool  | True | If True, the avatar will collide with other objects. |
| move_speed |  float  | 1.5 | The move speed in meters per second. |
| look_speed |  float  | 50 | The camera rotation speed in degrees per second. |
| look_x_limit |  float  | 45 | The camera rotation limit around the x axis in degrees. |
| framerate |  int  | 60 | The target framerate. |
| reticule_size |  int  | 9 | The size of the camera reticule in pixels. If None, no reticule will be shown. |

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

#### reset

**`self.reset()`**

**`self.reset(position=None, rotation=0, field_of_view=None)`**

Reset the avatar. Call this whenever the scene resets.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Dict[str, float] | None | The initial position of the avatar. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  float  | 0 | The initial rotation of the avatar in degrees. |
| field_of_view |  int  | None | If not None, set the field of view. |