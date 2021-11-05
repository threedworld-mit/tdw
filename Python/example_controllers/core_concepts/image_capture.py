from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Example implementation of the ImageCapture add-on.
"""

c = Controller()
object_id = c.get_unique_id()
camera = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                           look_at=object_id,
                           avatar_id="a")
c.add_ons.append(camera)

# Add the ImageCapture add-on.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("image_capture")
print(f"Images will be save to: {path.resolve()}")
capture = ImageCapture(path=path, avatar_ids=["a"], pass_masks=["_img", "_id"])
c.add_ons.append(capture)

# This will create the scene and the object.
# Then, the ThirdPersonCamera add-on will create an avatar.
# Then, the ImageCapture add-on will save an image to disk.
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       position={"x": 1, "y": 0, "z": -0.5},
                                       object_id=object_id)])
c.communicate({"$type": "terminate"})
