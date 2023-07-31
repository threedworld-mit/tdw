##### Video Recording

# Video with audio (OS X)

To start video capture, send  [`start_video_capture_osx`](../../api/command_api.md#start_video_capture_osx). 


This is a minimal example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
A minimal example of an audio-visual screen recorder for OS X.
"""

# The target framerate.
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
# This might not be true on your computer! You might need to set `position` manually.
screen_width = 256
screen_height = 256
position = TDWUtils.get_expected_window_position(window_width=screen_width, window_height=screen_height)

# This audio device may be incorrect, or might not exist; see `Documentation/lessons/video/screen_record_osx.md`.
audio_device = 0

# Initialize the scene.
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_screen_size",
             "width": screen_width,
             "height": screen_height},
            {"$type": "start_video_capture_osx",
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

In this example, we've also added [`Clatter`](../clatter/overview.md) to generate impact sounds.

## The `output_path` parameter

The `output_path` parameter of `start_video_capture_osx` is the path to the video file. Usually, this should be a .mp4 file.

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
            {"$type": "start_video_capture_osx",
             "output_path": str(path.resolve()),
             "framerate": 30,
             "audio_device": audio_device}]
```

## The `position` parameter

The `position` parameter of `start_video_capture_osx` sets the top-left corner of the capture region. ffmpeg captures a region of the screen rather than a specific window.

Unfortunately, on OS X, it's difficult to predict where the window will appear. If the window appears in the center of the screen, follow the instructions below for getting its position. If the window appears somewhere else, you will need to set the `position` parameter manually.

Assuming that the window appears in the center of the monitor, call `TDWUtils.get_expected_window_position(window_width, window_height)`.

If you get an error about `screeninfo` not being installed, run `pip3 install screeninfo` and try again.

### Title bar height

There is an optional parameter, `title_bar_height`, which sets the expected height of the window's title bar:

```python
from tdw.tdw_utils import TDWUtils

position = TDWUtils.get_expected_window_position(window_width=256, window_height=256, title_bar_height=25)
```

This parameter defaults to None, in which case `TDWUtils` will set it to a platform-specific value. In the case of OS X, the default value of `title_bar_height` is 25 pixels.

## The `audio_device` parameter

The `audio_device` parameter of `start_video_capture_osx`  is the *index* of the audio capture device (an integer). To get a list of device names and indices:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

**Initially, you might not have a valid audio capture device.** Download [iShowU Audio Capture](https://support.shinywhitebox.com) or [BlackHole](https://github.com/ExistentialAudio/BlackHole) and follow instructions for setting up an audio capture device.

## The `size_scale_factor` and `position_scale_factor` parameters

These parameters will scale the video size and video position by a factor. You will need to set these scale factors if you're using a retina display. The default value of each parameter is 2 (i.e. the actual video size will be twice that of the window size and the position will be multiplied by 2).

## Other parameters

For more information regarding the other optional parameters, read the API documentation for [`start_video_capture_osx`](../../api/command_api.md#start_video_capture_osx).

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
-f avfoundation -i "1:0" -vsync 0 -framerate 60 -filter:v"crop=512:512,1792:956" -c:v h264 -qp 0 -preset ultrafast -y "/Users/user/tdw_example_controller_output/video_capture/video.mp4" [TDWInput.StartVideoCaptureOsx]
```

3. In a terminal, type `ffmpeg` plus the arguments in the Player log:

```bash
ffmpeg -f avfoundation -i "1:0" -vsync 0 -framerate 60 -filter:v"crop=512:512,1792:956" -c:v h264 -qp 0 -preset ultrafast -y "/Users/user/tdw_example_controller_output/video_capture/video.mp4" 
```

4. If the ffmpeg process has an error, read the error carefully and adjust your command's parameters accordingly. An audio-related error, for example, usually means that your `"audio_device"` is wrong. If, on the other hand, there is no error, you can press `q` to quit.

*If you get an error about the framerate:* On some (but not all) machines, you may get an error like this:

```
[avfoundation @ 0x7fe0d2800000] Selected framerate (29.970030) is not supported by the device
```

If you see this error, the framerate you have selected (60 by default) isn't supported on your machine. Set `"framerate": 30` in your command.

## What to do if the video doesn't open

Open the video in VLC. 

If the video file size is very low (e.g. 48 bytes or 0 bytes), there was an error in video capture; see above for how to troubleshoot.

***

**This is the last document in the "Video Recording" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [screen_record_osx.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/video/screen_record_osx.py) A minimal example of an audio-visual screen recorder for OS X.

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`Clatter`](../../python/add_ons/clatter.md)

Command API:

- [`start_video_capture_osx`](../../api/command_api.md#start_video_capture_osx)
- [`stop_video_capture`](../../api/command_api.md#stop_video_capture)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)