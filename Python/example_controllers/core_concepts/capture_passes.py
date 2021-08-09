import json
from typing import List, Dict
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, SegmentationColors, CameraMatrices
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class CapturePasses(Controller):
    """
    Generate a series of images using each capture pass.

    Additionally:

    - Log the segmentation colors and IDs of each object in the scene.
    - Save point cloud data per frame (generated from the _depth pass).

    """

    def __init__(self, port: int = 1071, launch_build: bool = True):
        super().__init__(port=port, launch_build=launch_build)
        # Set the output directory.
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("capture_passes")
        print(f"Data will be saved to: {self.path.resolve()}")
        # Set the third-person camera. This won't do anything until we call run().
        self.camera: ThirdPersonCamera = ThirdPersonCamera(position={"x": 2.478, "y": 1.602, "z": 1.412},
                                                           look_at={"x": 0, "y": 0.2, "z": 0},
                                                           avatar_id="a")
        # Enable per-frame image capture. This won't do anything until we call run().
        self.capture: ImageCapture = ImageCapture(path=self.path,
                                                  avatar_ids=["a"],
                                                  pass_masks=["_img", "_id", "_mask", "_category", "_depth",
                                                              "_depth_simple", "_normals", "_albedo", "_flow"])
        # Get the segmentation colors per object.
        self.segmentation_colors: Dict[str, tuple] = dict()

    def run(self) -> None:
        """
        Create a scene. Apply a force to one of the objects.
        Per frame, capture images, point cloud data, and segmentation color data.
        """

        # Set the IDs and names of the objects.
        object_id_0 = self.get_unique_id()
        object_id_1 = self.get_unique_id()
        object_id_2 = self.get_unique_id()
        object_id_3 = self.get_unique_id()
        object_names: Dict[int, str] = {object_id_0: "small_table_green_marble",
                                        object_id_1: "rh10",
                                        object_id_2: "jug01",
                                        object_id_3: "jug05"}
        self.start()

        # Append the add-ons.
        self.add_ons.extend([self.camera, self.capture])

        # Create the scene. Add the objects. Request SegmentationColors for this frame and CameraMatrices for every frame.
        # Apply a force to one of the objects.
        # Send the commands and receive output data.
        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_object(object_names[object_id_0],
                                                     object_id=object_id_0),
                                 self.get_add_object(object_names[object_id_1],
                                                     position={"x": 0.7, "y": 0, "z": 0.4},
                                                     rotation={"x": 0, "y": 30, "z": 0},
                                                     object_id=object_id_1),
                                 self.get_add_object(model_name=object_names[object_id_2],
                                                     position={"x": -0.3, "y": 0.9, "z": 0.2},
                                                     object_id=object_id_2),
                                 self.get_add_object(object_names[object_id_3],
                                                     position={"x": 0.3, "y": 0.9, "z": -0.2},
                                                     object_id=object_id_3),
                                 {"$type": "send_segmentation_colors",
                                  "frequency": "once"},
                                 {"$type": "send_camera_matrices",
                                  "frequency": "always"},
                                 {"$type": "apply_force_to_object",
                                  "id": object_id_1,
                                  "force": {"x": -5, "y": 5, "z": -200}}])

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get all objects in the frame.
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    object_id = segm.get_object_id(j)
                    object_name = object_names[object_id]
                    object_color = segm.get_object_color(j)
                    self.segmentation_colors[object_name] = object_color
        # Save the segmentation color data.
        self.path.joinpath("segmentation_colors.json").write_text(json.dumps(self.segmentation_colors))
        # Save point cloud data.
        self.save_point_cloud(resp=resp)

        # Advance ten more frames. Save out image and point cloud data.
        for i in range(10):
            resp = self.communicate([])
            self.save_point_cloud(resp=resp)

        # End the simulation.
        self.communicate({"$type": "terminate"})

    def save_point_cloud(self, resp: List[bytes]) -> None:
        """
        Get the _depth pass and convert it to a point cloud. Save the point cloud to disk.

        :param resp: The response from the build.
        """

        # Get the camera matrix output data.
        camera_matrices = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "cama":
                camera_matrices = CameraMatrices(resp[i]).get_camera_matrix()
        # Get the image data for this avatar.
        images = self.capture.images["a"]
        for i in range(images.get_num_passes()):
            # Save a point cloud.
            if images.get_pass_mask(i) == "_depth":
                # Get the filepath.
                filepath = self.path.joinpath(f"point_cloud_{self.capture.frame}.txt")
                # Convert the _depth pass to depth values.
                depth_values = TDWUtils.get_depth_values(images.get_image(i), depth_pass="_depth",
                                                         width=images.get_width(), height=images.get_height())
                # Convert the depth values to point cloud data and save it to disk.
                TDWUtils.get_point_cloud(depth=depth_values, camera_matrix=camera_matrices, filename=str(filepath.resolve()))


if __name__ == "__main__":
    c = CapturePasses()
    c.run()
