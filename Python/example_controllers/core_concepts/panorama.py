from math import radians, sin, cos
from tdw.controller import Controller
from tdw.output_data import OutputData, Images
from tdw.tdw_utils import TDWUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class Panorama(Controller):
    """
    Capture a series of images around a model to form a 360-degree panorama.
    """

    def __init__(self, port: int = 1071, launch_build: bool = True):
        self.output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("panorama")
        print(f"Images will be saved to: {self.output_directory.resolve()}")

        super().__init__(port=port, launch_build=launch_build)

    def do_panorama(self, model_name: str) -> None:
        """
        Create panorama images of a single object.

        :param model_name: The name of the object model.
        """

        object_id = self.get_unique_id()
        # Create the model, teleport the avatar, and look at the object. Enable jpgs. Request images per frame.
        self.communicate([self.get_add_object(model_name=model_name, object_id=object_id),
                          {"$type": "teleport_avatar_to",
                           "avatar_id": "a",
                           "position": {"x": 5, "y": 2.5, "z": 0}},
                          {"$type": "look_at",
                           "avatar_id": "a",
                           "object_id": object_id},
                          {"$type": "set_img_pass_encoding",
                           "value": False},
                          {"$type": "send_images",
                           "frequency": "always"}])

        # Set the starting parameters of the rotation.
        d_theta = 15
        rotations = int(360 / d_theta)
        theta = 0
        x = 3
        y = 2.5
        z = 0
        c_x = 0
        c_z = 0

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
                                      "object_id": object_id}])
            # Save the images.
            for j in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[j])
                if r_id == "imag":
                    TDWUtils.save_images(Images(resp[j]), str(TDWUtils.zero_padding(i)), str(self.output_directory.resolve()))

            # Increment the angle.
            theta += d_theta

        # Stop image capture.
        # Destroy the target object.
        self.communicate([{"$type": "send_images",
                          "frequency": "never"},
                          {"$type": "destroy_object",
                           "id": object_id}])

    def run(self):
        # Add a scene, create an avatar, and set the pass masks.
        self.communicate([self.get_add_scene(scene_name="suburb_scene_2018"),
                          {"$type": "create_avatar",
                           "type": "A_Img_Caps_Kinematic",
                           "id": "a"},
                          {"$type": "set_pass_masks",
                           "avatar_id": "a",
                           "pass_masks": ["_img"]}])
        # Capture panorama images.
        for model_name in ["chair_billiani_doll", "small_table_green_marble"]:
            self.do_panorama(model_name)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    Panorama().run()
