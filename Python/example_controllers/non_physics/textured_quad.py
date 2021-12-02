from base64 import b64encode
from PIL import Image
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add a textured quad to the scene.
"""

input_image_path = "DT4897.jpg"
# Open the image and encode it to base 64.
with open(input_image_path, "rb") as f:
    image = b64encode(f.read()).decode("utf-8")
# Get the image size.
size = Image.open(input_image_path).size
quad_position = {"x": 1, "y": 2, "z": 3}
# Add a camera and enable image capture.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": 8, "z": -3},
                           look_at=quad_position)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("textured_quad")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
quad_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(8, 8),
               {"$type": "create_textured_quad",
                "position": quad_position,
                "size": {"x": 5, "y": 3},
                "euler_angles": {"x": 0, "y": 30, "z": 0},
                "id": quad_id},
               {"$type": "set_textured_quad",
                "id": quad_id,
                "dimensions": {"x": size[0], "y": size[1]},
                "image": image}])
c.communicate({"$type": "terminate"})
