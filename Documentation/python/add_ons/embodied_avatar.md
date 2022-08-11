# EmbodiedAvatar

`from tdw.add_ons.embodied_avatar import EmbodiedAvatar`

An `EmbodiedAvatar` is an avatar with a physical body. The body has a simple shape and responds to physics (just like objects and robots).

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `RENDER_ORDER` | int | The render order. Third person cameras will always render "on top" of any other cameras. | `100` |

***

## Fields

- `transform` [Transform data](../object_data/transform.md) for the avatar.

- `rigidbody` [Rigidbody data](../object_data/rigidbody.md) for the avatar.

- `camera_rotation` The rotation of the camera as an [x, y, z, w] numpy array.

- `is_moving` If True, the avatar is currently moving or turning.

- `avatar_id` The ID of the avatar that (this camera).

- `position` The position of the camera. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`EmbodiedAvatar()`**

**`EmbodiedAvatar(avatar_id=None, position=None, rotation=None, field_of_view=None, color=None, body=AvatarBody.capsule, scale_factor=None, mass=80, dynamic_friction=0.3, static_friction=0.3, bounciness=0.7)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | None | The ID of the avatar. If None, a random ID is generated. |
| position |  Dict[str, float] | None | The initial position of the avatar. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The initial rotation of the avatar. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| field_of_view |  int  | None | The initial field of view. |
| color |  Dict[str, float] | None | The color of the avatar as an `r, g, b, a` dictionary where each value is between 0 and 1. Can be None. |
| body |  AvatarBody  | AvatarBody.capsule | [The body of the avatar.](avatar_body.md) |
| scale_factor |  Dict[str, float] | None | Scale the avatar by this factor. Can be None. |
| mass |  float  | 80 | The mass of the avatar. |
| dynamic_friction |  float  | 0.3 | The dynamic friction coefficient of the avatar. |
| static_friction |  float  | 0.3 | The static friction coefficient of the avatar. |
| bounciness |  float  | 0.7 | The bounciness of the avatar. |

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### apply_force

**`self.apply_force(force)`**

Apply a force to the avatar to begin moving it.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| force |  Union[float, int, Dict[str, float] |  | The force. If float: apply a force along the forward (positive value) or backward (negative value) directional vector of the avatar. If dictionary or numpy array: Apply a force defined by the x, y, z vector. |

#### apply_torque

**`self.apply_torque(torque)`**

Apply a torque to the avatar so that it starts turning.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| torque |  float |  | The torque. Positive value = clockwise rotation. |

#### set_drag

**`self.set_drag()`**

**`self.set_drag(drag=1, angular_drag=0.5)`**

Set the drag of the avatar. Increase this to force the avatar to slow down.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| drag |  float  | 1 | The drag of the rigidbody. A higher drag value will cause the avatar slow down faster. |
| angular_drag |  float  | 0.5 | The angular drag of the rigidbody. A higher angular drag will cause the avatar's rotation to slow down faster. |

#### rotate_camera

**`self.rotate_camera(rotation)`**

Rotate the camera.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| rotation |  Dict[str, float] |  | Rotate the camera by these angles (in degrees). Keys are `"x"`, `"y"`, `"z"` and correspond to `(pitch, yaw, roll)`. |

#### look_at

**`self.look_at(target)`**

Look at a target object or position.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[int, Dict[str, float] |  | The target. If int: an object ID. If a dictionary or numpy array: an x, y, z position. |

#### reset_camera

**`self.reset_camera()`**

Reset the rotation of the camera.