from pathlib import Path
import matplotlib.pyplot as plt
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images, SystemInfo, CameraMatrices


"""
Capture a _depth image and calculate the depth values of each pixel.
"""


class DepthShader(Controller):
    def run(self):
        self.start()

        depth_pass = "_depth"

        # Create an empty room.
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Add the avatar.
        commands.extend(TDWUtils.create_avatar(position={"x": 1.57, "y": 3, "z": 3.56},
                                               look_at=TDWUtils.VECTOR3_ZERO))
        # Add an object.
        # Request images, system info, and camera matrices.
        # You only need to request system info once.
        commands.extend([self.get_add_object("trunck", object_id=0),
                         {"$type": "set_pass_masks",
                          "pass_masks": ["_img", depth_pass]},
                         {"$type": "send_images"},
                         {"$type": "send_system_info"},
                         {"$type": "send_camera_matrices"}])
        resp = self.communicate(commands)

        depth_image = None
        system_info = None
        camera_matrix = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the image.
            if r_id == "imag":
                images = Images(resp[i])
                for j in range(images.get_num_passes()):
                    if images.get_pass_mask(j) == "_depth":
                        depth_image = images.get_image(j)
            # Get the system info.
            elif r_id == "sysi":
                system_info = SystemInfo(resp[i])
            # Get the camera matrix.
            elif r_id == "cama":
                camera_matrix = CameraMatrices(resp[i]).get_camera_matrix()
        # Get the depth values of each pixel.
        depth = TDWUtils.get_depth_values(image=depth_image,
                                          width=system_info.get_width(),
                                          height=system_info.get_height(),
                                          uv_starts_on_top=system_info.get_uv_starts_at_top())
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
