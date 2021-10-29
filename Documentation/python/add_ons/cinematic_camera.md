# CinematicCamera

`from tdw.add_ons.cinematic_camera import CinematicCamera`

Wrapper class for third-person camera controls in TDW. These controls are "cinematic" in the sense that the camera will move, rotate, etc. *towards* a target at a set speed per frame. The `CinematicCamera` class is suitable for demo videos of TDW, but *not* for most actual experiments.

***

## Fields

- `avatar_id` The ID of the avatar that (this camera).

- `position` The position of the camera. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.

- `move_speed` The directional speed of the camera.

- `rotate_speed` The angular speed of the camera.

- `moving` If True, the camera is moving.

- `rotating` If True, the camera is rotating.

***

## Functions

#### \_\_init\_\_

**`CinematicCamera(look_at)`**

**`CinematicCamera(avatar_id=None, position=None, rotation=None, field_of_view=None, move_speed=0.1, rotate_speed=1, look_at, focus_distance=6)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | None | The ID of the avatar (camera). If None, a random ID is generated. |
| position |  Dict[str, float] | None | The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| field_of_view |  int  | None | If not None, set the field of view. |
| move_speed |  float  | 0.1 | The directional speed of the camera. This can later be adjusted by setting `self.move_speed`. |
| rotate_speed |  float  | 1 | The angular speed of the camera. This can later be adjusted by setting `self.rotate_speed`. |
| look_at |  Union[int, Dict[str, float] |  | If not None, the cinematic camera will look at this object (if int) or position (if dictionary). |
| focus_distance |  float  | 6 | The initial focus distance. Ignore if `look_at` is an object ID (in which case the camera will focus on the target object). |

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

#### move_to_position

**`self.move_to_position(target)`**

**`self.move_to_position(relative=False, target)`**

Start moving towards a target position.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| relative |  bool  | False | If True, the target is relative to the current position of the avatar. If False, the target is in absolute worldspace coordinates. |
| target |  Dict[str, float] |  | The target position. |

#### move_to_object

**`self.move_to_object(target)`**

**`self.move_to_object(target, offset_distance=1, min_y=0.25)`**

Start moving towards a target object.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  int |  | The ID of the target object. |
| offset_distance |  float  | 1 | Stop moving when the camera is this far away from the object. |
| min_y |  float  | 0.25 | Clamp the y positional coordinate of the camera to this minimum value. |

#### stop_moving

**`self.stop_moving()`**

Stop moving towards the current target.

#### rotate_to_object

**`self.rotate_to_object(target)`**

Rotate towards an object. This will update if

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  int |  | The ID of the target object. |

#### rotate_to_position

**`self.rotate_to_position(target)`**

Start to rotate towards a position.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Dict[str, float] |  | The target position. |

#### rotate_by_rpy

**`self.rotate_by_rpy(target)`**

Rotate the camera by the `[pitch, yaw, roll]` angles expressed as an `[x, y, z]` dictionary.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Dict[str, float] |  | The target `[pitch, yaw, roll]` angles from when this function was first called, in degrees. |

#### rotate_to_rotation

**`self.rotate_to_rotation(target)`**

Rotate towards a rotation quaternion.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Dict[str, float] |  | The target rotation. |

#### stop_rotating

**`self.stop_rotating()`**

Stop rotating towards the current target.

#### set_focus_distance

**`self.set_focus_distance(target)`**

Set the focus distance.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  float |  | The focus distance. |

#### focus_on_object

**`self.focus_on_object(target)`**

Set the focus distance to the distance from the camera to an object. This will update every frame as the camera or object moves.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  int |  | The object ID. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |



