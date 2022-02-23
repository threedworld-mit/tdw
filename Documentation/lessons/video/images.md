##### Video Recording

# Image-only video

## Option A: Capture images and convert them to a video

The simplest way to record video in TDW is to capture image data per-frame, save it to disk, and convert the images to a video using [ffmpeg](https://www.ffmpeg.org/).

### 1. Capture image data

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

### 2. Convert image data to a video file

1. `cd ~/tdw_example_controller_output/image_only_video`
2.  `ffmpeg -i img_%04d.jpg -vcodec libx264 -pix_fmt yuv420p image_only_video.mp4`

If you saved png files instead of jpg files, replace `img_%04d.jpg` with `img_%04d.png`

If you're using Windows and get an error, make sure that ffmpeg is in your [path environment variable](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/).

## Option B: Record using ffmpeg

It's possible to record directly with ffmpeg, though this requires a little more setup.

### Linux

If you're using a Linux server, you can record the screen using [x11grab](https://trac.ffmpeg.org/wiki/Capture/Desktop). 

- Make sure that xpra isn't running.
- Use **x11grab** (run this outside of a Docker container):

```bash
DISPLAY=:0 ffmpeg -video_size 256x256 -f x11grab -i :0.0+0,0 output.mp4
```

- `DISPLAY` must have a valid display number.
- `-video_size` must be the display size.
- The TDW screen size must be less than or equal to the display size.
- `:0.0+0,0` is the display number (which should match `DISPLAY`) and `+(x,y)` pixel offset. You can get the coordinates of the window with:

```bash
xwininfo -tree -root
```

### Windows:

```bash
ffmpeg -f dshow -i video="screen-capture-recorder" output.mp4
```

### OS X:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

## Option C:  Record with OBS

[OBS](https://obsproject.com) is an excellent screen recorder for personal computers. Unfortunately, it has very limited command line options. If you want to automatically generate many videos, you should use Option A. (TDW image capture) or Option B. (ffmpeg). OBS is best used for one-shot videos, especially if you want to fine-tune the input/output settings.

***

**Next: [Video with audio](audio.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [image_only_video.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/video/image_only_video.py) Capture image data and automatically call ffmpeg to convert it to a video.

Command API:

- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)