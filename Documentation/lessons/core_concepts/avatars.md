# Core concepts: Avatars and cameras

As mentioned [earlier](1.2.2_commands.md), TDW doesn't impose metaphors regarding what an agent is or whether there needs to be one at all.

**Avatars** are a type of agent in TDW but not the only one. The most commonly used avatar is a non-embodied camera; you can think of this avatar as being more or less equivalent to a third-person camera (though the [commands](1.2.2_commands.md) for cameras have slightly different parameters than avatars).

There are embodied avatars, such as the Sticky Mitten Avatar, but these have been deprecated in favor of robotic agents. Embodied avatars are a much older part of TDW than robotics that we've since deprecated. In most cases, you should only use the third-person camera avatar.

To add the third-person camera avatar to the scene:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": "a"}])
```

 ...which will render this image in the build application's window:

![](images/avatar.png)

The avatar is currently at position (0, 0, 0). To move it to a better location, send `teleport_avatar_to`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": "a"},
               {"$type": "teleport_avatar_to",
                "avatar_id": "a",
                "position": {"x": -1, "y": 0.6, "z": 2.4}}])
```

...which will render this image:

![](images/avatar_y.png)

This still isn't a very good image. Let's rotate the avatar's **sensor container** (its camera) for a better view of the scene:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": "a"},
               {"$type": "teleport_avatar_to",
                "avatar_id": "a",
                "position": {"x": -1, "y": 5.7, "z": -3.8}},
               {"$type": "rotate_sensor_container_by",
                "axis": "pitch",
                "angle": 26,
                "avatar_id": "a"},
               {"$type": "rotate_sensor_container_by",
                "axis": "yaw",
                "angle": -15,
                "avatar_id": "a"}])
```

...which will render this image:

![](images/avatar_rot.png)

## `TDWUtils.create_avatar()`

`TDWUtils` includes a helpful wrapper function for creating avatars: [`create_avatar()`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/tdw_utils.md#create_avataravatar_typea_img_caps_kinematic-avatar_ida-positionnone-look_atnone---listdict):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_type="A_Img_Caps_Kinematic",
                                       position={"x": -1, "y": 5.7, "z": -3.8},
                                       look_at={"x": 0, "y": 1, "z": 0}))
c.communicate(commands)
```

...which will render this image:

![](images/avatar_tdwutils.png)

## Moving and rotating the avatar

To move and rotate the avatar, simply teleport and rotate it by small increments per frame:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

# Note that in this example, the `avatar_id` parameters are missing. That's because they all default to "a".
c = Controller()
c.start()
y = 5.7
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": "a"},
               {"$type": "teleport_avatar_to",
                "position": {"x": -1, "y": y, "z": -3.8}},
               {"$type": "rotate_sensor_container_by",
                "axis": "pitch",
                "angle": 26},
               {"$type": "set_target_framerate",
                "framerate": 30}])
for i in range(20):
    y += 0.1
    c.communicate([{"$type": "rotate_sensor_container_by",
                   "axis": "yaw",
                   "angle": 2},
                   {"$type": "teleport_avatar_to",
                    "position": {"x": -1, "y": y, "z": -3.8}}])
c.communicate({"$type": "terminate"})
```

...which moves the avatar like this:

![](images/avatar_move.gif)

## The `ThirdPersonCamera` add-on

**Add-ons** in TDW are objects that can be added to a controller and act as wrappers for the Command API. They will inject commands at every `communicate()` call based on the output data from the build.

The [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md) add-on will add a third-person camera avatar to the scene. Unlike the avatar created by `TDWUtils.create_avatar()` this add-on has per-frame camera controls.

This controller does the exact same thing as the previous example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
c.start()

# Create the third-person camera.
cam = ThirdPersonCamera(avatar_id="a",
                        position={"x": -1, "y": 5.7, "z": -3.8},
                        rotation={"x": 26, "y": 0, "z": 0})

# Append the third-person camera add-on.
c.add_ons.append(cam)
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 30}])
for i in range(20):
    # Raise the camera up by 0.1 meters.
    cam.teleport(position={"x": 0, "y": 0.1, "z": 0},
                 absolute=False)
    # Rotate around the yaw axis by 2 degrees.
    cam.rotate(rotation={"x": 0, "y": 2, "z": 0})
    c.communicate([])
c.communicate({"$type": "terminate"})
```

## The `CinematicCamera` add-on

The [`CinematicCamera`](../../python/add_ons/cinematic_camera.md)  add-on is like the `ThirdPersonCamera` add-on but it's designed to smoothly rotate and move the camera. This is useful for making nice-looking videos but not that useful if you want to capture still images at various angles:

This example approximately equivalent to the previous two examples except that it will "smooth" out the movement and rotation of the camera by slowing it down at the start and end of the motion.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera

c = Controller()
c.start()

# Create the cinematic camera.
cam = CinematicCamera(avatar_id="a",
                      position={"x": -1, "y": 5.7, "z": -3.8},
                      rotation={"x": 26, "y": 0, "z": 0})

# Append the cinematic camera add-on.
c.add_ons.append(cam)
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 30}])
# Move and rotate the camera.
cam.move_to_position(target={"x": -1, "y": 7.7, "z": -3.8})
cam.rotate_by_rpy(target={"x": 0, "y": 20, "z": 0})
for i in range(20):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

## A few words regarding add-ons, wrapper functions and classes

In this document, we've referred several times to "wrapper" functions and objects. These bits of code "wrap" around the Command API; they *can't* do anything that you couldn't do just by sending TDW commands to the build.

For example, this is the code of `ThirdPersonCamera.rotate(rotation)`. Note that all it is doing is appending three `rotate_sensor_container_by` commands:

```python
def rotate(self, rotation: Dict[str, float]) -> None:
    for q, axis in zip(["x", "y", "z"], ["pitch", "yaw", "roll"]):
        self.commands.append({"$type": "rotate_sensor_container_by",
                              "axis": axis,
                              "angle": rotation[q],
                              "avatar_id": self.avatar_id})
```

***

**Next: [Objects](objects.md)**

Example controller: [third_person_camera.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/third_person_camera.py)

Python API:

- [`TDWUtils.create_avatar(avatar_type, position, look_at)`](../../python/tdw_utils.md)
- [`AddOn`](../../python/add_ons/add_on.md) (abstract base class for all add-ons)
-  [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md) 
- [`CinematicCamera`](../../python/add_ons/cinematic_camera.md)

Command API:

- [`create_avatar`](../../api/command_api.md#create_avatar)
- [`teleport_avatar_to`](../../api/command_api.md#teleport_avatar_to)
- [`rotate_sensor_container_by`](../../api/command_api.md#rotate_sensor_container_by)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)

[Return to the README](../../README.md)