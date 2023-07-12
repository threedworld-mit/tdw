from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter
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
