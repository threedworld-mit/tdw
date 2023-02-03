from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of an animated non-physics humanoid.
"""

# Add a camera and enable image capture.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": -5.5, "y": 5, "z": -2},
                           look_at={"x": 0, "y": 1.0, "z": -1})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("humanoid_minimal")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
# Create a scene and add a humanoid.
humanoid_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(36, 36),
            c.get_add_humanoid(humanoid_name="man_suit",
                               object_id=humanoid_id,
                               position={'x': 0, 'y': 0, 'z': -1})]
# Add an animation.
animation_name = "walking_1"
animation_command, animation_record = c.get_add_humanoid_animation(humanoid_animation_name=animation_name)
num_frames = animation_record.get_num_frames()
commands.extend([animation_command,
                 {"$type": "play_humanoid_animation",
                  "name": animation_name,
                  "id": humanoid_id}])
# Set the framerate.
commands.append({"$type": "set_target_framerate",
                 "framerate": animation_record.framerate})
# Send the commands.
c.communicate(commands)
# Play some loops.
for i in range(2):
    # Play the animation.
    for j in range(num_frames):
        c.communicate([])
    # Start the next loop.
    c.communicate({"$type": "play_humanoid_animation",
                   "name": animation_name,
                   "id": humanoid_id})
c.communicate({"$type": "terminate"})
