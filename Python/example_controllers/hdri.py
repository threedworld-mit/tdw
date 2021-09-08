import os
import shutil
from time import sleep
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images


"""
Create an object and avatar and capture images of the scene, rotating the HDRI skybox by 15 degrees
for each image.
"""


class HDRI(Controller):
    def run(self):
        # Create the output directory.
        output_directory = "example_output"
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
            sleep(0.5)
            os.mkdir(output_directory)

        self.start()
        # Load a streamed scene. This scene covers a relatively small area, and is optimized for use with HDRI maps.
        self.load_streamed_scene(scene="building_site")

        # Add the object.
        lamp_id = self.add_object("alma_floor_lamp", position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 90, "z": 0})

        # Create the avatar.
        self.communicate({"$type": "create_avatar", "type": "A_Img_Caps_Kinematic", "id": "a"})

        # Change the skybox.
        self.communicate(self.get_add_hdri_skybox("bergen_4k"))

        # Teleport the avatar to a suitable position.
        # Set the pass masks to _img.
        # Enable image capture.
        self.communicate([{"$type": "teleport_avatar_to",
                           "avatar_id": "a",
                           "position": {"x": -4.28, "y": 0.85, "z": 4.27}},
                          {"$type": "set_pass_masks",
                           "avatar_id": "a",
                           "pass_masks": ["_img"]},
                          {"$type": "send_images",
                           "frequency": "always"},
                          ])

        # Create the recommended post-processing setup for HDRI.
        self.communicate([{"$type": "set_post_exposure", "post_exposure": 0.6},
                          {"$type": "set_contrast", "contrast": -20},
                          {"$type": "set_saturation", "saturation": 10},
                          {"$type": "set_screen_space_reflections", "enabled": False},
                          {"$type": "set_vignette", "enabled": False}])

        # Set the shadow strength to maximum.
        self.communicate({"$type": "set_shadow_strength", "strength": 1.0})

        # Capture 48 images.
        for i in range(48):
            # Look at the lamp.
            resp = self.communicate({"$type": "look_at",
                                     "avatar_id": "a",
                                     "object_id": lamp_id,
                                     "use_centroid": True})
            # Rotate the skybox by 15 degrees.
            self.communicate({"$type": "rotate_hdri_skybox_by", "angle": 15})
            images = Images(resp[0])
            # Save the image.
            TDWUtils.save_images(images, TDWUtils.zero_padding(i), output_directory=output_directory)


if __name__ == "__main__":
    HDRI().run()
