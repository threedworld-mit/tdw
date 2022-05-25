from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.proc_gen.arrangements.cup_and_coaster import CupAndCoaster
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a cup and coaster.
"""

# Add a camera and enable image capture.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("cup_and_coaster")
print(f"Images will be saved to: {path}")
camera = ThirdPersonCamera(position={"x": -1.5, "y": 0.8, "z": 0},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
# Add a `CupAndCoaster` arrangement.
cup_and_coaster = CupAndCoaster(position={"x": 0, "y": 0, "z": 0},
                                rng=0)
# Create the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
# Add commands to create the cup and coaster.
commands.extend(cup_and_coaster.get_commands())
# Send the commands.
c.communicate(commands)
c.communicate({"$type": "terminate"})
