from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

camera = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                           avatar_id="a",
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("image_capture")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)

c = Controller()
c.add_ons.extend([camera, capture])
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name="iron_box",
                                         position={"x": 0, "y": 0, "z": 0},
                                         object_id=object_id))
c.communicate(commands)
c.communicate({"$type": "terminate"})
