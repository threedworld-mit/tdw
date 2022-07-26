from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact
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
