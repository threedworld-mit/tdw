from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add a compass rose to the scene.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": 3, "y": 3.6, "z": -1},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("compass_rose")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], pass_masks=["_img"], path=path)
c.add_ons.extend([camera, capture])
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_screen_size",
                "width": 512,
                "height": 512},
               c.get_add_object(model_name="rh10",
                                position={"x": 0, "y": 0, "z": 0},
                                rotation={"x": 0, "y": 25, "z": 0},
                                object_id=c.get_unique_id()),
               {"$type": "add_compass_rose"}])
c.communicate({"$type": "terminate"})
