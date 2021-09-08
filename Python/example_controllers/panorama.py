from pathlib import Path
from math import radians, sin, cos
from tdw.controller import Controller
from tdw.output_data import Images
from tdw.tdw_utils import TDWUtils


"""
Capture a series of images around a model to form a 360-degree panorama.
"""


class Panorama(Controller):
    def __init__(self):
        # Create the output directory.
        self.output_directory = Path("dist/panorama")
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)

        super().__init__()

    def do_panorama(self, model_name):
        # Create the model.
        object_id = self.add_object(model_name)

        # Teleport the avatar.
        self.communicate({"$type": "teleport_avatar_to",
                          "avatar_id": "a",
                          "position": {"x": 5, "y": 2.5, "z": 0}})

        # Set the starting parameters of the rotation.
        d_theta = 15
        rotations = int(360 / d_theta)
        theta = 0
        x = 3
        y = 2.5
        z = 0
        c_x = 0
        c_z = 0

        # Capture images.
        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        for i in range(rotations):
            # Get the new position.
            rad = radians(theta)
            x_rot = cos(rad) * (x - c_x) - sin(rad) * (z - c_z) + c_x
            z_rot = sin(rad) * (x - c_x) + cos(rad) * (z - c_z) + c_z

            # Teleport the avatar to the next position.
            # Rotate the avatar's camera to look at the object.
            # Receive an image.
            resp = self.communicate([{"$type": "teleport_avatar_to",
                                      "avatar_id": "a",
                                      "position": {"x": x_rot, "y": y, "z": z_rot}},
                                     {"$type": "look_at",
                                      "avatar_id": "a",
                                      "object_id": object_id}
                                     ])
            # Save the images.
            for r in resp[:-1]:
                TDWUtils.save_images(Images(r), str(TDWUtils.zero_padding(i)), str(self.output_directory.resolve()))

            # Increment the angle.
            theta += d_theta

        # Stop image capture.
        # Destroy the target object.
        self.communicate([{"$type": "send_images",
                          "frequency": "never"},
                          {"$type": "destroy_object",
                           "id": object_id}
                          ])

    def run(self):
        # Load the suburb scene_data.
        self.load_streamed_scene(scene="suburb_scene_2018")

        # Create the avatar.
        self.communicate({"$type": "create_avatar",
                          "type": "A_Img_Caps_Kinematic",
                          "id": "a"})

        # Set the pass masks.
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "a",
                          "pass_masks": ["_img"]})

        # Capture panorama images.
        for model_name in ["chair_billiani_doll", "small_table_green_marble"]:
            self.do_panorama(model_name)


if __name__ == "__main__":
    Panorama().run()
