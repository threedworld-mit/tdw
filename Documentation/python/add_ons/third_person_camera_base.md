# ThirdPersonCameraBase

`from tdw.add_ons.third_person_camera_base import ThirdPersonCameraBase`

An abstract base class for third-person camera controller add-ons.

***

## Fields

- `avatar_id` The ID of the avatar that (this camera).

- `position` The initial position of the object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.

***

## Functions

#### \_\_init\_\_

**`ThirdPersonCameraBase()`**

**`ThirdPersonCameraBase(avatar_id=None, position=None, rotation=None, fov=None, pass_masks=None, framerate=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | None | The ID of the avatar (camera). If None, a random ID is generated. |
| position |  Dict[str, float] | None | The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| fov |  int  | None | If not None, this is the initial field of view. Otherwise, defaults to 35. |
| pass_masks |  List[str] | None | The pass masks. If None, defaults to `["_img"]`. |
| framerate |  int  | None | If not None, sets the target framerate. |

#### on_send

_(Abstract)_

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

_Returns:_  A list of commands that will initialize this module.

#### previous_commands

**`self.previous_commands(commands)`**

Do something with the commands that were just sent to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that were just sent to the build. |

