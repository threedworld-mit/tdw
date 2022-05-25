from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.proc_gen.arrangements.kitchen_counter import KitchenCounter
from tdw.proc_gen.arrangements.cabinetry.cabinetry import CABINETRY
from tdw.proc_gen.arrangements.cabinetry.cabinetry_type import CabinetryType
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.ordinal_direction import OrdinalDirection
from tdw.cardinal_direction import CardinalDirection
from tdw.librarian import SceneLibrarian

"""
Create a kitchen counter arrangement.
"""

# Get the scene name, record, and the region where the kitchen counter will be added.
scene_name = "mm_craftroom_2a"
scene_record = SceneLibrarian().get_record("mm_craftroom_2a")
region = scene_record.rooms[0].main_region
# Generate a kitchen counter.
kitchen_counter = KitchenCounter(cabinetry=CABINETRY[CabinetryType.beech_honey],
                                 corner=OrdinalDirection.northeast,
                                 wall=CardinalDirection.north,
                                 distance=0,
                                 region=region,
                                 rng=3)
# Add a camera and enable image capture.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("kitchen_counter")
print(f"Images will be saved to: {path}")
# Look at the root object (the kitchen counter).
camera = ThirdPersonCamera(position={"x": 0, "y": 1.8, "z": 0},
                           look_at=kitchen_counter.root_object_id,
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
# Start the controller.
c = Controller()
# Append the add-ons.
c.add_ons = [camera, capture]
# Add the scene.
commands = [Controller.get_add_scene(scene_name=scene_name)]
# Add the kitchen counter's commands.
commands.extend(kitchen_counter.get_commands())
c.communicate(commands)
c.communicate({"$type": "terminate"})
