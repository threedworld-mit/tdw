from typing import List, NamedTuple
from tdw.add_ons.add_on import AddOn
from pathlib import Path
from tdw.backend.paths import VRAY_EXPORT_RESOURCES_PATH
import os
import subprocess


class matrix_data_struct(NamedTuple):
    column_one: list
    column_two: list
    column_three: list
    column_four: list


class VRayExport(AddOn):

    def __init__(self, image_width: int, image_height: int, scene_name: str, , output_path: Union[str, Path]):
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
        self.image_width: int = image_width
        self.image_height: int = image_height
        self.scene_name = scene_name

    def get_initialization_commands(self) -> List[dict]:
        return

    def on_send(self, resp: List[bytes]) -> None:
        return

    def download_model(self, model_name: str):
        """
        Download the zip file of a model from Amazon S3, and unpack the contents into the general "resources" folder.
        :param model_name: The name of the model.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name) + ".zip"
        url = os.path.join(self.S3_ROOT + "vray_models/", model_name) + ".zip"
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

    def fetch_node_ID(self, model_name: str):
        """
        For a given model (name), fetch the Node ID associated with that model.
        :param model_name: The name of the model.
        """
        # TBD

    def write_node_data(self, model_name: str, mat: matrix_data):
        """
        Append the scene position and orientation of a model to its .vrscene file, as Node data.
        NOTE: This could be called once, for a static scene, or every frame if capturing physics motion.
        :param model_name: The name of the model.
        """
        # Fetch node ID from metadata file.
        node_id = fetch_node_id(model_name) 
        # Open model .vrscene file to append node data
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name)  + ".vrscene"
        node_string = "Node " + model_name + "@node_" + node_id + 
                      "{\n" + "transform=Transform(Matrix" + 
                      "(Vector(" + str(matrix_data.column_one) + ")," +
                      "(Vector(" + str(matrix_data.column_two) + ")," +
                      "(Vector(" + str(matrix_data.column_three) + "))," +
                      "(Vector(" + str(matrix_data.column_four) + "));\n}"
        with open(path, "a") as f:  
            f.write(node_string)

    def export_static_node_data(self, model_name_list: List[str]):
        """
        For each model in a list, export the position and orientation data to the model's .vrscene file as Node data.
        This model list could come from the ObjectManager add-on, for example.
        :param model_name_list: The list of model names to write out Node data for.
        """
        for model_name in model_name_list:
            matrix_data = get_matrix_data_from_build(model_name)
            mat_struct = matrix_data_struct(column_one = matrix_data.column_one) #etc
            write_node_data(model_name, mat_struct)
            path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, "models.vrscene")
            with open(path, "w") as f:  
                f.writeln("#include " + model_name + ".vrscene")

    def write_static_camera_view_data(self):
        """
        Export the position and orientation of the camera to its .vrscene file as Node data.
        """	
        #TBD

    def assemble_render_file(self):
        scene_path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        with open(scene_path, "a") as f:  
            f.writeln("#include models.vrscene")
            f.writeln("#include views.vrscene")
            # Append nodes and lights files also, if either one exists
            if os.path.exists("nodes.vrscene"):
                f.writeln("#include views.vrscene")
            if os.path.exists("lights.vrscene"):
                f.writeln("#include lights.vrscene")

    def launch_vantage_render(self):
        """
        Launch Vantage in headless mode and render scene file.
        """
        scene_path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        subprocess.run(["C://Program Files//Chaos Group//Vantage//vantage_console.exe", 
                        "-sceneFile=" + scene_path, 
                        "-outputFile=" + self.output_path,  
                        "-outputWidth=" + self.image_width, 
                        "-outputHeight=" + self.image_height, "-quiet"])

	