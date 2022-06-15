from typing import List, Dict, NamedTuple, Union
from tdw.add_ons.add_on import AddOn
from pathlib import Path
from tdw.output_data import OutputData, TransformMatrices, SegmentationColors
from requests import get
import os
import re
import zipfile
import subprocess
import numpy as np


class matrix_data_struct(NamedTuple):
    column_one: str
    column_two: str
    column_three: str
    column_four: str


class VRayExport(AddOn):

    def __init__(self, image_width: int, image_height: int, scene_name: str, output_path: Union[str, Path]):
        super().__init__()
        if isinstance(output_path, str):
            """:field
            The path to the output directory.
            """
            self.output_path: Path = Path(output_path)
        else:
            self.output_path: Path = output_path
        if not self.output_path.exists():
            self.output_path.mkdir(parents=True)
        self.S3_ROOT = "https://tdw-public.s3.amazonaws.com/"
        self.VRAY_EXPORT_RESOURCES_PATH = Path.home().joinpath("vray_export_resources")
        if not self.VRAY_EXPORT_RESOURCES_PATH.exists():
            self.VRAY_EXPORT_RESOURCES_PATH.mkdir(parents=True)
        self.image_width: int = image_width
        self.image_height: int = image_height
        self.scene_name = scene_name
        # Conversion matrix from left-hand to right-hand.
        self.handedness = np.array([[1, 0, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 1, 0, 0],
                                    [0, 0, 0, 1]])
        # Dictionary of model names by ID
        self.object_names: Dict[int, str] = dict()


    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "send_transform_matrices",
                       "frequency": "always"},
                    {"$type": "send_segmentation_colors",
                       "frequency": "once"},
                    {"$type": "send_camera_matrices",
                       "frequency": "always"}]
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get segmentation color output data.
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    # Cache the object names and ID
                    object_id = segm.get_object_id(j)
                    object_name = segm.get_object_name(j)
                    self.object_names[object_id] = object_name

    def download_model(self, model_name: str):
        """
        Download the zip file of a model from Amazon S3, and unpack the contents into the general "resources" folder.
        :param model_name: The name of the model.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name.lower()) + ".zip"
        url = os.path.join(self.S3_ROOT + "vray_models/", model_name.lower()) + ".zip"
        with open(path, "wb") as f:
            f.write(get(url).content)
        # Unzip in place.
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.VRAY_EXPORT_RESOURCES_PATH)
        # Delete the zip file.
        os.remove(path)

    def download_scene(self):
        """
        Download the zip file of a streamed scene from Amazon S3, and unpack the contents into the general "resources" folder.
        :param model_name: The name of the scene.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".zip"
        url = os.path.join(self.S3_ROOT + "vray_scenes/", self.scene_name) + ".zip"
        with open(path, "wb") as f:
            f.write(get(url).content)
        # Unzip in place.
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.VRAY_EXPORT_RESOURCES_PATH)
        # Delete the zip file.
        os.remove(path)

    def fetch_node_id_string(self, model_name: str) -> str:
        """
        For a given model (name), fetch the Node ID associated with that model.
        :param model_name: The name of the model.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name)  + ".vrscene"
        with open(path, "r") as filename:  
            # Look for Node structure and output node ID.
            src_str = model_name + "@node_"
            pattern = re.compile(src_str, re.IGNORECASE)
            for line in filename:
                if pattern.search(line):
                    return line


    def write_node_data(self, model_name: str, mat: matrix_data_struct):
        """
        Append the scene position and orientation of a model to its .vrscene file, as Node data.
        NOTE: This could be called once, for a static scene, or every frame if capturing physics motion.
        :param model_name: The name of the model.
        """
        # Fetch node ID from metadata file.
        node_id_string = self.fetch_node_id_string(model_name) 
        # Open model .vrscene file to append node data
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name)  + ".vrscene"
        node_string = (node_id_string + 
                      "transform=Transform(Matrix" + 
                      "(Vector(" + mat.column_one + "), " +
                      "Vector(" + mat.column_two + "), " +
                      "Vector(" + mat.column_three + ")), " +
                      "Vector(" + mat.column_four + "));\n}")
        with open(path, "a") as f:  
            f.write(node_string)

    def export_static_node_data(self, resp: List[bytes]):
        """
        For each model in the scene, export the position and orientation data to the model's .vrscene file as Node data.
        Then append an #include reference to the model file at the end of the main scene file.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        with open(path, "a") as f: 
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "trma":
                    transform_matrices = TransformMatrices(resp[i])
                    # Iterate through the objects.
                    for j in range(transform_matrices.get_num()):
                        # Get the object ID.
                        object_id = transform_matrices.get_id(j)
                        # Get the matrix and convert it.
                        # Equivalent to: handedness * object_matrix * handedness.
                        matrix = np.matmul(self.handedness, np.matmul(transform_matrices.get_matrix(j), self.handedness))
                        # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
                        # We also need to negate the X and Y value, to complete the handedness conversion.
                        pos_x = -(matrix[3][0] * 100)
                        pos_y = -(matrix[3][1] * 100)
                        pos_z = matrix[3][2] * 100
                        mat_struct = matrix_data_struct(column_one = str(matrix[0][0]) + "," + str(matrix[0][1]) + "," + str(matrix[0][2]), 
                                                        column_two = str(matrix[1][0]) + "," + str(matrix[1][1]) + "," + str(matrix[1][2]), 
                                                        column_three = str(matrix[2][0]) + "," + str(matrix[2][1]) + "," + str(matrix[2][2]),  
                                                        column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
                        # Get the model name for this ID
                        model_name = self.object_names[object_id]
                        self.write_node_data(model_name, mat_struct)
                        f.write("#include \"" + model_name + ".vrscene\"\n")

    def write_static_camera_view_data(self):
        """
        Export the position and orientation of the camera to its .vrscene file as Node data.
        """	
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        with open(path, "a") as f: 
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "cama":
                    camera_matrices = CameraMatrices(resp[i])
                    # Iterate through the cameras.
                    for j in range(camera_matrices.get_num()):
                        # Get the avatar ID.
                        avatar_id = camera_matrices.get_avatar_id(j)
                        # Get the matrix and convert it.
                        # Equivalent to: handedness * object_matrix * handedness.
                        matrix = np.matmul(self.handedness, np.matmul(camera_matrices.get_camera_matrix(j), self.handedness))
                        # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
                        # We also need to negate the X and Y value, to complete the handedness conversion.
                        pos_x = -(matrix[3][0] * 100)
                        pos_y = -(matrix[3][1] * 100)
                        pos_z = matrix[3][2] * 100
                        mat_struct = matrix_data_struct(column_one = str(matrix[0][0]) + "," + str(matrix[0][1]) + "," + str(matrix[0][2]), 
                                                        column_two = str(matrix[1][0]) + "," + str(matrix[1][1]) + "," + str(matrix[1][2]), 
                                                        column_three = str(matrix[2][0]) + "," + str(matrix[2][1]) + "," + str(matrix[2][2]),  
                                                        column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
                        print(str(matrix_data_struct.column_one + "\n"), 
                              str(matrix_data_struct.column_two + "\n"), 
                              str(matrix_data_struct.column_three + "\n"), 
                              str(matrix_data_struct.column_four + "\n"))
        #self.write_renderview_data(mat_struct)

    def assemble_render_file(self):
        scene_path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        with open(scene_path, "a") as f:  
            #f.write("#include models.vrscene\n")
            #f.write("#include views.vrscene\n")
            # Append nodes and lights files also, if either one exists
            if os.path.exists("nodes.vrscene"):
                f.write("#include nodes.vrscene\n")
            if os.path.exists("lights.vrscene"):
                f.write("#include lights.vrscene\n")

    def launch_vantage_render(self):
        """
        Launch Vantage in headless mode and render scene file.
        """
        scene_path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        subprocess.run(["C://Program Files//Chaos Group//Vantage//vantage_console.exe", 
                        "-sceneFile=" + scene_path, 
                        "-outputFile=" + self.output_path,  
                        "-outputWidth=" + self.image_width, 
                        "-outputHeight=" + self.image_height,
                        "-quiet"])

	