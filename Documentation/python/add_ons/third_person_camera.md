# ThirdPersonCamera

`from tdw.add_ons.third_person_camera import ThirdPersonCamera`

Add a third-person camera to the scene. This includes initialization parameters (position, rotation, etc.) and some basic movement parameters (whether to follow or look at a target),.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller(launch_build=False)
c.start()
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
c.start()
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
c.start()

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

***

## Fields

- `avatar_id` The ID of the avatar that (this camera).

- `position` The initial position of the object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.

- `look_at_target` The target object or position that the camera will look at. Can be None (the camera won't look at a target).

- `follow_object` The ID of the object the camera will try to follow. Can be None (the camera won't follow an object).

- `follow_rotate` If `follow_object` is not None, this determines whether the camera will follow the object's rotation.

***

## Functions

#### \_\_init\_\_

**`ThirdPersonCamera(look_at)`**

**`ThirdPersonCamera(avatar_id=None, position=None, rotation=None, look_at, fov=None, follow_object=None, follow_rotate=False, pass_masks=None, framerate=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | None | The ID of the avatar (camera). If None, a random ID is generated. |
| position |  Dict[str, float] | None | The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| look_at |  Union[int, Dict[str, float] |  | If not None, rotate look at this target every frame. Overrides `rotation`. Can be an int (an object ID) or an `(x, y, z)` dictionary (a position). |
| fov |  int  | None | If not None, this is the initial field of view. Otherwise, defaults to 35. |
| follow_object |  int  | None | If not None, follow an object per frame. The `position` parameter will be treated as a relative value from the target object rather than worldspace coordinates. |
| follow_rotate |  bool  | False | If True, match the rotation of the object. Ignored if `follow_object` is None. |
| pass_masks |  List[str] | None | The pass masks. If None, defaults to `["_img"]`. |
| framerate |  int  | None | If not None, sets the target framerate. |

#### on_communicate

**`self.on_communicate(resp)`**

This is called after commands are sent to the build and a response is received.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

##### get_initialization_commands

**`self.get_initialization_commands()`**

_Returns:_  A list of commands that will initialize this module.

#### previous_commands

**`self.previous_commands(commands)`**

Do something with the commands that were just sent to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that were just sent to the build. |



