##### Video Recording

# Video with audio (Linux)

To start video capture, send  [`start_video_capture_linux`](../../api/command_api.md#start_video_capture_linux). This is a minimal example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
A minimal example of an audio-visual screen recorder for Linux.
"""

c = Controller()
# Add a camera.
camera = ThirdPersonCamera(position={"x": 0, "y": 0.8, "z": 1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
# Initialize audio.
audio_initializer = AudioInitializer(avatar_id="a")
# Add Clatter.
clatter = Clatter()
c.add_ons.extend([camera, audio_initializer, clatter])
# Set the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mp4")
print(f"Video will be saved to: {path}")

# Assume that the window will appear in the middle of the screen.
screen_width = 256
screen_height = 256
position = TDWUtils.get_expected_window_position(window_width=screen_width, window_height=screen_height)

# Initialize the scene.
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_screen_size",
             "width": screen_width,
             "height": screen_height},
            {"$type": "start_video_capture_linux",
             "output_path": str(path.resolve()),
             "position": position}]
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

In this example, we've also added [`Clatter`](../clatter/overview.md) to generate impact sounds.

## The `output_path` parameter

The `output_path` parameter of `start_video_capture_linux` is the path to the video file. Usually, this should be a .mp4 file.

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
            {"$type": "start_video_capture_linux",
             "output_path": str(path.resolve()),
             "framerate": 30,
             "audio_device": audio_device}]
```

## The `display` and `screen` parameters

The `display` and `screen` parameters of  `start_video_capture_linux` are *optional*  and set X11 indices. By default, both indices are 0. These parameters should match the display and screen that the TDW build is running on:

```
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_screen_size",
             "width": screen_width,
             "height": screen_height},
            {"$type": "start_video_capture_linux",
             "output_path": str(path.resolve()),
             "display": 1,
             "screen": 0,
             "position": position}]
```

To get a list of displays and screens, run `xrandr`.

 [Read this for more information.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/lessons/setup/install.md)

## The `position` parameter

The `position` parameter of `start_video_capture_linux` sets the top-left corner of the capture region. ffmpeg captures a region of the screen rather than a specific window.

Usually, the build simulation window will appear in the center of the monitor. To get its expected position, call `TDWUtils.get_expected_window_position(window_width, window_height)`.

If you get an error about `screeninfo` not being installed, run `pip3 install screeninfo` and try again.

### Title bar height

There is an optional parameter, `title_bar_height`, which sets the expected height of the window's title bar:

```python
from tdw.tdw_utils import TDWUtils

position = TDWUtils.get_expected_window_position(window_width=256, window_height=256, title_bar_height=48)
```

This parameter defaults to None, in which case `TDWUtils` will set it to a platform-specific value. In the case of Linux, this can vary quite a bit, but in Ubuntu 20 the default title bar height is 48 pixels.

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

position = TDWUtils.get_expected_window_position(window_width=256, window_height=256, title_bar_height=48, monitor_index=0)
```

## The `audio_device` parameter

The `audio_device` parameter of `start_video_capture_linux` is *optional* and is the name of the audio capture device. 

By default, the capture device is `"alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"`, which is correct for most Ubuntu installs:

```
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_screen_size",
             "width": screen_width,
             "height": screen_height},
            {"$type": "start_video_capture_linux",
             "output_path": str(path.resolve()),
             "position": position,
             "audio_device": "alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"}]
```

To get a list of device names:

```bash
pactl list sources | grep output
```

## Other parameters

For more information regarding the other optional parameters, read the API documentation for [`start_video_capture_linux`](../../api/command_api.md#start_video_capture_linux).

## Stop video capture

To stop video capture, send [`stop_video_capture`](../../api/command_api.md#stop_video_capture) or kill the TDW build process by sending [`terminate`](../../api/command_api.md#terminate).

## What to do if there is no video

1. Set the optional `log_args` parameter to `True` to log the ffmpeg args. This can allow you to replicate the exact ffmpeg call:

```
{"$type": "start_video_capture_osx",
 "output_path": str(path.resolve()),
 "log_args": True}
```

2. [Check the player log.](https://docs.unity3d.com/Manual/LogFiles.html) It will have a line that looks like this:

```
-f pulse -i alsa_output.pci-0000_00_1f.3.analog-stereo.monitor -c:a aac -ac 2 -video_size 256x256 -framerate 60 -f x11grab -i :0.0+952,1840 -c:v h264 -qp 0 -preset ultrafast -y "/home/user/tdw_example_controller_output/video_capture/video.mp4" [TDWInput.StartVideoCaptureLinux]
```

3. In a terminal, type `ffmpeg` plus the arguments in the Player log:

```bash
ffmpeg -f pulse -i alsa_output.pci-0000_00_1f.3.analog-stereo.monitor -c:a aac -ac 2 -video_size 256x256 -framerate 60 -f x11grab -i :0.0+952,1840 -c:v h264 -qp 0 -preset ultrafast -y "/home/user/tdw_example_controller_output/video_capture/video.mp4" 
```

4. If the ffmpeg process has an error, read the error carefully and adjust your command's parameters accordingly. An error regarding displays, for example, usually means that your `display` or `screen` paramter is wrong. If, on the other hand, there is no error, you can press `q` to quit.

## What to do if the video doesn't open

Open the video in VLC. 

If the video file size is very low (e.g. 48 bytes or 0 bytes), there was an error in video capture; see above for how to troubleshoot.

***

**This is the last document in the "Video Recording" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [screen_record_linux.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/video/screen_record_linux.py) A minimal example of an audio-visual screen recorder for Linux.

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`Clatter`](../../python/add_ons/clatter.md)

Command API:

- [`start_video_capture_linux`](../../api/command_api.md#start_video_capture_linux)
- [`stop_video_capture`](../../api/command_api.md#stop_video_capture)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)