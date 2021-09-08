from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images

"""
Rotate the directional light in the scene_data.
"""

output_directory = str(Path.home().joinpath("tdw_example_controller_output/directional_light"))
print(f"Images will be saved to {output_directory}")

c = Controller(launch_build=False)

# Load the scene_data. Set the screen size.
commands = [c.get_add_scene(scene_name="tdw_room"),
            {"$type": "set_screen_size",
             "width": 1280,
             "height": 720}]
# Add an avatar.
commands.extend(TDWUtils.create_avatar(position={"x": -2, "y": 0.9, "z": -1},
                                       look_at=TDWUtils.VECTOR3_ZERO))
# Enable image capture.
# Disable anti-aliasing.
# Disabling anti-aliasing isn't required for rotating directional lights but if we don't,
# the first and last rendered images will be slightly different, making this example harder to understand.
commands.extend([{"$type": "set_pass_masks",
                  "pass_masks": ["_img"]},
                 {"$type": "set_anti_aliasing",
                  "mode": "none"},
                 {"$type": "send_images",
                  "frequency": "always"}])
resp = c.communicate(commands)
TDWUtils.save_images(filename="0_default", output_directory=output_directory, images=Images(resp[0]))

# Rotate the light.
resp = c.communicate({"$type": "rotate_directional_light_by",
                      "angle": 70,
                      "axis": "pitch"})
TDWUtils.save_images(filename="1_rotated", output_directory=output_directory, images=Images(resp[0]))

# Reset the light.
resp = c.communicate({"$type": "reset_directional_light_rotation"})
TDWUtils.save_images(filename="2_reset", output_directory=output_directory, images=Images(resp[0]))

c.communicate({"$type": "terminate"})
