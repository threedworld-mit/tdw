##### Visual Perception

# Camera position and rotation

## Translate the camera

Translate the avatar (camera)'s position with the [`teleport_avatar_to` command](../../api/command_api.md#teleport_avatar_to):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
commands = [TDWUtils.create_empty_room(12, 12)]
x = 0
y = 1.6
z = 0
commands.extend(TDWUtils.create_avatar(position={"x": x, "y": y, "z": z},
                                       avatar_id="a"))
c.communicate(commands)
for i in range(30):
    z += 0.05
    c.communicate({"$type": "teleport_avatar_to",
                   "avatar_id": "a",
                   "position": {"x": x, "y": y, "z": z}})
c.communicate({"$type": "terminate"})
```

Or, with a `ThirdPersonCamera`, call `teleport(position)`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
c.start()
x = 0
y = 1.6
z = 0
cam = ThirdPersonCamera(position={"x": x, "y": y, "z": z})
c.add_ons.append(cam)
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(30):
    z += 0.05
    cam.teleport(position={"x": x, "y": y, "z": z})
    c.communicate([])
c.communicate({"$type": "terminate"})
```

## Rotating the avatar vs. rotating the sensor container

The non-embodied avatar object is structured like this:

```
Avatar
....SensorContainer (camera)
```

This is a holdover from earlier versions of TDW that emphasized using embodied avatars. For this reason, the Command API includes commands to rotate the avatar and, separately, to rotate the sensor container. The avatar rotation commands can be considered more or less deprecated; you should translate the avatar with `teleport_avatar_to` and rotate the camera with sensor container commands.

## Rotate by angles

- [`rotate_sensor_container_by`](../../api/command_api.md#rotate_sensor_container_by) rotates the avatar's camera (sensor container) by a given angle and axis.
- [`rotate_sensor_container_to`](../../api/command_api.md#rotate_sensor_container_to) rotates the avatar's camera to a given quaternion.
- [`reset_sensor_container_rotation`](../../api/command_api.md#reset_sensor_container_rotation) resets the rotation of the avatar's camera to its default rotation.

**TODO ADD-ONS**

## Rotate to look at

- [`look_at`](../../api/command_api.md#look_at)
-  look_at_avatar
-  look_at_position

***

Command API:

- [`teleport_avatar_to`](../../api/command_api.md#teleport_avatar_to)

Python API:

- [`ThirdPersonCamera.teleport(position, absolute=True)`](../../python/add_ons/third_person_camera.md) Translate the third-person camera to a new position.

