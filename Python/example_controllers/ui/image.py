from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.ui import UI
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add a UI image.
"""

c = Controller()
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 2.5, "z": 0},
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ui_image")
print(f"Images will be saved to: {path}")
capture = ImageCapture(path=path, avatar_ids=["a"])
ui = UI()
c.add_ons.extend([camera, capture, ui])
c.communicate(TDWUtils.create_empty_room(12, 12))
ui.attach_canvas_to_avatar(avatar_id="a")
ui.add_image(image="test.jpg",
             rgba=False,
             size={"x": 128, "y": 128},
             position={"x": 0, "y": 0})
c.communicate({"$type": "terminate"})
