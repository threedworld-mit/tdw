from tdw.controller import Controller
from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of the proc-gen kitchen.
"""

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("proc_gen_kitchen_minimal")
print(f"Images will be saved to: {path}")
proc_gen_kitchen = ProcGenKitchen()
proc_gen_kitchen.create()
camera = ThirdPersonCamera(position={"x": 2, "y": 1.8, "z": -0.5},
                           look_at={"x": 0, "y": 0.6, "z": 0},
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
c = Controller()
c.add_ons.extend([proc_gen_kitchen, camera, capture])
c.communicate([])
c.communicate({"$type": "terminate"})
