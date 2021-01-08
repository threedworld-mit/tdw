from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images, CameraMatrices, Raycast, AvatarKinematic


"""
Capture a _depth image and calculate the depth values of each pixel.
"""


class DepthShader(Controller):
    def run(self):
        self.start()

        depth_pass = "_depth"

        # Create an empty room.
        # Set the screen size.
        commands = [TDWUtils.create_empty_room(12, 12),
                    {"$type": "set_screen_size",
                     "width": 512,
                     "height": 512}]
        # Add the avatar.
        commands.extend(TDWUtils.create_avatar(position={"x": 1.57, "y": 3, "z": 3.56}, look_at=TDWUtils.VECTOR3_ZERO))
        # Add an object.
        # Request images and camera matrices.
        # Get a raycast from at the center of the camera viewport.
        # Request avatar data to get the avatar position (you'll need this if the avatar is moving).
        commands.extend([self.get_add_object("trunck", object_id=0),
                         {"$type": "set_pass_masks",
                          "pass_masks": [depth_pass]},
                         {"$type": "send_images"},
                         {"$type": "send_camera_matrices"},
                         {"$type": "send_viewport_raycast"},
                         {"$type": "send_avatars"}])
        resp = self.communicate(commands)

        depth_image = None
        camera_matrix = None
        images = None
        raycast = None
        avatar = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the image.
            if r_id == "imag":
                images = Images(resp[i])
                for j in range(images.get_num_passes()):
                    if images.get_pass_mask(j) == depth_pass:
                        depth_image = images.get_image(j)
            # Get the camera matrix.
            elif r_id == "cama":
                camera_matrix = CameraMatrices(resp[i]).get_camera_matrix()
            # Get the raycast.
            elif r_id == "rayc":
                raycast = Raycast(resp[i])
            elif r_id == "avki":
                avatar = AvatarKinematic(resp[i])
        # Save the image.
        TDWUtils.save_images(images=images, output_directory="D:/depth_shader", filename="0", append_pass=True)
        # Get the depth values of each pixel.
        depth = TDWUtils.get_depth_values(image=depth_image, width=images.get_width(),  height=images.get_height())

        # Un-normalize the depth values by getting the distance from the avatar to the raycast point.
        avatar_position = np.array(avatar.get_position())
        raycast_point = np.array(raycast.get_point())
        distance_to_raycast_point = np.linalg.norm(avatar_position - raycast_point)
        unnormalized = distance_to_raycast_point / depth[int(images.get_height() / 2)][int(images.get_width() / 2)]
        depth *= unnormalized
        print(depth)

        # Get a point cloud and write it to disk.
        point_cloud_filename = "point_cloud.txt"
        print(f"Point cloud saved to: {Path(point_cloud_filename)}")
        TDWUtils.get_point_cloud(depth=depth, filename=point_cloud_filename, camera_matrix=camera_matrix)
        # Show the depth values.
        plt.imshow(depth)
        plt.show()
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    DepthShader(launch_build=False).run()
