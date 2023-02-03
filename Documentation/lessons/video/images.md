##### Video Recording

# Image-only video

The simplest way to record video in TDW is to capture image data per-frame, save it to disk, and convert the images to a video using [ffmpeg](https://www.ffmpeg.org/).

## 1. Capture image data

This example controller will:

1. Add a [third-person camera](../core_concepts/avatars.md)
2. Enable [image capture](../core_concepts/images.md)
3. Add an [object](../core_concepts/objects.md)
4. Set the target framerate to 30 or 60 frames per second
5. Let the object fall (images will be saved each frame)

```python
from os import chdir
from subprocess import call
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
camera = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
c.add_ons.append(camera)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("image_only_video")
print(f"Images will be save to: {path.resolve()}")
capture = ImageCapture(path=path, avatar_ids=["a"])
c.add_ons.append(capture)
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 60},
               c.get_add_object(model_name="iron_box",
                                position={"x": 1, "y": 3, "z": -0.5},
                                object_id=c.get_unique_id())])
for i in range(100):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

## 2. Convert image data to a video file

1. `cd ~/tdw_example_controller_output/image_only_video`
2.  `ffmpeg -i img_%04d.jpg -vcodec libx264 -pix_fmt yuv420p image_only_video.mp4`

If you saved png files instead of jpg files, replace `img_%04d.jpg` with `img_%04d.png`

***

**Next: [Video with audio](audio.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [image_only_video.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/video/image_only_video.py) Capture image data and automatically call ffmpeg to convert it to a video.

Command API:

- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)