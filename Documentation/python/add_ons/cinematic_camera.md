# CinematicCamera

`from tdw.add_ons.cinematic_camera import CinematicCamera`

Wrapper class for third-person camera controls in TDW. These controls are "cinematic" in the sense that the camera will move, rotate, etc. *towards* a target at a set speed per frame. The `CinematicCamera` class is suitable for demo videos of TDW, but *not* for most actual experiments.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera

c = Controller(launch_build=False)
c.start()
cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0},
                      rotation={"x": 2, "y": 45, "z": 0},
                      move_speed=0.1,
                      rotate_speed=3,
                      focus_speed=0.3)
c.add_ons.append(cam)
c.communicate(TDWUtils.create_empty_room(12, 12))
```

Each function in this class will *start* to move the camera but won't actually send commands (because this is not an `AddOn`, not a `Controller`).

To actually apply changes to the camera and the scene, you need to send commands to the build like you normally would. In this example, the list of commands is empty, but it doesn't have to be:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera

c = Controller(launch_build=False)
c.start()
cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0},
                      rotation={"x": 2, "y": 45, "z": 0},
                      move_speed=0.1,
                      rotate_speed=3,
                      focus_speed=0.3)
c.add_ons.append(cam)

# Set a movement target for the camera. This won't actually send any commands!
cam.move_to_position(target={"x": 1, "y": 2, "z": -0.5})

c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(100):
    c.communicate([])
```

Note that all objects that you want the camera to move to must be in the scene *before* adding the camera:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera

object_id = 0
c = Controller(launch_build=False)
c.start()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box", object_id=object_id)])
cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                      rotation={"x": 2, "y": 45, "z": 0})
c.add_ons.append(cam)

# Look at the target object.
cam.move_to_object(target=object_id, offset_distance=1)
cam.rotate_to_object(target=object_id)

for i in range(500):
    c.communicate([])
```

## Possible motions

- **Move** towards a target object or position
- **Rotate** towards a target quaternion, Euler angles; or rotate to look at a target position or object
- **Focus** towards a target distance or object. Focusing is handled implicitly whenever the camera is rotating towards a target object.

## Stopping motions

There are two ways to stop a camera motion:

1. Call `cam.stop_moving()` or `cam.stop_rotating()`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera

object_id = 0
c = Controller(launch_build=False)
c.start()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box", object_id=object_id)])
cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                      rotation={"x": 2, "y": 45, "z": 0})
c.add_ons.append(cam)

# Look at the target object.
cam.move_to_object(target=object_id, offset_distance=1)
cam.rotate_to_object(target=object_id)

for i in range(20):
    c.communicate([])

# Stop moving and rotating the camera.
cam.stop_rotating()
cam.stop_moving()

for i in range(500):
    c.communicate([])
```

2. Call `cam.motions_are_done(resp)`, which will return a dictionary indicating whether the each type of motion is done:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera

object_id = 0
c = Controller(launch_build=False)
c.start()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box", object_id=object_id)])
cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                      rotation={"x": 2, "y": 45, "z": 0})
c.add_ons.append(cam)

# Look at the target object.
cam.move_to_object(target=object_id, offset_distance=1)
cam.rotate_to_object(target=object_id)

done = False
while not done:
    resp = c.communicate([])
    motions = cam.motions_are_done(resp=resp)
    done = motions["move"] and motions["rotate"]
print("Done!")
c.communicate({"$type": "terminate"})
```

## Output Data

This object requires certain output data, which it will automatically request via `cam.init_commands`. If you're not already requesting this data per frame, you might notice that the simulation runs slightly slower.

The output data will include:

- `Bounds` (for all objects in the scene)
- Avatar data (for all avatars in the scene; for this avatar, it's `AvatarKinematic`)
- `ImageSensors` (for all avatars in the scene)
- `CameraMotionComplete` (for this avatar and any other cinematic cameras, whenever the avatar finishes a motion)

## Saving Images

To save images per frame, include an `ImageCapture` add-on to the Controller:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera
from tdw.add_ons.image_capture import ImageCapture

object_id = 0
c = Controller(launch_build=False)
c.start()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box", object_id=object_id)])
cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                      rotation={"x": 2, "y": 45, "z": 0})
cap = ImageCapture(path="D:/cinematic_camera_demo", avatar_ids=[cam.avatar_id])
c.add_ons.extend([cam, cap])

# Look at the target object.
cam.move_to_object(target=object_id, offset_distance=1)
cam.rotate_to_object(target=object_id)

done = False
while not done:
    resp = c.communicate([])
    motions = cam.motions_are_done(resp=resp)
    done = motions["move"] and motions["rotate"]
print("Done!")
c.communicate({"$type": "terminate"})
```

***

## Fields

- `avatar_id` The ID of the avatar that (this camera).

- `position` The initial position of the object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.

- `move_speed` The directional speed of the camera. This can later be adjusted by setting `self.move_speed`.

- `rotate_speed` The angular speed of the camera. This can later be adjusted by setting `self.rotate_speed`.

- `focus_speed` The speed of the focus of the camera. This can later be adjusted by setting `self.focus_speed`.

***

## Functions

#### \_\_init\_\_

**`CinematicCamera()`**

**`CinematicCamera(avatar_id=None, position=None, rotation=None, fov=None, pass_masks=None, framerate=None, move_speed=0.1, rotate_speed=3, focus_speed=0.3)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | None | The ID of the avatar (camera). If None, a random ID is generated. |
| position |  Dict[str, float] | None | The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| fov |  int  | None | If not None, this is the initial field of view. Otherwise, defaults to 35. |
| pass_masks |  List[str] | None | The pass masks. If None, defaults to `["_img"]`. |
| framerate |  int  | None | If not None, sets the target framerate. |
| move_speed |  float  | 0.1 | The directional speed of the camera. This can later be adjusted by setting `self.move_speed`. |
| rotate_speed |  float  | 3 | The angular speed of the camera. This can later be adjusted by setting `self.rotate_speed`. |
| focus_speed |  float  | 0.3 | The speed of the focus of the camera. This can later be adjusted by setting `self.focus_speed`. |

#### on_communicate

**`self.on_communicate(resp)`**

This is called after commands are sent to the build and a response is received.

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

Start to rotate towards an object (to look at the object).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  int |  | The ID of the target object. |

#### rotate_by_rpy

**`self.rotate_by_rpy(target)`**

Start rotating the camera by the `[roll, pitch, yaw]` angles expressed as an `[x, y, z]` dictionary.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Dict[str, float] |  | The target `[roll, pitch, yaw]` angles from when this function was first called, in degrees. |

#### rotate_to_rotation

**`self.rotate_to_rotation(target)`**

Start rotating to a rotation, expressed as a quaternion dictionary.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Dict[str, float] |  | The target rotation. |

#### stop_rotating

**`self.stop_rotating()`**

Stop rotating towards the current target.

#### motions_are_done

**`self.motions_are_done(resp)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The most recent response from the build. |

_Returns:_  A dictionary of which motions are complete. For example: `{"move": True, "rotate": False, "focus": False}`

#### get_initialization_commands

**`self.get_initialization_commands()`**

_Returns:_  A list of commands that will initialize this module.

#### previous_commands

**`self.previous_commands(commands)`**

Do something with the commands that were just sent to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that were just sent to the build. |



