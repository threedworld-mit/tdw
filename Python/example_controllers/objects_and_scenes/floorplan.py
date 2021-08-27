from tdw.floorplan_controller import FloorplanController
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Generate a floorplan scene and populate it with a layout of objects.
"""

c = FloorplanController()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("floorplan_controller")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], pass_masks=["_img"], path=path)
c.add_ons.append(capture)
# Get commands to load the scene and populate it with objects.
commands = c.get_scene_init_commands(scene="1a", layout=0, audio=True)
commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 40, "z": 0},
                                       look_at={"x": 0, "y": 0, "z": 0},
                                       avatar_id="a"))
# Make the image 720p and hide the roof.
commands.extend([{"$type": "set_screen_size",
                  "width": 1280,
                  "height": 720},
                 {"$type": "set_floorplan_roof",
                 "show": False}])
c.communicate(commands)
c.communicate({"$type": "terminate"})
