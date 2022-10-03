from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.librarian import ModelLibrarian
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Set an object's visual material.
"""

c = Controller()
object_id = c.get_unique_id()

model_record = ModelLibrarian().get_record("white_lounger_chair")
material_name = "parquet_long_horizontal_clean"
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("set_visual_material")
print(f"Images will be saved to: {path}")
cap = ImageCapture(avatar_ids=[cam.avatar_id], pass_masks=["_img"], path=path)
c.add_ons.extend([cam, cap])

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name=model_record.name,
                             object_id=object_id),
            c.get_add_material(material_name=material_name)]
commands.extend(TDWUtils.set_visual_material(c=c, substructure=model_record.substructure, material=material_name, object_id=object_id))
c.communicate(commands)
c.communicate({"$type": "terminate"})
