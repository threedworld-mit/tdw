##### Video Recording

# Video with Audio (Windows)

To start video capture, send  [`start_video_capture_windows`](../../api/command_api.md#start_video_capture_windows). This is a minimal example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
A minimal example of an audio-visual screen recorder for Windows.
"""

c = Controller()
# Add a camera.
camera = ThirdPersonCamera(position={"x": 0, "y": 0.8, "z": 1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
# Initialize audio.
audio_initializer = AudioInitializer(avatar_id="a")
# Add PyImpact.
py_impact = PyImpact()
c.add_ons.extend([camera, audio_initializer, py_impact])
# Set the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mp4")
print(f"Video will be saved to: {path}")

# Assume that the window will appear in the middle of the screen.
screen_width = 256
screen_height = 256
position = TDWUtils.get_expected_window_position(window_width=screen_width, window_height=screen_height)

# This audio device may be incorrect, or might not exist; see `Documentation/lessons/video/screen_record_windows.md`.
audio_device = "Stereo Mix (Realtek(R) Audio)"

# Initialize the scene.
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_screen_size",
             "width": screen_width,
             "height": screen_height},
            {"$type": "start_video_capture_windows",
             "output_path": str(path.resolve()),
             "position": position,
             "audio_device": audio_device}]
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  position={"x": 0, "y": 1.5, "z": 0},
                                                  object_id=Controller.get_unique_id()))
c.communicate(commands)
# Run the controller.
for i in range(200):
    c.communicate([])
# Stop video capture.
c.communicate({"$type": "stop_video_capture"})
# End the simulation.
c.communicate({"$type": "terminate"})
```

## Initialize audio

Add a  [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md) and an [`AudioInitializer`](../../python/add_ons/audio_initializer.md) to initialize audio. For more information about audio in TDW, [read this](../audio/overview.md). Set the `framerate` parameter of `AudioInitializer` to match the framerate of the video (see below); this will tell the build to send [`set_target_framerate`](../../api/command_api.md#set_target_framerate).

In this example, we've also added [`PyImpact`](../audio/py_impact.md) to generate impact sounds.

## The `output_path` parameter

The `output_path` parameter of `start_video_capture_windows` is the path to the video file. Usually, this should be a .mp4 file.

## The `framerate` parameter

The `framerate` parameter of `start_video_capture_windows` is *optional* and defaults to 60 frames per second.

If you want to set the framerate, make sure that the framerate is set in `AudioInitializer` (this will automatically send the command [`set_target_framerate`](../../api/command_api.md#set_target_framerate)):

```
audio_initializer = AudioInitializer(avatar_id="a", framerate=30)
```

...as well as in the `start_video_capture_windows` command:

```
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_screen_size",
             "width": screen_width,
             "height": screen_height},
            {"$type": "start_video_capture_windows",
             "output_path": str(path.resolve()),
             "framerate": 30,
             "audio_device": audio_device}]
```

## The `position` parameter

The `position` parameter of `start_video_capture_windows` sets the top-left corner of the capture region. ffmpeg captures a region of the screen rather than a specific window.

Usually, the build simulation window will appear in the center of the monitor. To get its expected position, call `TDWUtils.get_expected_window_position(window_width, window_height)`.

If you get an error about `screeninfo` not being installed, run `pip3 install screeninfo` and try again.

*Note: It is technically possible in Windows for ffmpeg to capture a  window rather than a screen region; however, when we tested this, we found that window capture had many problems. In particular, if the video is a .mp4 value, a window capture will be a totally black screen.*

### Title bar height

There is an optional parameter, `title_bar_height`, which sets the expected height of the window's title bar:

```python
from tdw.tdw_utils import TDWUtils

position = TDWUtils.get_expected_window_position(window_width=256, window_height=256, title_bar_height=25)
```

This parameter defaults to None, in which case `TDWUtils` will set it to a platform-specific value. In the case of Windows, the default value of `title_bar_height` is 25 pixels.

### Monitor index

If you have multiple monitors, you may need to set the optional `monitor_index` parameter. To get a list of your monitors and their indices:

```python
import screeninfo

monitors = screeninfo.get_monitors()
for i, monitor in enumerate(monitors):
    print(i, monitor)
```

Then, set `monitor_index` accordingly:

```python
from tdw.tdw_utils import TDWUtils

position = TDWUtils.get_expected_window_position(window_width=256, window_height=256, title_bar_height=25, monitor_index=0)
```

## The `audio_device` parameter

The `audio_device` parameter of `start_video_capture_windows`  is the name of the audio capture device. To get a list of device names:

```bash
ffmpeg -list_devices true -f dshow -i dummy
```

The exact name of the audio device will vary between computers, but they will all begin with `Stereo Mix`. If you don't see an appropriate audio device you will need to adjust your sound settings to enable Stereo Mix; exactly how to do this varies depending on your audio drivers.

## Other parameters

For more information regarding the other optional parameters, read the API documentation for [`start_video_capture_windows`](../../api/command_api.md#start_video_capture_windows).

## Stop video capture

To stop video capture, send [`stop_video_capture`](../../api/command_api.md#stop_video_capture) or kill the TDW build process by sending [`terminate`](../../api/command_api.md#terminate).

## What to do if there is no video

1. Set the optional `log_args` parameter to `True` to log the ffmpeg args. This can allow you to replicate the exact ffmpeg call:

```
{"$type": "start_video_capture_windows",
 "output_path": str(path.resolve()),
 "log_args": True}
```

2. [Check the player log.](https://docs.unity3d.com/Manual/LogFiles.html) It will have a line that looks like this:

```
-audio_buffer_size 5 -f dshow -i audio="Stereo Mix (Realtek(R) Audio)" -c:a aac -ac 2 -f gdigrab -draw_mouse 0 -framerate 60 -offset_x 952 -offset_y 1817 -video_size 256x256 -i desktop -c:v h264 -qp 0 -preset ultrafast -y "C:\Users\user\tdw_example_controller_output\video_capture\video.mp4" [TDWInput.StartVideoCaptureWindows]
```

3. In a terminal, type `ffmpeg` plus the arguments in the Player log:

```bash
ffmpeg -audio_buffer_size 5 -f dshow -i audio="Stereo Mix (Realtek(R) Audio)" -c:a aac -ac 2 -f gdigrab -draw_mouse 0 -framerate 60 -offset_x 952 -offset_y 1817 -video_size 256x256 -i desktop -c:v h264 -qp 0 -preset ultrafast -y "C:\Users\user\tdw_example_controller_output\video_capture\video.mp4" 
```

4. If the ffmpeg process has an error, read the error carefully and adjust your command's parameters accordingly. An audio-related error, for example, usually means that your `"audio_device"` is wrong. If, on the other hand, there is no error, you can press `q` to quit.

## What to do if the video doesn't open

Open the video in VLC. 

If the video file size is very low (e.g. 48 bytes or 0 bytes), there was an error in video capture; see above for how to troubleshoot.

***

**This is the last document in the "Video Recording" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [screen_record_windows.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/video/screen_record_windows.py) A minimal example of an audio-visual screen recorder for Windows.

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`PyImpact`](../../python/add_ons/py_impact.md)

Command API:

- [`start_video_capture_windows`](../../api/command_api.md#start_video_capture_windows)
- [`stop_video_capture`](../../api/command_api.md#stop_video_capture)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)