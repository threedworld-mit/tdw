##### Scene Setup (High-Level APIs)

# Scripted object placement (floorplan layouts)

TDW includes a number of predefined **"floorplan layouts"**. These are interior scenes with multiple rooms. Each scene has several "variants" which are purely cosmetic (such as changing what the floors look like) and three "layouts". Each layout is a list of objects and their positions, masses, and so on.

To access the floorplan layouts, use a [`Floorplan`](../../python/add_ons/floorplan.md) add-on. The following example will load a scene and populate it with a layout. This controller also sends [`set_floorplan_roof`](../../api/command_api.md#set_floorplan_roof) to hide the roof of the house so that we can see the interior:

```python
from tdw.controller import Controller
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.floorplan import Floorplan
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Generate a floorplan scene and populate it with a layout of objects.
"""

c = Controller()

# Initialize the floorplan add-on.
floorplan = Floorplan()
# Scene 1, visual variant a, object layout 0.
floorplan.init_scene(scene="1a", layout=0)

# Add a camera and enable image capture.
camera = ThirdPersonCamera(position={"x": 0, "y": 40, "z": 0},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("floorplan_controller")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], pass_masks=["_img"], path=path)

c.add_ons.extend([floorplan, camera, capture])
# Initialize the scene.
c.communicate([])
# Make the image 720p and hide the roof.
c.communicate([{"$type": "set_screen_size",
                "width": 1280,
                "height": 720},
               {"$type": "set_floorplan_roof",
                "show": False}])
c.communicate({"$type": "terminate"})
```

Result:

![](images/floorplan.jpg)

## Valid scene+layout combinations

In the `scene` parameter, the number (1, 2, 4, or 5) defines the geometry of the house and the letter (a, b, or c) defines the visual variant of that house . The `layout` parameter sets which list of objects to load.

| `scene` | `layout` |
| --- | --- |
| 1a, 1b, or 1c | 0, 1, or 2 |
| 2a, 2b, or 2c | 0, 1, or 2 |
| 4a, 4b, or 4c | 0, 1, or 2 |
| 5a, 5b, or 5c | 0, 1, or 2 |

## Images of every scene+layout combination

[**Images of every scene+layout combination can be found here.**](https://github.com/threedworld-mit/tdw/blob/master/Documentation/lessons/scene_setup_high_level/images/floorplans) 

***

**Next: [Reset a scene](reset_scene.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [floorplan.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/scene_setup_high_level/floorplan.py) Initialize a floorplan scene and populate it with objects.

Python API:

-  [`Floorplan`](../../python/add_ons/floorplan.md)

Command API:

- [`set_screen_size`](../../api/command_api.md#set_screen_size)
- [`set_floorplan_roof`](../../api/command_api.md#set_floorplan_roof)

