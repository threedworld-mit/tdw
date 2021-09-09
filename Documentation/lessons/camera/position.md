##### Camera Controls

# Move a camera

Translate the avatar (camera)'s position with the [`teleport_avatar_to` command](../../api/command_api.md#teleport_avatar_to):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
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

***

**Next: [Rotate a camera](rotation.md)**

[Return to the README](../../../README.md)

***

Command API:

- [`teleport_avatar_to`](../../api/command_api.md#teleport_avatar_to)

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)

