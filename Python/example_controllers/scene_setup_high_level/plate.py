from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.proc_gen.arrangements.plate import Plate
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a `Plate` arrangement.
"""

# Add a `Plate` arrangement.
plate = Plate(position={"x": 0, "y": 0, "z": 0},
              rng=0)
plate_commands = plate.get_commands()
# The object ID of the plate is the root ID of the arrangement.
plate_id = plate.root_object_id
# Add a camera and enable image capture. Look at the plate.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("plate")
print(f"Images will be saved to: {path}")
camera = ThirdPersonCamera(position={"x": 0.5, "y": 0.2, "z": 0},
                           look_at=plate_id,
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
# Create the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
# Add commands to create the arrangement.
commands.extend(plate_commands)
# Send the commands.
c.communicate(commands)
c.communicate({"$type": "terminate"})
