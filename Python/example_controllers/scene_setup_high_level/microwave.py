from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.proc_gen.arrangements.microwave import Microwave
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.cardinal_direction import CardinalDirection

"""
Create a `Microwave` arrangement.
"""

# Add a `Microwave` arrangement.
microwave = Microwave(position={"x": 0, "y": 0, "z": 0},
                      rng=2,
                      wall=CardinalDirection.west)
microwave_commands = microwave.get_commands()
# The object ID of the microwave is the root ID of the arrangement.
microwave_id = microwave.root_object_id
# Add a camera and enable image capture. Look at the microwave.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("microwave")
print(f"Images will be saved to: {path}")
camera = ThirdPersonCamera(position={"x": 1, "y": 0.8, "z": 0},
                           look_at=microwave_id,
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
# Add a composite object manager, which we'll use to open the microwave door.
composite_object_manager = CompositeObjectManager()
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture, composite_object_manager])
# Create the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
# Add commands to create the arrangement.
commands.extend(microwave_commands)
# Send the commands.
c.communicate(commands)
# Start to open the door.
commands.clear()
for object_id in composite_object_manager.static:
    if object_id == microwave_id:
        for spring_id in composite_object_manager.static[object_id].springs:
            commands.extend([{"$type": "set_spring_force",
                              "spring_force": 50,
                              "id": spring_id},
                             {"$type": "set_spring_target_position",
                              "target_position": 90,
                              "id": spring_id}])
        break
c.communicate(commands)
# Open the door.
for i in range(50):
    c.communicate([])
c.communicate({"$type": "terminate"})
