# ThirdPersonCamera

`from tdw.add_ons.third_person_camera import ThirdPersonCamera`

Add a third-person camera to the scene. This includes initialization parameters (position, rotation, etc.) and some basic movement parameters (whether to follow or look at a target),.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller(launch_build=False)
cam = ThirdPersonCamera(avatar_id="c",
                        position={"x": 1, "y": 2.2, "z": -0.5},
                        rotation={"x": 0, "y": -45, "z": 0})
c.add_ons.append(cam)
c.communicate(TDWUtils.create_empty_room(12, 12))
```

By itself, a `ThirdPersonCamera` won't capture images (though it will render them on the screen). For image capture, include an `ImageCapture` add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture

c = Controller(launch_build=False)
cam = ThirdPersonCamera(avatar_id="c",
                        position={"x": 1, "y": 2.2, "z": -0.5},
                        rotation={"x": 0, "y": -45, "z": 0})
cap = ImageCapture(path="images", avatar_ids=["c"])
c.add_ons.append(cam)
c.add_ons.append(cap)
c.communicate(TDWUtils.create_empty_room(12, 12))
```

## Third-person cameras and avatars

The `ThirdPersonCamera` is a wrapper class for a standard `A_Img_Caps_Kinematic` TDW avatar. All non-physics avatar commands may be sent for this camera.

In this document, the words "camera" and "avatar" may be used interchangeably.

## Multiple cameras

Unlike most `AddOn` objects, it is possible to add multiple `ThirdPersonCamera`s to the scene:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture

c = Controller(launch_build=False)

# Add two cameras.
cam_0 = ThirdPersonCamera(avatar_id="c0",
                          position={"x": 1, "y": 2.2, "z": -0.5},
                          rotation={"x": 0, "y": -45, "z": 0})
cam_1 = ThirdPersonCamera(avatar_id="c1",
                          position={"x": 2, "y": 1, "z": -5})

# Enable image capture for both cameras.
cap = ImageCapture(path="images", avatar_ids=["c0", "c1"])

c.add_ons.extend([cam_0, cam_1, cap])
c.communicate(TDWUtils.create_empty_room(12, 12))
```

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `RENDER_ORDER` | int | The render order. Third person cameras will always render "on top" of any other cameras. | `100` |

***

## Fields

- `follow_object` The ID of the object the camera will try to follow. Can be None (the camera won't follow an object).

- `follow_rotate` If `follow_object` is not None, this determines whether the camera will follow the object's rotation.

- `avatar_id` The ID of the avatar that (this camera).

- `position` The position of the camera. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ThirdPersonCamera(look_at)`**

**`ThirdPersonCamera(avatar_id=None, position=None, rotation=None, look_at, field_of_view=None, follow_object=None, follow_rotate=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | None | The ID of the avatar (camera). If None, a random ID is generated. |
| position |  Dict[str, float] | None | The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| look_at |  Union[int, Dict[str, float] |  | If not None, rotate look at this target every frame. Overrides `rotation`. Can be an int (an object ID) or an `(x, y, z)` dictionary (a position). |
| field_of_view |  int  | None | If not None, set the field of view. |
| follow_object |  int  | None | If not None, follow an object per frame. The `position` parameter will be treated as a relative value from the target object rather than worldspace coordinates. |
| follow_rotate |  bool  | False | If True, match the rotation of the object. Ignored if `follow_object` is None. |

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

#### teleport

**`self.teleport(position)`**

**`self.teleport(position, absolute=True)`**

Teleport the camera to a new position.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Dict[str, float] |  | The new position of the camera. |
| absolute |  bool  | True | If True, `position` is absolute worldspace coordinates. If False, `position` is relative to the avatar's current position. |

#### rotate

**`self.rotate(rotation)`**

Rotate the camera.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| rotation |  Dict[str, float] |  | Rotate the camera by these angles (in degrees). Keys are `"x"`, `"y"`, `"z"` and correspond to `(pitch, yaw, roll)`. |

#### look_at

**`self.look_at(target)`**

Look at a target position or object. The camera will continue to look at the target until you call `camera.look_at(None)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[int, Dict[str, float] |  | The look at target. Can be an int (an object ID), an `(x, y, z)` dictionary (a position), or None (stop looking at a target). |