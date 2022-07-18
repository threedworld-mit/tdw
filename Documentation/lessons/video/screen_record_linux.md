# Video with audio (Linux)

Start video capture with  [`start_video_capture_linux`](../../api/command_api.md#start_video_capture_linux). This is a minimal example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("video_capture").joinpath("video.mkv")
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





