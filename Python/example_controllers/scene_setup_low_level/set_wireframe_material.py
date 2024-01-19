from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.librarian import ModelLibrarian
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Set an object's material to wireframe.
"""

c = Controller(launch_build=False)
object_id_1 = c.get_unique_id()
object_id_2 = c.get_unique_id()

model_record_1 = ModelLibrarian().get_record("white_lounger_chair")
model_record_2 = ModelLibrarian().get_record("chair_billiani_doll")
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id_1)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("set_wireframe_material")
print(f"Images will be saved to: {path}")
cap = ImageCapture(avatar_ids=[cam.avatar_id], pass_masks=["_img"], path=path)
c.add_ons.extend([cam, cap])

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name=model_record_1.name,
                             object_id=object_id_1),
            c.get_add_object(model_name=model_record_2.name,
                             object_id=object_id_2,
                             position={"x": 2, "y": 0, "z": 0})]
commands.extend(TDWUtils.set_wireframe_material(substructure=model_record_1.substructure, object_id=object_id_1, color={"r": 1.0, "g": 0, "b": 0, "a": 1.0}, thickness=0.05))
commands.extend(TDWUtils.set_wireframe_material(substructure=model_record_2.substructure, object_id=object_id_2, color={"r": 0, "g": 0, "b": 1.0, "a": 1.0}, thickness=0.035))
c.communicate(commands)
#c.communicate({"$type": "terminate"})
