from pathlib import Path
from typing import List, Dict, Union
import re
import zipfile
import subprocess
from shutil import copyfile
from requests import get
import numpy as np
import boto3
from fabric import Connection
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.version import __version__
from tdw.output_data import OutputData, TransformMatrices, SegmentationColors, AvatarTransformMatrices, FieldOfView
from tdw.vray_data.vray_matrix import VRayMatrix, get_converted_node_matrix, get_converted_camera_matrix


class VRayExporter(AddOn):
    """
    (TODO)
    """

    """:class_var
    The S3 URL root.
    """
    S3_ROOT: str = "https://tdw-public.s3.amazonaws.com/"
    """:class_var
    The path to location of all downloaded and exported .vrscene files, maps etc.
    """
    VRAY_EXPORT_RESOURCES_PATH: Path = Path.home().joinpath("vray_export_resources")
    if not VRAY_EXPORT_RESOURCES_PATH.exists():
        VRAY_EXPORT_RESOURCES_PATH.mkdir(parents=True)

    def __init__(self, image_width: int, image_height: int, scene_name: str, output_directory: Union[str, Path],
                 animate: bool = False, render_host: str = "localhost"):
        super().__init__()
        self.render_host: str = render_host
        self.output_directory: Path = TDWUtils.get_path(output_directory)
        if (self.render_host == "localhost") and (not self.output_directory.exists()):
            self.output_directory.mkdir(parents=True)
        self.image_width: int = image_width
        self.image_height: int = image_height
        self.animate: bool = animate
        self.scene_name: str = scene_name
        self._scene_local_source_path: Path = VRayExporter.VRAY_EXPORT_RESOURCES_PATH.joinpath(f"{self.scene_name}.vrscene")
        self._scene_local_working_path: Path = VRayExporter.VRAY_EXPORT_RESOURCES_PATH.joinpath(f"{self.scene_name}_copy.vrscene")
        self._render_view_str: str = ""
        """:field
        The list of each model that can be rendered with VRay. The first time you run this add-on, it will query the S3 server for a list of models and save the result to `~/vray_export_resources/models.txt`, which it will use for all subsequent runs.
        """
        self.vray_model_list = self._get_vray_models()
        # Dictionary of model names by ID
        self.object_names: Dict[int, str] = dict()
        # Dictionary of model IDs by name
        self.model_ids: Dict[str, int] = dict()
        # Dictionary of node IDs by model name
        self.node_ids: Dict[str, str] = dict()
        # The current frame count.
        self.frame_count: int = 0
        self._downloaded_data: bool = False

    def launch_renderer(self) -> None:
        """
        Launch Vantage in headless mode and render scene file, updating for animation if necessary.
        """

        # Open the master scene file.
        output_path = str(self.output_directory.joinpath(f"{self.scene_name}.png").resolve())
        scene_path = str(self._scene_local_working_path)
        if self.frame_count > 0:
            # Write out to the master scene file the animation settings, including final frame_count, as the end of the animation sequence.
            self._export_animation_settings()
            # Launch vantage in appropriate mode.
            if self.render_host == "localhost":
                subprocess.run(["C:/Program Files/Chaos Group/Vantage/vantage_console.exe",
                                "-sceneFile=" + scene_path,
                                "-outputFile=" + output_path,
                                "-outputWidth=" + str(self.image_width),
                                "-outputHeight=" + str(self.image_height),
                                "-frames=0" + "-" + str(self.frame_count),
                                "-quiet",
                                "-autoClose=true"])
            else:
                # Rendering on a remote machine.
                arglist = "-sceneFile=" + scene_path + " " \
                          + "-outputFile=" + output_path + " " \
                          + "-outputWidth=" + str(self.image_width) + " " \
                          + "-outputHeight=" + str(self.image_height) + " " \
                          + "-frames=0" + "-" + str(self.frame_count) + " " \
                          + "-quiet" + " " \
                          + "-autoClose=true"
                with Connection(host=self.render_host, port=1071) as c:
                    c.run("cd C:/Program Files/Chaos Group/Vantage & " + "\"./vantage_console.exe\"" + arglist)
        else:
            if self.render_host == "localhost":
                print(output_path)
                subprocess.run(["C:/Program Files/Chaos Group/Vantage/vantage_console.exe",
                                "-sceneFile=" + scene_path,
                                "-outputFile=" + output_path,
                                "-outputWidth=" + str(self.image_width),
                                "-outputHeight=" + str(self.image_height),
                                "-quiet",
                                "-autoClose=true"])
            else:
                arglist = "-sceneFile=" + scene_path + " " \
                          + "-outputFile=" + output_path + " " \
                          + "-outputWidth=" + str(self.image_width) + " " \
                          + "-outputHeight=" + str(self.image_height) + " " \
                          + "-quiet" + " " \
                          + "-autoClose=true"
                with Connection(host=self.render_host, port=1071) as c:
                    c.run("cd C:/Program Files/Chaos Group/Vantage & " + "\"./vantage_console.exe\"" + arglist)

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "set_screen_size",
                     "width": self.image_width,
                     "height": self.image_height},
                    {"$type": "send_transform_matrices",
                     "frequency": "always"},
                    {"$type": "send_segmentation_colors",
                     "frequency": "once"},
                    {"$type": "send_camera_matrices",
                     "frequency": "always"},
                    {"$type": "send_avatar_transform_matrices",
                     "frequency": "always"},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_field_of_view",
                     "frequency": "always"}]
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Download the scene file and model files if we have not done so already.
        if not self._downloaded_data:
            self._downloaded_data = True
            self._get_objects(resp=resp)
            # Download and unzip scene file -- this will be the "master" file, that all model .vrscene files will be appended to.
            self._download_scene()
            # Download and unzip all object models in the scene.
            for model_name in self.object_names.values():
                self._download_model(model_name)
            # Update model files to reflect initial scene object transforms.
            self._export_model_node_data(resp=resp)
            # Update V-Ray camera to reflect TDW camera position and orientation.
            self._export_static_camera_view_data(resp=resp)
        # Process object or camera movement.
        if self.animate:
            self._export_animation(resp=resp)

    @staticmethod
    def _get_vray_models() -> List[str]:
        """
        :return: A list of VRay models.
        """

        vray_models_path = VRayExporter.VRAY_EXPORT_RESOURCES_PATH.joinpath("models.txt")
        version_path = VRayExporter.VRAY_EXPORT_RESOURCES_PATH.joinpath("version.txt")
        # Use an existing list.
        if vray_models_path.exists() and version_path.exists() and version_path.read_text() == __version__:
            return vray_models_path.read_text(encoding="utf-8").split("\n")
        # Generate the list.
        else:
            models: List[str] = list()
            s3 = boto3.resource('s3')
            bucket = s3.Bucket('tdw-public')
            for obj in bucket.objects.filter(Prefix='vray_models/'):
                models.append(obj.key.replace("vray_models/", "").replace(".zip", ""))
            # Write the list.
            vray_models_path.write_text("\n".join(models), encoding="utf-8")
            version_path.write_text(__version__)
            return models

    def _get_objects(self, resp: List[bytes]) -> None:
        """
        Rebuild `self.object_names` and `self.model_ids`.

        :param resp: The response from the build.
        """

        self.object_names.clear()
        self.model_ids.clear()
        # Rebuild the object list.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get segmentation color output data.
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    # Cache the object names and IDs.
                    object_id = segm.get_object_id(j)
                    object_name = segm.get_object_name(j).lower()
                    # Make sure we have a vray model for this object.
                    if object_name in self.vray_model_list:
                        self.object_names[object_id] = object_name
                        self.model_ids[object_name] = object_id
                    else:
                        raise Exception("Model " + object_name + " does not have a V-Ray-ready equivalent; cannot continue processing scene.")

    def _download_model(self, model_name: str):
        """
        Download the zip file of a model from Amazon S3, and unpack the contents into the VRAY_EXPORT_RESOURCES_PATH folder. Delete the zip file. Get the node ID.

        :param model_name: The name of the model.
        """

        path = VRayExporter.VRAY_EXPORT_RESOURCES_PATH.joinpath(f"{model_name}.vrscene")
        if not path.exists():
            self._download(f"vray_models/{model_name}")
        self.node_ids[model_name] = re.search(r"(Node (.*?)@node_(.*?){)", path.read_text(encoding="utf8"),
                                              flags=re.MULTILINE).group(1)

    def _download_scene(self) -> None:
        """
        Download the zip file of a streamed scene from Amazon S3, and unpack the contents into the general "resources" folder.
        """

        # Download the scene.
        if not self._scene_local_source_path.exists():
            self._download(f"vray_scenes/{self.scene_name}")
        # Delete an existing local copy.
        if self._scene_local_working_path.exists():
            self._scene_local_working_path.unlink()
        # Copy the scene file.
        copyfile(src=str(self._scene_local_source_path), dst=str(self._scene_local_working_path))
        text = self._scene_local_working_path.read_text(encoding="utf-8")
        self._render_view_str = re.search(r"(RenderView(.*))", text, flags=re.MULTILINE).group(1)

    def _download(self, s3_suffix: str) -> None:
        name = s3_suffix.split("/")[1]
        zip_path = VRayExporter.VRAY_EXPORT_RESOURCES_PATH.joinpath(f"{name}.zip")
        url = self.S3_ROOT + s3_suffix + ".zip"
        # Download.
        zip_path.write_bytes(get(url).content)
        # Unzip.
        with zipfile.ZipFile(str(zip_path), 'r') as zip_ref:
            zip_ref.extractall(self.VRAY_EXPORT_RESOURCES_PATH)
        # Delete the zip file.
        zip_path.unlink()
    
    def _export_model_node_data(self, resp: List[bytes]) -> None:
        """
        For each model in the scene, update the position and orientation data in the model's .vrscene file as Node data.

        Then append an #include reference to the model file at the end of the main scene file.

        :param resp: The response from the build.
        """

        with open(str(self._scene_local_working_path), "at") as f:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "trma":
                    transform_matrices = TransformMatrices(resp[i])
                    # Iterate through the objects.
                    for j in range(transform_matrices.get_num()):
                        # Get the object ID.
                        object_id = transform_matrices.get_id(j)
                        # Get the converted matrix.
                        matrix: VRayMatrix = get_converted_node_matrix(transform_matrices.get_matrix(j))
                        # Get the model name for this ID
                        model_name = self.object_names[object_id]
                        self._write_static_node_data(model_name, matrix)
                        f.write("#include \"" + model_name + ".vrscene\"\n\n")

    @staticmethod
    def _write_static_node_data(model_name: str, matrix: VRayMatrix) -> None:
        """
        Replace the Node transform in a model's .vrscene file to match the object's position and orientation in the TDW scene.

        :param model_name: The model name.
        :param matrix: The `VRayMatrix` data.
        """

        # Generate the node string.
        node_string = ("transform=Transform(Matrix" +
                       "(Vector(" + matrix.column_one + "), " +
                       "Vector(" + matrix.column_two + "), " +
                       "Vector(" + matrix.column_three + ")), " +
                       "Vector(" + matrix.column_four + "));")
        # Open model .vrscene file to append node data.
        path = VRayExporter.VRAY_EXPORT_RESOURCES_PATH.joinpath(f"{model_name}.vrscene").resolve()
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"^\s+transform=(.*?);", f"  transform={node_string}", text, flags=re.MULTILINE)
        path.write_text(text, encoding="utf-8")

    def _get_dynamic_node_data_string(self, matrix: np.ndarray, model_name: str, frame_count: int) -> str:
        """
        For each model in the scene, compute the position and orientation data for one frame, as Node data.

        Return a per-frame interpolated Node data string of the form:

        ```
        Node Box102@node_9701 {
          transform=interpolate(
          (2, Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(-152.2906646728516, -145.2715454101563, 0)))
          );
        }
        ```

        For each frame in the object's motion, we will output one of these strings that interpolates from the previous frame to the new frame's transform matrix values.

        :param matrix: The matrix.
        :param model_name: The model name.
        :param frame_count: The frame count.

        :return: A node data string.
        """

        m: VRayMatrix = get_converted_node_matrix(matrix)
        # Get node ID from cached dictionary
        node_id_string = self.node_ids[model_name]
        # Form interpolation string.
        node_string = ("\n" + node_id_string +
                       "transform=interpolate(\n" +
                       "(" + str(frame_count) + ", " +
                       "Transform(Matrix" +
                       "(Vector(" + m.column_one + "), " +
                       "Vector(" + m.column_two + "), " +
                       "Vector(" + m.column_three + ")), " +
                       "Vector(" + m.column_four + ")))\n" +
                       ");\n}\n")
        return node_string

    def _export_static_camera_view_data(self, resp: List[bytes]) -> None:
        """
        Output the position and orientation of the camera to the scene .vrscene file as Transform data.

        :param resp: The response from the build.
        """

        focal_length: float = 0
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "fofv":
                focal_length = FieldOfView(resp[i]).get_focal_length()
                break
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "atrm":
                avatar_transform_matrices = AvatarTransformMatrices(resp[i])
                for j in range(avatar_transform_matrices.get_num()):
                    avatar_matrix = avatar_transform_matrices.get_avatar_matrix(j)
                    sensor_matrix = avatar_transform_matrices.get_sensor_matrix(j)
                    matrix: VRayMatrix = get_converted_camera_matrix(avatar_matrix, sensor_matrix)
                    self._write_camera_parameters(matrix, focal_length)
                    return

    def _get_dynamic_camera_data_string(self, avatar_matrix, sensor_matrix, frame_count: int) -> str:
        """
        Compute the position and orientation of the moving camera for one frame, as Node data.
        Return a per-frame interpolated Node data string of the form:

        ```
        Node Box102@node_9701 {
          transform=interpolate(
          (2, Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(-152.2906646728516, -145.2715454101563, 0)))
          );
        }
        ```

        For each frame in the camera's motion, we will output one of these strings that interpolates from the previous frame to the new frame's transform matrix values.

        :param avatar_matrix: The avatar transform matrix.
        :param sensor_matrix: The sensor container transform matrix.
        :param frame_count: The frame count.

        :return: The node string.
        """

        matrix: VRayMatrix = get_converted_camera_matrix(avatar_matrix, sensor_matrix)
        # Form interpolation string.
        node_string = ("\n" + self._render_view_str +
                       "\ntransform=interpolate(\n" +
                       "(" + str(frame_count) + ", " +
                       "Transform(Matrix" +
                       "(Vector(" + matrix.column_one + "), " +
                       "Vector(" + matrix.column_two + "), " +
                       "Vector(" + matrix.column_three + ")), " +
                       "Vector(" + matrix.column_four + ")))\n" +
                       ");\n}\n")
        return node_string

    def _write_camera_parameters(self, matrix: VRayMatrix, focal_length: float) -> None:
        """
        Replace the camera transform line in the scene file with the converted TDW camera pos/ori data.
        Replace the physical camera focal length line in the scene file with the TDW focal length.

        :param matrix: The camera transform matrix.
        :param focal_length: The camera focal length.
        """

        # Create the node string.
        node_string = ("transform=Transform(Matrix" +
                       "(Vector(" + matrix.column_one + "), " +
                       "Vector(" + matrix.column_two + "), " +
                       "Vector(" + matrix.column_three + ")), " +
                       "Vector(" + matrix.column_four + "));")
        # Open the file.
        text = self._scene_local_working_path.read_text(encoding="utf-8")
        # Replace the node string.
        text = re.sub(r"RenderView (.*)((.|\n)*?)\s+transform=(.*?);", r"RenderView \1\n\n  transform=" + node_string, text, flags=re.MULTILINE)
        # Replace the focal length.
        text = re.sub(r"((CameraPhysical (.*?)@node(.*){)((.|\n)*?))focal_length=(.*?);", r"\1focal_length=" + str(focal_length) + ";", text, flags=re.MULTILINE)
        # Save the file.
        self._scene_local_working_path.write_text(text, encoding="utf-8")
  
    def _export_animation_settings(self) -> None:
        """
        Write out the output settings with the end frame of any animation in the scene.
        """

        with open(str(self._scene_local_working_path), "a") as f:
            out_string = ("SettingsOutput output_settings {\n" +
                          "img_width=" + str(self.image_width) + ";\n" +
                          "img_height=" + str(self.image_height) + ";\n" +
                          "img_pixelAspect=1;\n" +
                          "img_file_needFrameNumber=1;\n" +
                          "img_clearMode=0;\n" +
                          "anim_start=0;\n" +
                          "anim_end=" + str(self.frame_count) + ";\n" +
                          "frame_start=0;\n" +
                          "frames_per_second=1;\n" +
                          "frames=List(\n" +
                          "List(0, " + str(self.frame_count) + ")\n" +
                          ");\n" +
                          "}\n")
            f.write(out_string)

    def _export_animation(self, resp: List[bytes]) -> None:
        """
        Open the master scene file, so we can output the dynamic data for any moving objects and/or a moving camera.
        """

        with open(str(self._scene_local_working_path), "a") as f:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "atrm":
                    avatar_transform_matrices = AvatarTransformMatrices(resp[i])
                    for j in range(avatar_transform_matrices.get_num()):
                        avatar_matrix = avatar_transform_matrices.get_avatar_matrix(j)
                        sensor_matrix = avatar_transform_matrices.get_sensor_matrix(j)
                        # Convert matrices to V-Ray format and output to master scene file as frame-by-frame interpolations.
                        node_data_string = self._get_dynamic_camera_data_string(avatar_matrix, sensor_matrix, self.frame_count)
                        f.write(node_data_string)
                if r_id == "trma":
                    transform_matrices = TransformMatrices(resp[i])
                    # Iterate through the objects.
                    for j in range(transform_matrices.get_num()):
                        # Get the object ID.
                        object_id = transform_matrices.get_id(j)
                        mat = transform_matrices.get_matrix(j)
                        node_data_string = self._get_dynamic_node_data_string(mat, self.object_names[object_id], self.frame_count)
                        f.write(node_data_string)
            self.frame_count += 1
