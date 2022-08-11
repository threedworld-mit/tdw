##### Camera Controls

# Rotate a camera

## Rotating the avatar vs. rotating the sensor container

The non-embodied avatar object is structured like this:

```
Avatar
....SensorContainer (camera)
```

This is a holdover from earlier versions of TDW that emphasized using embodied avatars. For this reason, the Command API includes commands to rotate the avatar and, separately, to rotate the sensor container. The avatar rotation commands can be considered more or less deprecated; you should translate the avatar with `teleport_avatar_to` and rotate the camera with sensor container commands.

## Rotate the sensor container (camera)

### Rotate the camera by an angle and axis

Option 1: Send the [`rotate_sensor_container_by` command:](../../api/command_api.md#rotate_sensor_container_by) 

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()

object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             library="models_core.json",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id)]
commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 1.6, "z": -0.6},
                                       look_at={"x": 1, "y": 0, "z": -0.5},
                                       avatar_id="a"))
c.communicate(commands)
c.communicate({"$type": "rotate_sensor_container_by",
               "axis": "pitch",
               "angle": -10,
               "avatar_id": "a"})
c.communicate([])
c.communicate({"$type": "terminate"})
```

Option 2: With a [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md), call the `rotate()` function (which internally creates a `rotate_sensor_container_by` command):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()

object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id)
c.add_ons.append(cam)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                library="models_core.json",
                                position={"x": 1, "y": 0, "z": -0.5},
                                object_id=object_id)])
# Stop following the target object.
cam.look_at_target = None
cam.rotate({"x": -10, "y": 0, "z":0})
c.communicate([])
c.communicate({"$type": "terminate"})
```

### Rotate the camera to a quaternion

Send the [`rotate_sensor_container_to` command](../../api/command_api.md#rotate_sensor_container_to) or, with a `ThirdPersonCamera`, call `rotate` but supply an (x, y, z, w) dictionary instead of an (x, y, z) dictionary.

Quaternions are difficult to use, but they're the only reliable way to repeatedly rotate an object; all other rotation commands such as `rotate_sensor_container_by` convert parameters specified by the user into quaternions.

It is often use to rotate the camera to a quaternion if you want to store the camera's rotation and apply it later. To get the current quaternion of the camera, send [`send_image_sensors`](../../api/command_api.md#send_image_sensors) which will return [`ImageSensors` output data](../../api/output_data.md#ImageSensors):

```python
from typing import List
import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, ImageSensors


class RotateSensorContainerToExample(Controller):
    def get_random_rotation(self) -> List[dict]:
        commands = []
        for axis in ["pitch", "yaw", "roll"]:
            commands.append({"$type": "rotate_sensor_container_by",
                             "axis": axis,
                             "angle": random.uniform(-15, 15),
                             "avatar_id": "a"})
        return commands

    def run(self):
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 1.6, "z": -0.6},
                                               avatar_id="a"))
        # Set a random initial rotation.
        commands.extend(self.get_random_rotation())
        # Request image sensors data.
        commands.append({"$type": "send_image_sensors",
                         "frequency": "once"})
        resp = self.communicate(commands)
        initial_rotation = (0, 0, 0, 0)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imse":
                imse = ImageSensors(resp[i])
                if imse.get_avatar_id() == "a":
                    initial_rotation = imse.get_sensor_rotation(0)
        # Set a random rotation.
        self.communicate(self.get_random_rotation())
        # Reset to the initial rotation.
        self.communicate({"$type": "rotate_sensor_container_to",
                          "rotation": TDWUtils.array_to_vector4(initial_rotation), 
                          "avatar_id": "a"})
        self.communicate({"$type": "terminate"})
        
if __name__ == "__main__":
    c = RotateSensorContainerToExample()
    c.run()
```

### Reset the camera rotation

Reset the camera rotation to its neutral position with the [`reset_sensor_container_rotation`](../../api/command_api.md#reset_sensor_container_rotation):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 1.6, "z": -0.6},
                                       avatar_id="a"))
c.communicate(commands)
c.communicate({"$type": "rotate_sensor_container_by",
               "axis": "pitch",
               "angle": 70,
               "avatar_id": "a"})
c.communicate([{"$type": "reset_sensor_container_rotation",
                "avatar_id": "a"}])
c.communicate({"$type": "terminate"})
```

## Rotate the camera to look at something

Send [`look_at`](../../api/command_api.md#look_at) to rotate the camera such that a target object is at the center of the image (the viewport). Set the `"use_centroid"` to True to look at the center of the object rather than its bottom-center pivot:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()

object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             library="models_core.json",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id)]
commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 1.6, "z": -0.6},
                                       avatar_id="a"))
commands.append({"$type": "look_at",
                 "object_id": object_id,
                 "use_centroid": True,
                 "avatar_id": "a"})
c.communicate(commands)
c.communicate({"$type": "terminate"})
```

Send [`look_at_position`](../../api/command_api.md#look_at_position) to rotate the camera such that a target position  is at the center of the image (the viewport). This is automatically called whenever we set the `look_at` parameter of `TDWUtils.create_avatar()`. This example creates an avatar and points the camera at a position without using the wrapper function:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()

object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": "a"},
               {"$type": "look_at_position",
                "avatar_id": "a",
                "position": {"x": 0, "y": 10, "z": 0}}])
c.communicate({"$type": "terminate"})
```

The `ThirdPersonCamera` wraps both of these commands (`look_at` and `look_at_position` in a function: `camera.look_at(target)`. It will continue to look at the target every frame until you call `camera.look_at(None)`.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()

object_id = c.get_unique_id()
cam = ThirdPersonCamera(avatar_id="a", position={"x": 2, "y": 1.6, "z": -0.6})
c.add_ons.append(cam)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                library="models_core.json",
                                position={"x": 1, "y": 0, "z": -0.5},
                                object_id=object_id)])
# Look at the object.
cam.look_at(object_id)
c.communicate([])
# Look at a position.
cam.look_at({"x": -2, "y": 0.5, "z": 0})
c.communicate([])
c.communicate({"$type": "terminate"})
```

***

**Next: [Follow an object](follow.md)**

[Return to the README](../../../README.md)

***

Command API:

- [`rotate_sensor_container_by`](../../api/command_api.md#rotate_sensor_container_by)
- [`rotate_sensor_container_to`](../../api/command_api.md#rotate_sensor_container_to)
- [`send_image_sensors`](../../api/command_api.md#send_image_sensors)
- [`reset_sensor_container_rotation`](../../api/command_api.md#reset_sensor_container_rotation) 
- [`look_at`](../../api/command_api.md#look_at)
- [`look_at_position`](../../api/command_api.md#look_at_position)

Output Data API:

- [`ImageSensors`](../../api/output_data.md#ImageSensors)

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)
- [`TDWUtils.array_to_vector4(arr)`](../../python/tdw_utils.md) Convert an array to a vector4 dictionary (in this case, a quaternion).

