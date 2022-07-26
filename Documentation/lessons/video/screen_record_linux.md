##### Video Recording

# Video with audio (Linux)

To start video capture, send  [`start_video_capture_linux`](../../api/command_api.md#start_video_capture_linux). 

To stop video capture, send [`stop_video_capture`](../../api/command_api.md#stop_video_capture) or kill the TDW build process by sending [`terminate`](../../api/command_api.md#terminate).

This is a minimal example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
# Add a camera.
camera = ThirdPersonCamera(position={"x": 0, "y": 0.8, "z": 1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
c.add_ons.append(camera)
# Set the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mp4")
print(f"Video will be saved to: {path}")
# Start video capture.
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 60},
               {"$type": "start_video_capture_linux",
                "output_path": str(path.resolve())}])
# Wait 200 frames.
for i in range(200):
    c.communicate([])
# Stop video capture.
c.communicate({"$type": "stop_video_capture"})
# End the simulation.
c.communicate({"$type": "terminate"})
```

## Display and screen

The optional parameters `display` and `screen` are X11 indices; they should match the display and screen that the TDW build is running on. [Read this for more information.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/lessons/setup/install.md)

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
# Add a camera.
camera = ThirdPersonCamera(position={"x": 0, "y": 0.8, "z": 1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
c.add_ons.append(camera)
# Set the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mp4")
print(f"Video will be saved to: {path}")
# Start video capture.
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 60},
               {"$type": "start_video_capture_linux",
                "display": 0,
                "screen": 0,
                "output_path": str(path.resolve())}])
# Wait 200 frames.
for i in range(200):
    c.communicate([])
# Stop video capture.
c.communicate({"$type": "stop_video_capture"})
# End the simulation.
c.communicate({"$type": "terminate"})
```

## Display region capture

On Linux, ffmpeg captures a region of the screen, not a specific window. To define the region, set the `position` parameter.

You may find it easier to set `position` by removing the window title bar from the TDW window application. To do this:

1. [Set `launch_build==False` in your controller.](../core_concepts/launch_build.md)
2. Launch the build with an extra command-line argument: `cd ~/tdw_build/TDW && ./TDW.x86_64 -popupwindow`
3. Launch the controller.

Usually, the TDW build will launch in the center of the monitor. Assuming that you're using a 1080p monitor, that TDW is 256x256, and that you've hidden the title bar, you can set the position like this:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

# Launch the build with -popupwindow
c = Controller(launch_build=False)
# Add a camera.
camera = ThirdPersonCamera(position={"x": 0, "y": 0.8, "z": 1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
c.add_ons.append(camera)
# Set the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mp4")
print(f"Video will be saved to: {path}")
monitor_width = 1920
monitor_height = 1080
screen_width = 256
screen_height = 256
position = {"x": monitor_width // 2 - screen_width // 2,
            "y": monitor_height // 2 - screen_height // 2}
# Start video capture.
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 60},
               {"$type": "set_screen_size",
                "width": screen_width,
                "height": screen_height},
               {"$type": "start_video_capture_linux",
                "output_path": str(path.resolve()),
                "position": position}])
# Wait 200 frames.
for i in range(200):
    c.communicate([])
# Stop video capture.
c.communicate({"$type": "stop_video_capture"})
# End the simulation.
c.communicate({"$type": "terminate"})
```

## Audio capture

By default, audio capture is enabled. Set `audio` to False to disable audio capture:

If `audio` is True, you must set `audio_device`. To get a list of device names:

```bash
pactl list sources | grep output
```

The exact name of the audio device may vary between computers.

You must then [initialize audio in TDW](../audio/initialize_audio.md). You *don't* have to [record audio with fmedia](../audio/record_audio.md); the ffmpeg process launched by `start_video_capture_windows` will automatically record audio.

This minimal example initializes audio, [initializes PyImpact](../audio/py_impact.md), and starts video capture with audio:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
# Add a camera.
camera = ThirdPersonCamera(position={"x": 0, "y": 0.8, "z": 1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
# Initialize audio.
audio_initializer = AudioInitializer(avatar_id="a",
                                     framerate=60)
# Add PyImpact.
py_impact = PyImpact()
c.add_ons.extend([camera, audio_initializer, py_impact])
# Set the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mp4")
print(f"Video will be saved to: {path}")
# Initialize the scene.
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_target_framerate",
             "framerate": 60},
            {"$type": "start_video_capture_linux",
             "output_path": str(path.resolve()),
             "audio_device": "alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"}]
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

## Other parameters

For more information regarding the other optional parameters, read the API documentation for [`start_video_capture_linux`](../../api/command_api.md#start_video_capture_linux).

## Linux server

1. See [install guide](../setup/install.md) for Docker requirements.
2. [Build this container.](https://github.com/threedworld-mit/tdw/blob/master/Docker/Dockerfile_audio)
3. On the server, Make sure that xpra isn't running.
4. In the `tdw` repo, `cd Docker` and `./start_container.sh`
5. Run your controller

***

**This is the last document in the "Video Recording" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [screen_record_linux.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/video/screen_record_linux.py) A minimal example of an audio-visual screen recorder for Linux.

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`PyImpact`](../../python/add_ons/py_impact.md)

Command API:

- [`start_video_capture_linux`](../../api/command_api.md#start_video_capture_linux)
- [`stop_video_capture`](../../api/command_api.md#stop_video_capture)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)