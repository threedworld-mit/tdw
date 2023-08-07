from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Set an object's velocity.
"""

c = Controller()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("set_velocity")
print(f"Images will be saved to: {path}")
camera = ThirdPersonCamera(position={"x": 0.5, "y": 1.1, "z": -4},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([camera, capture])
commands = [TDWUtils.create_empty_room(12, 12)]
object_id = Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="chair_billiani_doll",
                                                  object_id=object_id,
                                                  position={"x": 0, "y": 1, "z": 0}))
# Set the object's velocity.
commands.append({"$type": "set_velocity",
                 "id": object_id,
                 "velocity": {"x": 2, "y": 0.5, "z": 0}})
c.communicate(commands)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
