import os
import shutil
from time import sleep
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images


"""
Create a few objects, and avatar, and capture images of the objects.
"""


class ObjectsAndImages(Controller):
    def run(self):
        # Create the output directory.
        output_directory = "example_output"
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
            sleep(0.5)
            os.mkdir(output_directory)

        self.start()
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Add the objects.
        lamp_id = self.add_object("alma_floor_lamp",
                                  position={"x": 1, "y": 0, "z": 0},
                                  rotation={"x": 0, "y": 90, "z": 0})
        self.add_object("live_edge_coffee_table",
                        position={"x": 1.5, "y": 0, "z": 1.5},
                        rotation={"x": 0, "y": 30, "z": 0})
        self.add_object("small_table_green_marble",
                        position={"x": -0.9, "y": 0, "z": -1.35})

        # Create the avatar.
        self.communicate({"$type": "create_avatar",
                          "type": "A_Img_Caps_Kinematic",
                          "id": "a"})

        # Try to find a valid position on the NavMesh.
        x, y, z = TDWUtils.get_random_position_on_nav_mesh(self, 12, 12)

        # Teleport the avatar to the valid position.
        # Apply a force to the lamp.
        # Set the pass masks to _img.
        # Enable image capture.
        self.communicate([{"$type": "teleport_avatar_to",
                           "avatar_id": "a",
                           "position": {"x": x, "y": 1.5, "z": z}},
                          {"$type": "apply_force_to_object",
                           "force": {"x": 2, "y": 1, "z": 0},
                           "id": lamp_id},
                          {"$type": "set_pass_masks",
                           "avatar_id": "a",
                           "pass_masks": ["_img", "_id"]},
                          {"$type": "send_images",
                           "frequency": "always"},
                          ])

        # Capture 100 images.
        for i in range(100):
            # Look at the lamp.
            resp = self.communicate({"$type": "look_at",
                                     "avatar_id": "a",
                                     "object_id": lamp_id,
                                     "use_centroid": True})
            images = Images(resp[0])
            # Save the image.
            TDWUtils.save_images(images, TDWUtils.zero_padding(i), output_directory=output_directory)


if __name__ == "__main__":
    ObjectsAndImages().run()
