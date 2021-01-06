from pathlib import Path
import matplotlib.pyplot as plt
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images, CameraMatrices


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
        commands.extend(TDWUtils.create_avatar(position={"x": 1.57, "y": 3, "z": 3.56},
                                               look_at=TDWUtils.VECTOR3_ZERO))
        # Add an object.
        # Request images and camera matrices.
        commands.extend([self.get_add_object("trunck", object_id=0),
                         {"$type": "set_pass_masks",
                          "pass_masks": ["_img", depth_pass]},
                         {"$type": "send_images"},
                         {"$type": "send_camera_matrices"}])
        resp = self.communicate(commands)

        depth_image = None
        camera_matrix = None
        images = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the image.
            if r_id == "imag":
                images = Images(resp[i])
                for j in range(images.get_num_passes()):
                    if images.get_pass_mask(j) == "_depth":
                        depth_image = images.get_image(j)
            # Get the camera matrix.
            elif r_id == "cama":
                camera_matrix = CameraMatrices(resp[i]).get_camera_matrix()
        # Save the image.
        TDWUtils.save_images(images=images, output_directory="D:/depth_shader", filename="0", append_pass=True)
        # Get the depth values of each pixel.
        depth = TDWUtils.get_depth_values(image=depth_image,
                                          width=images.get_width(),
                                          height=images.get_height(),
                                          uv_starts_at_top=images.get_uv_starts_at_top())
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
