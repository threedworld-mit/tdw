from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a scene, add an object, and save the image.
"""

c = Controller()
object_id = c.get_unique_id()

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 0, "z": 0},
                             object_id=object_id)]
commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 1.6, "z": -0.6},
                                       avatar_id="a",
                                       look_at={"x": 0, "y": 0, "z": 0}))
commands.extend([{"$type": "set_pass_masks",
                  "pass_masks": ["_img"],
                  "avatar_id": "a"},
                 {"$type": "send_images",
                  "frequency": "always",
                  "ids": ["a"]}])

resp = c.communicate(commands)
output_directory = str(EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("send_images").resolve())
print(f"Images will be saved to: {output_directory}")

for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    # Get Images output data.
    if r_id == "imag":
        images = Images(resp[i])
        # Determine which avatar captured the image.
        if images.get_avatar_id() == "a":
            # Iterate throught each capture pass.
            for j in range(images.get_num_passes()):
                # This is the _img pass.
                if images.get_pass_mask(j) == "_img":
                    image_arr = images.get_image(j)
                    # Get a PIL image.
                    pil_image = TDWUtils.get_pil_image(images=images, index=j)
            # Save the image.
            TDWUtils.save_images(images=images, filename="0", output_directory=output_directory)
c.communicate({"$type": "terminate"})
