##### Video Recording

# Video with audio (OS X)

To start video capture, send  [`start_video_capture_osx`](../../api/command_api.md#start_video_capture_osx). 

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
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mkv")
print(f"Video will be saved to: {path}")
# Start video capture.
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 60},
               {"$type": "start_video_capture_osx",
                "output_path": str(path.resolve())}])
# Wait 200 frames.
for i in range(200):
    c.communicate([])
# Stop video capture.
c.communica({"$type": "stop_video_capture"})
# End the simulation.
c.communicate({"$type": "terminate"})
```

## Display region capture

On OS X, ffmpeg captures a region of the screen, not a specific window. To define the region, set the `position` parameter.

You may find it easier to set `position` by removing the window title bar from the TDW window application. To do this:

1. [Set `launch_build==False` in your controller.](../core_concepts/launch_build.md)
2. Launch the build with an extra command-line argument: `cd ~/tdw_build/TDW && ./TDW/Contents/MacOS/TDW -popupwindow`
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
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mkv")
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
               {"$type": "start_video_capture_osx",
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
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mkv")
print(f"Video will be saved to: {path}")
# Start video capture.
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 60},
               {"$type": "start_video_capture_osx",
                "output_path": str(path.resolve()),
                "audio": False}])
# Wait 200 frames.
for i in range(200):
    c.communicate([])
# Stop video capture.
c.communicate({"$type": "stop_video_capture"})
# End the simulation.
c.communicate({"$type": "terminate"})
```

If `audio` is True, you must set `audio_device`, the *index* of the audio capture device. To get a list of device names and indices:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

**You might not have a valid audio capture device initially.** [Read this for more information, under "OS X".](../audio/record_audio.md) 

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
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mkv")
print(f"Video will be saved to: {path}")
# Initialize the scene.
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_target_framerate",
             "framerate": 60},
            {"$type": "start_video_capture_osx",
             "output_path": str(path.resolve()),
             "audio_device": 0}]
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

For more information regarding the other optional parameters, read the API documentation for [`start_video_capture_osx`](../../api/command_api.md#start_video_capture_osx).

***

**This is the last document in the "Video Recording" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [screen_record_osx.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/video/screen_record_osx.py) A minimal example of an audio-visual screen recorder for OS X.

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)
- [`AudioInitializer`](../../python/add_ons/audio_initializer.md)
- [`PyImpact`](../../python/add_ons/py_impact.md)

Command API:

- [`start_video_capture_osx`](../../api/command_api.md#start_video_capture_osx)
- [`stop_video_capture`](../../api/command_api.md#stop_video_capture)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)